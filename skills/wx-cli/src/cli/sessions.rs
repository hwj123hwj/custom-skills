use super::output::{emit_warnings, print_response, OutputOpts};
use super::transport;
use crate::ipc::Request;
use anyhow::Result;

pub fn cmd_sessions(limit: usize, opts: OutputOpts) -> Result<()> {
    let (with_meta, debug_source) = opts.request_flags();
    let resp = transport::send(Request::Sessions {
        limit,
        with_meta,
        debug_source,
    })?;
    emit_warnings(&resp.data);
    print_response(&resp.data, &opts)
}
