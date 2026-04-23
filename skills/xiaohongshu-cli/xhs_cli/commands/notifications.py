"""Notification commands: unread counts and notification feeds."""

import click

from ..command_normalizers import normalize_unread_summary
from ..formatter import console, render_notifications
from ._common import handle_command, structured_output_options


@click.command()
@click.option(
    "--type", "notif_type",
    type=click.Choice(["mentions", "likes", "connections"]),
    default="mentions",
    help="Notification type: mentions (评论和@), likes (赞和收藏), connections (新增关注)",
)
@click.option("--cursor", default="", help="Pagination cursor")
@click.option("--num", default=20, help="Number of items per page")
@structured_output_options
@click.pass_context
def notifications(ctx, notif_type: str, cursor: str, num: int, as_json: bool, as_yaml: bool):
    """View notifications (mentions, likes, connections)."""
    def _load_notifications(client):
        if notif_type == "mentions":
            return client.get_notification_mentions(cursor=cursor, num=num)
        if notif_type == "likes":
            return client.get_notification_likes(cursor=cursor, num=num)
        return client.get_notification_connections(cursor=cursor, num=num)

    handle_command(
        ctx,
        action=_load_notifications,
        render=lambda data: render_notifications(data, notif_type),
        as_json=as_json,
        as_yaml=as_yaml,
    )


@click.command()
@structured_output_options
@click.pass_context
def unread(ctx, as_json: bool, as_yaml: bool):
    """Show unread notification counts."""
    def _render_unread(data):
        summary = normalize_unread_summary(data)
        console.print(f"📬 未读通知: [bold]{summary['unread_count']}[/bold]")
        console.print(f"   💬 评论和@: {summary['mentions']}")
        console.print(f"   ❤️ 赞和收藏: {summary['likes']}")
        console.print(f"   👥 新增关注: {summary['connections']}")

    handle_command(
        ctx,
        action=lambda client: client.get_unread_count(),
        render=_render_unread,
        as_json=as_json,
        as_yaml=as_yaml,
    )
