# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "bilibili-api-python",
#     "SQLAlchemy",
#     "psycopg[binary]",
#     "python-dotenv",
#     "httpx",
# ]
# ///

import asyncio
import os
import re
import datetime
import io
import json
import httpx
from dotenv import load_dotenv
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Bilibili-api 相关导入
from bilibili_api import user, video, Credential, sync, HEADERS

# 加载配置
load_dotenv()

# ================= 配置区 =================
# 初始连接库名
POSTGRES_DB = "postgres"

_ENGINE = None

def _quote_ident(ident: str) -> str:
    return '\"' + ident.replace('\"', '\"\"') + '\"'
# ================= 配置加载 =================
def load_secrets():
    """递归向上查找 secrets.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        secrets_path = os.path.join(current_dir, "secrets.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 到达根目录
            return {}
        current_dir = parent_dir

SECRETS = load_secrets()

# 优先从 secrets.json 获取完整 Cookie 字符串
BILIBILI_COOKIE = SECRETS.get("BILIBILI_COOKIE") or os.getenv("BILIBILI_COOKIE")

# 从完整 Cookie 中解析 SESSDATA, BILI_JCT, BUVID3
SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""

if BILIBILI_COOKIE:
    sess_match = re.search(r'SESSDATA=([^;]+)', BILIBILI_COOKIE)
    jct_match = re.search(r'bili_jct=([^;]+)', BILIBILI_COOKIE)
    buv_match = re.search(r'buvid3=([^;]+)', BILIBILI_COOKIE)
    if sess_match: SESSDATA = sess_match.group(1)
    if jct_match: BILI_JCT = jct_match.group(1)
    if buv_match: BUVID3 = buv_match.group(1)

# ================= 环境变量增强加载 =================
def get_env_flexible(key_name, default=None):
    """优先从 os.getenv 获取，如果为空则尝试从 Windows 用户注册表读取（解决终端未刷新问题），最后从 secrets.json 获取"""
    # 1. 尝试当前进程环境变量
    val = os.getenv(key_name)
    if val: return val
    
    # 2. 尝试从 Windows 注册表读取 (仅限 Windows)
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, key_name)
                if val: return val
        except Exception:
            pass
            
    # 3. 尝试从 secrets.json 获取
    if SECRETS and key_name in SECRETS:
        return SECRETS[key_name]
        
    return default

# AI API Key 加载
SILICONFLOW_API_KEY = get_env_flexible("SILICONFLOW_API_KEY")

# 检查必要的 Cookie 是否存在
if not SESSDATA or not BILI_JCT:
    print("⚠️ 警告: 未能在 secrets.json 或 环境变量的 BILIBILI_COOKIE 中解析出 SESSDATA 或 BILI_JCT。B站相关功能可能会受限。")

# 创建凭证
credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)

# ================= 数据库操作 =================
def get_db_config():
    """从环境变量或 secrets.json 获取数据库配置"""
    return {
        "user": get_env_flexible("DB_USER", "root"),
        "password": get_env_flexible("DB_PASSWORD", "15671040800q"),
        "host": get_env_flexible("DB_HOST", "127.0.0.1"),
        "port": get_env_flexible("DB_PORT", "5433"),
        "database": get_env_flexible("DB_NAME", "media_knowledge_base")
    }

def _make_db_url(database: str):
    config = get_db_config()
    port = config.get("port")
    try:
        port = int(port) if port is not None else None
    except (TypeError, ValueError):
        port = None

    return URL.create(
        "postgresql+psycopg",
        username=config.get("user"),
        password=config.get("password"),
        host=config.get("host"),
        port=port,
        database=database,
    )

def get_engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE
    config = get_db_config()
    _ENGINE = create_engine(_make_db_url(config["database"]), pool_pre_ping=True)
    return _ENGINE

def init_database():
    """初始化数据库和表"""
    config = get_db_config()
    # 尝试连接默认库检查目标库是否存在
    admin_engine = create_engine(_make_db_url(POSTGRES_DB), isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :dbname"),
                {"dbname": config["database"]},
            ).first()
            if not exists:
                print(f"创建数据库: {config['database']}...")
                conn.execute(text(f"CREATE DATABASE {_quote_ident(config['database'])}"))
    finally:
        admin_engine.dispose()

    # 创建表
    with get_engine().begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS bili_video_contents (
            id SERIAL PRIMARY KEY,
            bvid VARCHAR(50) UNIQUE NOT NULL,
            title TEXT,
            up_name VARCHAR(255),
            up_mid BIGINT,
            up_sign TEXT,
            tid INTEGER,
            pub_time TIMESTAMP,
            tags TEXT[],
            content_text TEXT,
            organized_content TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """))

