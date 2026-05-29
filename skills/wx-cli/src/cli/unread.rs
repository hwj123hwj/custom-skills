use super::output::{emit_warnings, print_response, OutputOpts};
use super::transport;
use crate::ipc::Request;
use anyhow::Result;

pub fn cmd_unread(limit: usize, filter: Vec<String>, opts: OutputOpts) -> Result<()> {
    // 空或含 "all" 视为不过滤；其他值已被 clap value_parser 验证过，直接透传给 daemon。
    let filter_vec = if filter.is_empty() || filter.iter().any(|s| s == "all") {
        None
    } else {
        Some(filter)
    };
    let (with_meta, debug_source) = opts.request_flags();
    let resp = transport::send(Request::Unread {
        limit,
        filter: filter_vec,
        with_meta,
        debug_source,
    })?;
    emit_warnings(&resp.data);
    print_response(&resp.data, &opts)
}
