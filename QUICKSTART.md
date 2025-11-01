# Quick Start Guide - Instagram Barber Bot

## What You Need to Do Next (In Order)

### ✅ Already Done
- [x] Instagram Business Account setup
- [x] Meta Business Suite linked
- [x] Facebook Developer account
- [x] Long-lived access token generated

### 🎯 Next Steps (Do These Now)

#### Step 1: Get OpenAI API Key (5 minutes)
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Click on your profile (top right) > "API Keys"
4. Click "Create new secret key"
5. Copy and save the key (starts with `sk-`)
6. Add payment method in Billing (you'll only spend cents per day)

#### Step 2: Set Up Google Calendar API (15 minutes)
1. Go to https://console.cloud.google.com/
2. Create a new project: "Barber Bot"
3. Enable Google Calendar API:
   - Menu > "APIs & Services" > "Library"
   - Search "Google Calendar API" and Enable it
4. Create Service Account:
   - "APIs & Services" > "Credentials"
   - "Create Credentials" > "Service Account"
   - Name it "barber-bot" and Create
5. Create JSON Key:
   - Click on the service account you just created
   - "Keys" tab > "Add Key" > "Create new key" > JSON
   - Download the file and rename it to `credentials.json`
   - Put it in the `app/` folder
6. Share Your Calendar:
   - Open Google Calendar (calendar.google.com)
   - Settings (gear icon) > Select your calendar
   - "Share with specific people"
   - Add the email from your credentials.json (looks like: xyz@project.iam.gserviceaccount.com)
   - Give it "Make changes to events" permission
7. Get Calendar ID:
   - Same settings page > "Integrate calendar"
   - Copy the "Calendar ID" (usually your email)

#### Step 3: Configure Your App (5 minutes)
1. Copy `app/.env.example` to `app/.env`
2. Fill in these values:

```bash
# Instagram (you already have these)
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_PAGE_ID=your_page_id_here

# Create a random string for verify token
VERIFY_TOKEN=make_up_a_random_string_12345

# OpenAI (from Step 1)
OPENAI_API_KEY=sk-your_key_here

# Google Calendar (from Step 2)
GOOGLE_CALENDAR_ID=your_email@gmail.com
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json

# Your friend's info
BARBER_NAME=Your Friend's Name
BARBER_BUSINESS_HOURS_START=09:00
BARBER_BUSINESS_HOURS_END=18:00
APPOINTMENT_DURATION_MINUTES=60
```

#### Step 4: Test Locally (5 minutes)
```bash
cd app
pip install -r requirements.txt
python main.py
```

Visit http://localhost:8000 - you should see: `{"status": "Instagram DM Bot is running"}`

#### Step 5: Deploy to Render.com (10 minutes)

**First, push your code to GitHub:**
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub, then:
git remote add origin https://github.com/yourusername/barber-bot.git
git push -u origin main
```

**Then deploy:**
1. Go to https://render.com and sign up
2. Connect your GitHub account
3. Click "New +" > "Web Service"
4. Select your repo
5. Configure:
   - **Name**: barber-bot
   - **Environment**: Python 3
   - **Build Command**: `cd app && pip install -r requirements.txt`
   - **Start Command**: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add all environment variables from your `.env` file (click "Advanced" > "Add Environment Variable")
7. Click "Create Web Service"
8. Wait for deployment (~5 minutes)
9. Copy your Render URL (e.g., https://barber-bot-xyz.onrender.com)

#### Step 6: Connect Instagram Webhooks (5 minutes)
1. Go to https://developers.facebook.com/apps
2. Select your app
3. Left sidebar: "Products" > Add "Webhooks" if not already added
4. Click "Instagram" > "Webhooks" > "Configure Webhooks"
5. Click "Edit" next to "messages"
6. Fill in:
   - **Callback URL**: `https://your-render-url.onrender.com/webhook`
   - **Verify Token**: The exact string you put in VERIFY_TOKEN in your .env
7. Click "Verify and Save"
8. Toggle ON these subscriptions:
   - messages
   - messaging_postbacks
   - message_echoes

#### Step 7: Test It! (2 minutes)
1. From another Instagram account, DM your business account
2. Send: "Hi, I want to book a haircut"
3. The bot should respond!

Try these test messages:
- "What times are available tomorrow?"
- "Book me for Saturday at 2pm"
- "What services do you offer?"

---

## 🎉 You're Done!

Your bot is now live and handling Instagram DMs automatically!

## Quick Troubleshooting

**Bot isn't responding to DMs?**
- Check Render logs (Dashboard > Logs)
- Verify webhook is subscribed to "messages"
- Make sure VERIFY_TOKEN matches in both places

**"Calendar service not initialized"?**
- Make sure credentials.json is in the app/ folder
- Verify you shared the calendar with the service account email

**OpenAI errors?**
- Check your API key is correct
- Verify billing is set up on OpenAI

## Need Help?

Check the full README.md for detailed troubleshooting and advanced features.

## Costs

Running this bot will cost approximately:
- Hosting: FREE (Render free tier) or $7/month
- OpenAI: ~$0.50-2/month depending on message volume
- Google Calendar: FREE

Total: Less than $3/month for typical use! 🎉