async def check_exists(bvid):
    """检查数据库是否已存在且内容完整"""
    try:
        with get_engine().connect() as conn:
            return (
                conn.execute(
                    text("SELECT 1 FROM bili_video_contents WHERE bvid = :bvid AND content_text IS NOT NULL"),
                    {"bvid": bvid},
                ).first()
                is not None
            )
    except:
        return False

def save_up_to_db(up_data):
    """保存或更新 UP 主信息"""
    query = text("""
    INSERT INTO up_users (mid, name, sign, fans, level, face, last_updated)
    VALUES (:mid, :name, :sign, :fans, :level, :face, CURRENT_TIMESTAMP)
    ON CONFLICT (mid) DO UPDATE SET
        name = EXCLUDED.name,
        sign = EXCLUDED.sign,
        fans = EXCLUDED.fans,
        level = EXCLUDED.level,
        face = EXCLUDED.face,
        last_updated = CURRENT_TIMESTAMP;
    """)
    with get_engine().begin() as conn:
        conn.execute(
            query,
            {
                "mid": up_data["mid"],
                "name": up_data["name"],
                "sign": up_data["sign"],
                "fans": up_data.get("fans", 0),
                "level": up_data.get("level", 0),
                "face": up_data.get("face", ""),
            },
        )
    print(f"UP主 {up_data['name']} (Fans: {up_data.get('fans')}) 信息已更新。")

def save_to_db(data):
    """保存记录到数据库 (视频内容表)"""
    query = text("""
    INSERT INTO bili_video_contents (bvid, title, up_mid, tid, pub_time, tags, content_text)
    VALUES (:bvid, :title, :up_mid, :tid, :pub_time, :tags, :content_text)
    ON CONFLICT (bvid) DO UPDATE SET
        title = EXCLUDED.title,
        up_mid = EXCLUDED.up_mid,
        tid = EXCLUDED.tid,
        pub_time = EXCLUDED.pub_time,
        tags = EXCLUDED.tags,
        content_text = EXCLUDED.content_text,
        created_at = CURRENT_TIMESTAMP;
    """)
    with get_engine().begin() as conn:
        conn.execute(
            query,
            {
                "bvid": data["bvid"],
                "title": data["title"],
                "up_mid": data["up_mid"],
                "tid": data["tid"],
                "pub_time": data["pub_time"],
                "tags": data["tags"],
                "content_text": data["content_text"],
            },
        )

# ================= ASR 逻辑 =================

