# Bolna to Slack Integration

This is a lightweight FastAPI middleware that listens for webhook events from Bolna AI agents. When a call completes, it parses the execution data and pushes a cleanly formatted alert and transcript thread to a specified Slack channel using the official Slack SDK.

## Prerequisites
* Python 3.13 or Docker
* A Slack Workspace with permissions to create Apps
* A Bolna AI account
* [Zrok](https://zrok.io/) CLI installed

---

## 1. Slack Setup (The Sink)

1. Go to the [Slack API Apps page](https://api.slack.com/apps) and click **Create New App** -> **From scratch**.
2. Name your app (e.g., "Bolna Alerts") and select your workspace.
3. In the left sidebar, click **OAuth & Permissions**.
4. Scroll down to **Scopes** -> **Bot Token Scopes** and add:
   * `chat:write` (Allows the bot to post messages)
5. Scroll up and click **Install to Workspace**.
6. Copy the **Bot User OAuth Token** (it starts with `xoxb-`).
7. In your Slack desktop app, create or navigate to the channel you want alerts in. 
8. **Crucial:** You must invite the bot to the channel. Type `/invite @YourBotName` in the channel.
9. Right-click the channel name in the sidebar, select **View channel details**, scroll to the bottom, and copy the **Channel ID** (usually starts with a `C`).

---

## 2. Local Configuration

This application uses a local `secrets.ini` file to manage credentials. 

Create a file named `secrets.ini` in the root directory and format it exactly like this:
```ini
[slack]
bot-token = xoxb-your-bot-token-here
channel-id = C1234567890
```
Refer the file `secrets.ini.example`.

---

## 3. Running the Application
You can run the application either natively using Python or via Docker.

### Option A: Native Python
Install dependencies:
```Bash
pip install -r requirements.txt
```

Start the FastAPI server:
```Bash
python main.py
```
The app will start on http://0.0.0.0:8070.

### Option B: Docker
Build the Docker image:
```Bash
docker build -t bolna-slack-app .
```

Run the container:
```Bash
docker run -d -p 8070:8070 --name bolna-slack bolna-slack-app
```

---

## 4. Zrok Setup (The Tunnel)
To allow Bolna to reach your local application, we use Zrok to create a secure tunnel.
If you haven't authenticated Zrok yet, run zrok enable <your-token>.

Reserve a public endpoint for port 8070:
```Bash
zrok reserve public localhost:8070
```
This outputs a Share Token and a Public URL (e.g., https://abc123xyz.share.zrok.io).

Start the tunnel:
```Bash
zrok share reserved <your-share-token>
```
Keep this terminal window open. Your local app is now accessible via the internet.

----

## 5. Bolna Setup (The Source)
<ol type="a">
    <li>Log in to the Bolna Dashboard.</li>
    <li>Open the agent you want to track.</li>
    <li>Navigate to the Analytics tab.</li>
    <li>Locate the "Push all execution data to webhook" field.</li>
    <li>Paste your Zrok URL and append the /anjee-sunona endpoint path.</li>
    <li>Format: https://<your-zrok-url>.share.zrok.io/anjee-sunona</li>
    <li>Click Save Agent.</li>
</ol>

---

## Testing the Flow
<ol type="i">
    <li>Ensure your FastAPI app is running (Native or Docker).</li>
    <li>Ensure your Zrok tunnel is active.</li>
    <li>Open the Bolna Dashboard and use the Playground to test a call.</li>
    <li>Once the call is completed, Bolna will trigger the webhook, and a formatted message with the transcript will appear in your Slack channel!</li>
</ol>