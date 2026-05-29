use super::history::{parse_time, parse_time_end};
use super::output::{emit_warnings, print_response, OutputOpts};
use super::transport;
use crate::ipc::Request;
use anyhow::Result;

pub fn cmd_stats(
    chat: String,
    since: Option<String>,
    until: Option<String>,
    opts: OutputOpts,
) -> Result<()> {
    let since_ts = since.as_deref().map(parse_time).transpose()?;
    let until_ts = until.as_deref().map(parse_time_end).transpose()?;
    let (with_meta, debug_source) = opts.request_flags();
    let resp = transport::send(Request::Stats {
        chat,
        since: since_ts,
        until: until_ts,
        with_meta,
        debug_source,
    })?;
    emit_warnings(&resp.data);
    print_response(&resp.data, &opts)
}
