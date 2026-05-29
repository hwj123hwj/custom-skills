use anyhow::Result;
use crate::ipc::Request;
use super::transport;
use super::output::{resolve, print_value};

pub fn cmd_members(chat: String, json: bool) -> Result<()> {
    let resp = transport::send(Request::Members { chat })?;
    let members = resp.data.get("members")
        .cloned()
        .unwrap_or(serde_json::Value::Array(vec![]));
    print_value(&members, &resolve(json))
}