async def async_speech_to_text(audio_data: bytes, filename: str):
    """异步调用 SiliconFlow ASR"""
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {SILICONFLOW_API_KEY}"}

    # 构造 multipart/form-data
    files = {"file": (filename, audio_data, "audio/mpeg")}
    data = {"model": "TeleAI/TeleSpeechASR"}

    async with httpx.AsyncClient() as client:
        try:
            print(f"正在上传 {filename} 进行语音识别...")
            response = await client.post(url, headers=headers, data=data, files=files, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get('text', '')
        except Exception as e:
            print(f"ASR 识别失败: {e}")
            return None

# ================= Bilibili-api 逻辑实现 =================

async def get_up_videos(uid: int, max_pages: int = 3):
    """获取指定 UP 主的视频（默认只抓取前 3 页最新视频）"""
    u = user.User(uid=uid, credential=credential)
    all_videos = []
    page = 1
    while page <= max_pages:
        res = await u.get_videos(pn=page, ps=30)
        v_list = res.get('list', {}).get('vlist', [])
        if not v_list:
            break
        all_videos.extend(v_list)
        print(f"已获取 UP主({uid}) 视频列表: 第 {page} 页...")
        if len(all_videos) >= res.get('page', {}).get('count', 0):
            break
        page += 1
        await asyncio.sleep(1.5) # 稍微增加延迟，更安全
    return all_videos

async def process_single_video(bvid: str, up_info_cached=None):
    """处理单个视频：抓取 -> 转录 -> 入库"""
    if await check_exists(bvid):
        print(f"跳过: {bvid} 已在库中且有内容。")
        return False

    v = video.Video(bvid=bvid, credential=credential)

    # 1. 获取视频详情
    info = await v.get_info()
    title = info['title']
    owner = info['owner']
    pub_time = datetime.datetime.fromtimestamp(info['pubdate'])
    tid = info['tid']

    # 获取标签
    tags_res = await v.get_tags()
    tags = [t['tag_name'] for t in tags_res] if isinstance(tags_res, list) else []

    # 2. 获取/保存 UP 主信息
    up_data_for_db = None
    if up_info_cached:
        up_data_for_db = up_info_cached
    else:
        u = user.User(uid=owner['mid'], credential=credential)
        u_base = await u.get_user_info()
        try:
            # 尝试获取关系统计（粉丝数）
            rel_info = await u.get_relation_info()
            u_base['fans'] = rel_info.get('follower', 0)
        except:
            u_base['fans'] = 0
        up_data_for_db = {
            'mid': owner['mid'],
            'name': u_base.get('name', owner['name']),
            'sign': u_base.get('sign', ''),
            'fans': u_base['fans'],
            'level': u_base.get('level', 0),
            'face': u_base.get('face', '')
        }
        # 单个处理时也存一下 UP 表
        save_up_to_db(up_data_for_db)

    print(f"正在处理视频: {title} ({bvid})")

    # 3. 获取音频流
    url_data = await v.get_download_url(0)
    detecter = video.VideoDownloadURLDataDetecter(url_data)
    streams = detecter.detect_best_streams()

    # 我们优先要音频流
    audio_url = None
    if detecter.check_video_and_audio_stream():
        # DASH 流，streams[1] 通常是音频
        audio_url = streams[1].url
    else:
        # FLV/MP4 流，直接下音视频流（这里比较麻烦，我们尽量用 DASH）
        audio_url = streams[0].url

    if not audio_url:
        print(f"未能获取到音频流: {bvid}")
        return False

    # 4. 下载音频到内存
    async with httpx.AsyncClient(headers=HEADERS) as client:
        # bilibili 的 CDN 有时候需要 referer
        res = await client.get(audio_url, timeout=60)
        res.raise_for_status()
        audio_bytes = res.content

    # 5. ASR 转换
    content_text = await async_speech_to_text(audio_bytes, f"{bvid}.mp3")

    if not content_text:
        print(f"视频 {bvid} 无转录内容，跳过。")
        return False

    # 6. 入库
    db_data = {
        'bvid': bvid,
        'title': title,
        'up_mid': owner['mid'],
        'tid': tid,
        'pub_time': pub_time,
        'tags': tags,
        'content_text': content_text
    }
    save_to_db(db_data)
    print(f"完成! 已保存至数据库。")
    return True

# ================= 导出文稿逻辑 =================

def clean_filename(title):
    """替换 Windows 文件名非法字符"""
    invalid_chars = r'\/:*?"<>|'
    for char in invalid_chars:
        title = title.replace(char, "_")
    return title.strip()

def export_transcript(query, export_all=False):
    """导出视频文稿到 TXT 文件

    Args:
        query: 查询条件（BVID 或标题关键词）
        export_all: 是否导出所有视频（仅当 query 为 'all' 时生效）
    """
    # 使用项目目录下的 transcripts 文件夹
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcripts")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建导出目录: {output_dir}")

    try:
        # 判断导出模式
        if export_all or query.lower() == "all":
            # 导出所有视频
            stmt = text("SELECT bvid, title, content_text FROM bili_video_contents WHERE content_text IS NOT NULL")
            params = {}
        elif query.upper().startswith("BV"):
            # BVID 精确搜索
            stmt = text("SELECT bvid, title, content_text FROM bili_video_contents WHERE bvid = :bvid")
            params = {"bvid": query}
        else:
            # 标题模糊搜索
            stmt = text("SELECT bvid, title, content_text FROM bili_video_contents WHERE title ILIKE :title")
            params = {"title": f"%{query}%"}

        with get_engine().connect() as conn:
            results = conn.execute(stmt, params).fetchall()

        if not results:
            print(f"[错误] 未找到匹配的视频: {query}")
            return

        print(f"[信息] 找到 {len(results)} 个匹配视频，正在导出...")

        for bvid, title, content in results:
            if not content:
                print(f"[警告] 视频 [{title}] ({bvid}) 没有文稿内容，跳过。")
                continue

            safe_title = clean_filename(title)
            file_path = os.path.join(output_dir, f"{safe_title}.txt")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"标题: {title}\n")
                f.write(f"BVID: {bvid}\n")
                f.write("=" * 50 + "\n\n")
                f.write(content)

            print(f"[成功] 已导出: {file_path}")

    except Exception as e:
        print(f"数据库查询失败: {e}")
        return

