# Instagram DM Booking Bot for Barbers

An automated Instagram DM bot that helps barbers manage appointment bookings through Instagram direct messages. The bot uses OpenAI for natural conversation and integrates with Google Calendar for appointment management.

## Features

- 🤖 Automated Instagram DM responses
- 📅 Google Calendar integration for appointment booking
- 🧠 Natural language processing with OpenAI GPT-3.5
- ✅ Automatic appointment confirmation
- 📱 Real-time availability checking
- 💬 Friendly, conversational interface

## Project Structure

```
app/
├── main.py                 # FastAPI webhook server
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── services/
│   ├── instagram.py       # Instagram Graph API integration
│   └── calendar.py        # Google Calendar API integration
├── logic/
│   ├── intent_router.py   # Message routing and intent detection
│   ├── booking.py         # Booking management logic
│   └── responses.py       # Response generation templates
└── tests/
    └── test_logic.py      # Unit tests
```

## Prerequisites

Before you begin, make sure you have:

1. ✅ Instagram Business Account
2. ✅ Facebook/Meta Business Suite account
3. ✅ Facebook Developer account
4. ✅ Long-lived Instagram access token
5. ⬜ Google Cloud Project (for Calendar API)
6. ⬜ OpenAI API key
7. ⬜ Server or hosting platform (Render, Railway, or VPS)

## Setup Instructions

### 1. Install Dependencies

```bash
cd app
pip install -r requirements.txt
```

### 2. Set Up Google Calendar API

This is the part you haven't done yet - here's how:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
5. Create a Key:
   - Click on your new service account
   - Go to "Keys" tab
   - "Add Key" > "Create new key" > "JSON"
   - Save the downloaded file as `credentials.json` in your `app/` directory
6. Share your Google Calendar with the service account:
   - Open Google Calendar
   - Go to Settings > Share with specific people
   - Add the service account email (found in credentials.json)
   - Give "Make changes to events" permission
7. Get your Calendar ID:
   - In Google Calendar settings
   - Select your calendar
   - Scroll to "Integrate calendar"
   - Copy the Calendar ID

### 3. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Save it securely

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
# From Facebook Developer
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
INSTAGRAM_PAGE_ID=your_instagram_business_account_id

# Create a random secure string (e.g., use: openssl rand -base64 32)
VERIFY_TOKEN=your_custom_random_string_here

# From OpenAI
OPENAI_API_KEY=sk-...

# From Google Calendar setup
GOOGLE_CALENDAR_ID=your_email@gmail.com
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json

# Customize for your friend's business
BARBER_NAME=YourFriend's Name
BARBER_BUSINESS_HOURS_START=09:00
BARBER_BUSINESS_HOURS_END=18:00
APPOINTMENT_DURATION_MINUTES=60
```

### 5. Test Locally

```bash
cd app
python main.py
```

The server should start on `http://localhost:8000`

Test the health check:
```bash
curl http://localhost:8000
```

### 6. Deploy to a Server

You need a publicly accessible URL for Instagram webhooks. Here are recommended options:

#### Option A: Render.com (Free Tier Available)

1. Create account at [Render.com](https://render.com)
2. Click "New +" > "Web Service"
3. Connect your GitHub repo (you'll need to push your code to GitHub first)
4. Configure:
   - Name: `instagram-barber-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all your environment variables from `.env`
6. Deploy!

#### Option B: Railway.app

1. Create account at [Railway.app](https://railway.app)
2. "New Project" > "Deploy from GitHub repo"
3. Select your repo
4. Add environment variables
5. Railway will auto-detect Python and deploy

#### Option C: Ngrok (For Testing Only)

For testing webhooks locally:
```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start your app
python main.py

# In another terminal, expose port 8000
ngrok http 8000
```

Use the ngrok HTTPS URL for webhook setup (but remember it changes each time).

### 7. Configure Instagram Webhooks

Now for the final connection:

1. Go to your [Facebook Developer App](https://developers.facebook.com/apps)
2. Select your app
3. In the left sidebar, go to "Instagram" > "Webhooks"
4. Click "Configure Webhooks"
5. Enter your webhook details:
   - **Callback URL**: `https://your-domain.com/webhook`
   - **Verify Token**: The same token you put in your `.env` file
6. Click "Verify and Save"
7. Subscribe to these fields:
   - `messages`
   - `messaging_postbacks`
   - `message_echoes`
8. Click "Save"

### 8. Test the Bot

1. Send a DM to your Instagram business account from another account
2. Try messages like:
   - "Hi, I want to book a haircut"
   - "What times do you have available tomorrow?"
   - "Book me for Saturday at 2pm"

Check your server logs to see the bot processing messages!

## Troubleshooting

### Webhook Verification Fails
- Double-check your VERIFY_TOKEN matches in both `.env` and Facebook Developer settings
- Make sure your server is publicly accessible (not localhost)
- Check server logs for errors

### Messages Not Being Received
- Verify Instagram webhooks are subscribed to `messages`
- Check that your access token hasn't expired
- Ensure your Instagram account is in Business mode
- Check server logs for incoming webhook requests

### Google Calendar Not Working
- Verify the service account email is shared with your calendar
- Check that credentials.json is in the correct location
- Make sure you've enabled the Calendar API in Google Cloud Console
- Verify the calendar ID is correct

### OpenAI Errors
- Check your API key is valid
- Verify you have credits/billing set up
- Check rate limits if getting 429 errors

### Bot Responses Don't Make Sense
- Check your OpenAI API key is working
- Review the conversation state in logs
- The bot learns context from previous messages

## File Descriptions

- **main.py**: FastAPI server handling webhooks
- **services/instagram.py**: Instagram API calls
- **services/calendar.py**: Google Calendar integration
- **logic/intent_router.py**: Detects user intent and routes conversation
- **logic/booking.py**: Manages appointment creation and availability
- **logic/responses.py**: Templates for bot responses
- **tests/test_logic.py**: Unit tests

## Cost Considerations

- **Instagram/Meta**: Free
- **Google Calendar API**: Free (under quota limits)
- **OpenAI API**: ~$0.001-0.002 per conversation (very cheap for typical use)
- **Hosting**: Free tier available on Render/Railway, or ~$5-10/month for reliable hosting

## Security Notes

- Never commit your `.env` file or `credentials.json` to Git
- Keep your access tokens secure
- Rotate tokens periodically
- Use environment variables on your hosting platform

## Next Steps & Improvements

Once it's working, consider adding:
- User name collection during first conversation
- Cancellation/rescheduling support
- Multiple service type selection (haircut, beard trim, etc.)
- SMS/email confirmations
- Admin dashboard for managing bookings
- Redis for persistent conversation state
- Rate limiting to prevent abuse

## Getting Help

If you run into issues:
1. Check the logs on your hosting platform
2. Verify all environment variables are set correctly
3. Test each API connection individually
4. Use the test file: `pytest tests/test_logic.py -v`

## License

Free to use for personal projects!

---

Built with ❤️ for your friend's barbershop
