import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

CHANNELS = {
    "pipeline":  os.environ["SLACK_PIPELINE_CHANNEL"],
    "alerts":    os.environ["SLACK_ALERTS_CHANNEL"],
    "architect": os.environ["SLACK_ARCHITECT_CHANNEL"],
    "coder":     os.environ["SLACK_CODER_CHANNEL"],
    "reviewer":  os.environ["SLACK_REVIEWER_CHANNEL"],
    "tester":    os.environ["SLACK_TESTER_CHANNEL"],
}

def post(channel_key: str, message: str) -> str:
    """Post a message to a channel. Returns the message timestamp (ts)."""
    try:
        result = client.chat_postMessage(
            channel=CHANNELS[channel_key],
            text=message
        )
        return result["ts"]
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
        raise

def wait_for_approval(prompt: str, timeout_seconds: int = 3600) -> bool:
    """
    Post prompt to #lsb-pipeline and poll for 'approved' or 'rejected'.
    Returns True if approved, False if rejected or timed out.
    """
    import time

    ts = post("pipeline", f"⏸ *Approval needed:*\n{prompt}\n\nReply `approved` or `rejected`.")
    channel_id = _get_channel_id("pipeline")

    deadline = time.time() + timeout_seconds
    last_checked = ts  # only look at messages after the bot's own post

    print(f"Waiting for approval in #lsb-pipeline (timeout: {timeout_seconds}s)...")

    while time.time() < deadline:
        time.sleep(10)  # poll every 10 seconds
        try:
            result = client.conversations_history(
                channel=channel_id,
                oldest=last_checked,
                limit=10
            )
            for msg in reversed(result["messages"]):
                if msg.get("ts") == ts:
                    continue  # skip the bot's own message
                text = msg.get("text", "").strip().lower()
                if "approved" in text:
                    post("pipeline", "✅ Approved — continuing pipeline.")
                    return True
                elif "rejected" in text:
                    post("pipeline", "❌ Rejected — pipeline halted.")
                    return False
        except SlackApiError as e:
            print(f"Poll error: {e.response['error']}")

    post("alerts", "⚠️ Approval timeout — pipeline halted waiting for response.")
    return False

def _get_channel_id(channel_key: str) -> str:
    """Resolve channel name to ID for history lookups."""
    name = CHANNELS[channel_key].lstrip("#")
    result = client.conversations_list(types="private_channel,public_channel")
    for ch in result["channels"]:
        if ch["name"] == name:
            return ch["id"]
    raise ValueError(f"Channel not found: {name}")