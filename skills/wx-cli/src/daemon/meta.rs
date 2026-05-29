//! Freshness metadata appended to every q_* response.
//!
//! 背景：`all_keys.json` 是 `wx init` 时的快照。WeChat 在 daemon 启动后随时可能创建
//! 新的 `message_N.db` 分片；如果只信任 init 时收到的 `msg_db_keys` 列表，新分片里
//! 的数据对 daemon 完全不可见 → 调用方拿到的是看似正常但缺数据的结果（"stale"）。
//!
//! 本模块的职责：
//! 1. 提供 `Meta` 结构体，由各 `q_*` 函数填充后塞进 response（顶层 `meta` 字段）。
//! 2. 提供 `discover_unknown_shards(db_dir, msg_db_keys)`：扫描磁盘上当前真实存在的
//!    `message/message_*.db` 文件，diff 出 daemon 未持有 enc_key 的"未知分片"列表。
//! 3. 集中 `MetaStatus` 的判定规则，避免 8 个 q_* 各自判，规则漂移。

use serde::Serialize;
use std::collections::HashMap;
use std::path::Path;

/// 每条 q_* 响应附带的"新鲜度元数据"。
///
/// 序列化为 JSON 时，所有 `Option` 字段在 `None` 时省略，让最常见的命令调用
/// 输出尽量短；重负载字段（per_shard_*、shard_paths）默认不填，由 CLI 层
/// 通过 `--debug-source` 等开关显式请求时才放进来。
#[derive(Debug, Clone, Serialize, Default)]
pub struct Meta {
    /// 命中数据中最新一条的 create_time（unix 秒）。
    /// `q_history` / `q_search` / `q_new_messages` 等基于 Msg_ 表的查询都应填。
    /// `q_sessions` / `q_unread` 这类基于 SessionTable 的查询填会话维度的最新 ts。
    #[serde(skip_serializing_if = "Option::is_none")]
    pub chat_latest_timestamp: Option<i64>,

    /// 上面那条最新消息所在的分片 rel_key（`message/message_3.db`）。
    /// 让 agent 一眼看出"当前命中的最新数据来自哪个分片"。
    #[serde(skip_serializing_if = "Option::is_none")]
    pub chat_latest_db: Option<String>,

    /// 该 chat 在 `session.db.SessionTable.last_timestamp` 里的值（如果可读）。
    /// 这是 WeChat 自己写的"最近一条消息时间"，与上面 `chat_latest_timestamp` 比较
    /// 即可发现"session 说有更新但 history 没读到" → 漏分片。
    #[serde(skip_serializing_if = "Option::is_none")]
    pub session_last_timestamp: Option<i64>,

    /// 本次查询实际遍历的分片数（即 `names.msg_db_keys.len()` 的子集；包括命中 0 行的）。
    pub shards_scanned: usize,

    /// 本次查询里至少返回了 1 行的分片数。
    pub shards_hit: usize,

    /// 磁盘上存在但 daemon 没有 enc_key 的分片 rel_key 列表。
    /// 非空 ⇒ `wx init` 之后 WeChat 又分裂了新分片 → 必须重跑 `wx init`。
    pub unknown_shards: Vec<String>,

    /// 由上述字段派生出的总体状态，CLI / agent 主要看这一个。
    pub status: MetaStatus,

    // 重负载/调试字段：默认不填，CLI 层显式开启
    #[serde(skip_serializing_if = "Option::is_none")]
    pub per_shard_latest: Option<HashMap<String, i64>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cache_mode_per_shard: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub shard_paths: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Copy, Serialize, PartialEq, Eq, Default)]
#[serde(rename_all = "snake_case")]
pub enum MetaStatus {
    #[default]
    Ok,
    /// `session.db` 的最新时间明显领先于本次消息查询结果，说明数据可能过期或不完整。
    PossiblyStale,
    /// 最强信号：磁盘上出现 daemon 不认识的新分片，通常必须重跑 `wx init --force`。
    PossiblyStaleUnknownShards,
    /// 调用方主动传了 `since` / `until` / `offset` 等窗口条件，结果天然是局部视图。
    Windowed,
}

/// session 领先 history 多少秒就报 `PossiblyStale`。
///
/// 24h 的取值是故意保守的：活跃群聊/私聊很少会整整一天没有新消息，
/// 超过这个窗口就值得显式提醒 agent 不要把结果当成“当前最新状态”。
pub const STALE_THRESHOLD_SECS: i64 = 24 * 3600;

/// 统一 freshness status 的优先级：
/// 1. `unknown_shards` 非空：daemon 整体视图已经过期，优先返回 `PossiblyStaleUnknownShards`
/// 2. `windowed=true`：调用方本来就在看局部窗口，不参与 stale 推导
/// 3. `session_last - chat_latest > STALE_THRESHOLD_SECS`：返回 `PossiblyStale`
/// 4. 其他情况：`Ok`
pub fn derive_status(
    chat_latest: Option<i64>,
    session_last: Option<i64>,
    unknown_shards: &[String],
    windowed: bool,
) -> MetaStatus {
    if !unknown_shards.is_empty() {
        return MetaStatus::PossiblyStaleUnknownShards;
    }
    if windowed {
        return MetaStatus::Windowed;
    }
    match (chat_latest, session_last) {
        (Some(c), Some(s)) if s - c > STALE_THRESHOLD_SECS => MetaStatus::PossiblyStale,
        _ => MetaStatus::Ok,
    }
}

