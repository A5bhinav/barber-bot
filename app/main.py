#This is the start of a bot that will take instagram comments for a barber and then respond to them. 
#It will use the Instagram Graph API to fetch comments and respond accordingly.
#It will also use OpenAI's GPT-3.5 to generate responses based on the comments.
#It will take the comments and have a conversation with them about when the best time to come in for a haircut is.
#The bot will ask the user to confirm the time slot, and then send a confirmation message, as well as marking the time slot as booked in a local database.


#This is where the webhooks will go to receive comments from Instagram

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import logging
from services.instagram import InstagramService
from services.calendar import CalendarService
from logic.intent_router import IntentRouter
from logic.responses import ResponseGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Instagram DM Booking Bot")

# Initialize services
instagram_service = InstagramService()
calendar_service = CalendarService()
response_generator = ResponseGenerator()
intent_router = IntentRouter(response_generator, calendar_service)

# Verify token for webhook verification
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Instagram DM Bot is running", "version": "1.0"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for Instagram.
    Facebook/Instagram will call this to verify your webhook.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=challenge)
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Main webhook endpoint to receive Instagram messages and comments.
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")

        # Process the webhook data
        if body.get("object") == "instagram":
            for entry in body.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    await process_message(messaging_event)
                
                # Handle comments if needed
                for changes in entry.get("changes", []):
                    if changes.get("field") == "comments":
                        await process_comment(changes)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Return 200 even on error to prevent Instagram from retrying
        return {"status": "error", "message": str(e)}


async def process_message(messaging_event: dict):
    """Process incoming Instagram direct messages"""
    try:
        sender_id = messaging_event.get("sender", {}).get("id")
        recipient_id = messaging_event.get("recipient", {}).get("id")
        
        # Check if there's a message
        message = messaging_event.get("message", {})
        message_text = message.get("text", "")

        if not message_text or sender_id == recipient_id:
            # Skip if no text or if it's from the page itself
            return

        logger.info(f"Processing message from {sender_id}: {message_text}")

        # Route the message through intent detection and conversation flow
        response_text = await intent_router.route_message(sender_id, message_text)

        # Send response back via Instagram
        if response_text:
            await instagram_service.send_message(sender_id, response_text)
            logger.info(f"Sent response to {sender_id}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Send a fallback message
        fallback_message = "Sorry, I'm having trouble processing your message. Please try again or contact us directly."
        await instagram_service.send_message(sender_id, fallback_message)


async def process_comment(change_data: dict):
    """Process Instagram comments (optional feature)"""
    try:
        value = change_data.get("value", {})
        comment_id = value.get("id")
        comment_text = value.get("text", "")
        commenter_id = value.get("from", {}).get("id")

        if not comment_text:
            return

        logger.info(f"Processing comment from {commenter_id}: {comment_text}")

        # For comments, we might want to reply or just log
        # You could implement comment response logic here if needed
        
    except Exception as e:
        logger.error(f"Error processing comment: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)