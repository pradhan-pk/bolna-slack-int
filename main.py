import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
import configparser

config = configparser.ConfigParser()
config.read("secrets.ini")

# Loading slack connection details
try:
    SLACK_BOT_TOKEN = config["slack"]["bot-token"]
    DEFAULT_CHANNEL_ID = config["slack"]["channel-id"]
except Exception as e:
    print(f"Missing required environment variables: SLACK_BOT_TOKEN or SLACK_CHANNEL_ID: {e}")


app = FastAPI()
slack_client = AsyncWebClient(token=SLACK_BOT_TOKEN)


async def process_and_alert_slack(payload: dict):
    """
    Parses the Bolna payload and sends a formatted Slack alert using Block Kit.
    """
    # Chceking process status to be completed
    if payload.get("status") != "completed":
        print("Call not completed - not proceeding to update Slack.")
        return

    # Data extraction
    call_id = payload.get("id", "N/A")
    agent_id = payload.get("agent_id", "N/A")
    transcript = payload.get("transcript", "No transcript available")
    
    telephony_data = payload.get("telephony_data", {})
    duration = telephony_data.get("duration", "N/A")

    # Slack Block Kit payload for the main alert
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📞 Bolna Call Completed"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Call ID:*\n`{call_id}`"},
                {"type": "mrkdwn", "text": f"*Agent ID:*\n`{agent_id}`"},
                {"type": "mrkdwn", "text": f"*Duration:*\n{duration}s"}
            ]
        }
    ]

    try:
        # Step 1: Post the main alert message to the channel
        response = await slack_client.chat_postMessage(
            channel=DEFAULT_CHANNEL_ID,
            blocks=blocks,
            text=f"Bolna Call Completed for agent {agent_id}" # Fallback text for mobile notifications
        )
        
        # Step 2: Transcript in a thread to keep the main channel clean
        if transcript and transcript != "No transcript available":
            await slack_client.chat_postMessage(
                channel=DEFAULT_CHANNEL_ID,
                thread_ts=response["ts"], # Using timestamp from main message to thread it
                text=f"*Transcript:*\n```{transcript}```"
            )
            
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")

@app.post("/anjee-sunona")
async def bolna_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint to receive the execution payload from Bolna.
    """
    payload = await request.json()
    
    # Offloading processing and Slack API call to background task for immediate ack preventing timeout
    background_tasks.add_task(process_and_alert_slack, payload)
    
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8070)