/// 扫描 `<db_dir>/message/` 下真实存在的 `message_*.db`，diff 出 daemon 当前没有 key
/// 的未知分片。
///
/// 契约：
/// - 返回值一律是 `/` 分隔的 rel_key（如 `message/message_3.db`），与 `all_keys.json` 对齐
/// - 结果按字典序排序，方便测试和 CLI 稳定显示
/// - 排除 `_fts*` / `_resource*`，因为它们是索引/附件库，不属于消息分片真相
pub fn discover_unknown_shards(db_dir: &Path, known: &[String]) -> Vec<String> {
    let known_set: std::collections::HashSet<String> =
        known.iter().map(|k| k.replace('\\', "/")).collect();

    let msg_dir = db_dir.join("message");
    let entries = match std::fs::read_dir(&msg_dir) {
        Ok(it) => it,
        Err(_) => return Vec::new(),
    };

    let mut unknown: Vec<String> = Vec::new();
    for entry in entries.flatten() {
        let name = entry.file_name();
        let Some(name_str) = name.to_str() else {
            continue;
        };
        if !is_message_shard(name_str) {
            continue;
        }
        let rel = format!("message/{}", name_str);
        if !known_set.contains(&rel) {
            unknown.push(rel);
        }
    }
    unknown.sort();
    unknown
}

fn is_message_shard(file_name: &str) -> bool {
    if !file_name.starts_with("message_") || !file_name.ends_with(".db") {
        return false;
    }
    if file_name.contains("_fts") || file_name.contains("_resource") {
        return false;
    }
    let stem = &file_name["message_".len()..file_name.len() - ".db".len()];
    !stem.is_empty() && stem.chars().all(|c| c.is_ascii_digit())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn is_message_shard_accepts_normal_shards() {
        assert!(is_message_shard("message_0.db"));
        assert!(is_message_shard("message_12.db"));
    }

    #[test]
    fn is_message_shard_rejects_fts_and_resource() {
        assert!(!is_message_shard("message_0_fts.db"));
        assert!(!is_message_shard("message_fts.db"));
        assert!(!is_message_shard("message_0_resource.db"));
        assert!(!is_message_shard("message_resource.db"));
    }

    #[test]
    fn is_message_shard_rejects_non_digits() {
        assert!(!is_message_shard("message_a.db"));
        assert!(!is_message_shard("message_.db"));
        assert!(!is_message_shard("session.db"));
        assert!(!is_message_shard("message_0.db.bak"));
    }

    #[test]
    fn discover_unknown_shards_finds_disk_only_shards() {
        let dir = tempdir();
        let msg_dir = dir.join("message");
        std::fs::create_dir_all(&msg_dir).unwrap();
        for f in [
            "message_0.db",
            "message_1.db",
            "message_2.db",
            "message_0_fts.db",
        ] {
            std::fs::write(msg_dir.join(f), b"").unwrap();
        }
        let known = vec![
            "message/message_0.db".to_string(),
            "message/message_1.db".to_string(),
        ];
        let unknown = discover_unknown_shards(&dir, &known);
        assert_eq!(unknown, vec!["message/message_2.db".to_string()]);
    }

    #[test]
    fn discover_unknown_shards_normalizes_backslash_in_known_keys() {
        let dir = tempdir();
        let msg_dir = dir.join("message");
        std::fs::create_dir_all(&msg_dir).unwrap();
        std::fs::write(msg_dir.join("message_0.db"), b"").unwrap();

        let known = vec!["message\\message_0.db".to_string()];
        assert!(discover_unknown_shards(&dir, &known).is_empty());
    }

    #[test]
    fn discover_unknown_shards_returns_empty_when_message_dir_missing() {
        let dir = tempdir();
        assert!(discover_unknown_shards(&dir, &[]).is_empty());
    }

    #[test]
    fn derive_status_unknown_shards_overrides_windowed() {
        let unknown = vec!["message/message_3.db".to_string()];
        assert_eq!(
            derive_status(Some(100), Some(100), &unknown, true),
            MetaStatus::PossiblyStaleUnknownShards
        );
    }

    #[test]
    fn derive_status_windowed_when_user_paginates() {
        assert_eq!(
            derive_status(Some(100), Some(999_999), &[], true),
            MetaStatus::Windowed,
        );
    }

    #[test]
    fn derive_status_possibly_stale_when_session_far_ahead() {
        let chat = Some(1_000_000);
        let session = Some(1_000_000 + STALE_THRESHOLD_SECS + 1);
        assert_eq!(
            derive_status(chat, session, &[], false),
            MetaStatus::PossiblyStale
        );
    }

    #[test]
    fn derive_status_ok_when_within_threshold() {
        let chat = Some(1_000_000);
        let session = Some(1_000_000 + STALE_THRESHOLD_SECS - 1);
        assert_eq!(derive_status(chat, session, &[], false), MetaStatus::Ok);
    }

    #[test]
    fn derive_status_ok_when_either_side_unknown() {
        assert_eq!(
            derive_status(None, Some(999_999_999), &[], false),
            MetaStatus::Ok
        );
        assert_eq!(derive_status(Some(1), None, &[], false), MetaStatus::Ok);
        assert_eq!(derive_status(None, None, &[], false), MetaStatus::Ok);
    }

    fn tempdir() -> std::path::PathBuf {
        let pid = std::process::id();
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let p = std::env::temp_dir().join(format!("wx-cli-meta-test-{}-{}", pid, nanos));
        std::fs::create_dir_all(&p).unwrap();
        p
    }
}