# ================= 主程序入口 =================

async def main():
    init_database()

    args = sys.argv[1:]

    if not args:
        print("=" * 60)
        print("B站视频采集与导出工具")
        print("=" * 60)
        print("\n使用方法:")
        print("  采集模式:")
        print("    uv run python bili_collect_and_export.py <UID> [页数]        # 采集 UP 主视频（默认前3页）")
        print("    uv run python bili_collect_and_export.py <BVID1> <BVID2>    # 采集指定视频")
        print("\n  导出模式:")
        print("    uv run python bili_collect_and_export.py export <QUERY>     # 导出指定视频文稿")
        print("    uv run python bili_collect_and_export.py export all         # 导出所有视频文稿")
        print("\n  参数说明:")
        print("    UID        - UP 主的数字 ID")
        print("    页数        - 可选，采集前N页视频（默认3页，每页最多30个视频）")
        print("    BVID       - 视频 ID，如 BV1xx411c7mD")
        print("    QUERY      - BVID 精确搜索 或 标题关键词模糊搜索")
        print("\n  示例:")
        print("    uv run python bili_collect_and_export.py 123456789")
        print("    uv run python bili_collect_and_export.py 123456789 5        # 采集前5页")
        print("    uv run python bili_collect_and_export.py BV1xx411c7mD")
        print("    uv run python bili_collect_and_export.py export Python教程")
        print("    uv run python bili_collect_and_export.py export all")
        print("=" * 60)
        return

    # 判断是否为导出模式
    if args[0].lower() == "export":
        if len(args) < 2:
            print("请提供导出查询条件（BVID 或 标题关键词 或 'all'）")
            return

        query = " ".join(args[1:])
        export_all = query.lower() == "all"
        export_transcript(query, export_all)
        return

    # 采集模式：判断第一个参数是 UID 还是 BVID
    if args[0].isdigit():
        uid = int(args[0])

        # 解析页数参数（可选）
        max_pages = 3  # 默认采集前3页
        if len(args) >= 2 and args[1].isdigit():
            max_pages = int(args[1])
            print(f"正在获取 UP主 {uid} 的视频（最多采集 {max_pages} 页）...")
        else:
            print(f"正在获取 UP主 {uid} 的视频（默认采集前 3 页，可指定页数：uv run python bili_collect_and_export.py {uid} 5）...")

        # 先取一次 UP 主信息并行保存
        u = user.User(uid=uid, credential=credential)
        up_base = await u.get_user_info()
        try:
            rel_info = await u.get_relation_info()
            up_base['fans'] = rel_info.get('follower', 0)
        except:
            up_base['fans'] = 0

        up_db_info = {
            'mid': uid,
            'name': up_base.get('name', ''),
            'sign': up_base.get('sign', ''),
            'fans': up_base['fans'],
            'level': up_base.get('level', 0),
            'face': up_base.get('face', '')
        }
        save_up_to_db(up_db_info)

        video_list = await get_up_videos(uid, max_pages=max_pages)
        print(f"共发现 {len(video_list)} 个视频，开始逐一处理...")

        for v_summary in video_list:
            bvid = v_summary['bvid']
            try:
                await process_single_video(bvid, up_info_cached=up_db_info)
            except Exception as e:
                print(f"处理 {bvid} 失败: {e}")
            # 适当延迟
            await asyncio.sleep(1)
    else:
        # 处理 BVID 列表
        for bvid in args:
            if bvid.startswith("BV"):
                try:
                    await process_single_video(bvid)
                except Exception as e:
                    print(f"处理 {bvid} 失败: {e}")
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
