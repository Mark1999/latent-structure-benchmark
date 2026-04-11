from slack_sdk import WebClient
from dotenv import load_dotenv
import os

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

result = client.chat_postMessage(
    channel="#lsb-alerts",
    text="✅ LSB Orchestrator bot is online and connected."
)

print(f"Message sent, timestamp: {result['ts']}")