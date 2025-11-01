import os
import logging
from datetime import datetime
from typing import Dict, Optional
from openai import AsyncOpenAI
from logic.responses import ResponseGenerator
from logic.booking import BookingManager
from services.calendar import CalendarService

logger = logging.getLogger(__name__)


class IntentRouter:
    """Routes messages based on detected intent and manages conversation state"""

    def __init__(self, response_generator: ResponseGenerator, calendar_service: CalendarService):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.response_generator = response_generator
        self.booking_manager = BookingManager(calendar_service)
        
        # Simple in-memory conversation state (consider using Redis for production)
        self.conversation_state: Dict[str, Dict] = {}

    async def route_message(self, user_id: str, message_text: str) -> str:
        """
        Route incoming message to appropriate handler based on intent
        
        Args:
            user_id: Instagram user ID
            message_text: Message text from user
            
        Returns:
            str: Response message to send back
        """
        # Get or initialize conversation state
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {
                "stage": "initial",
                "history": [],
                "booking_data": {}
            }

        state = self.conversation_state[user_id]
        state["history"].append({"role": "user", "content": message_text})

        # Detect intent using OpenAI
        intent = await self._detect_intent(message_text, state)
        logger.info(f"Detected intent for user {user_id}: {intent}")

        # Route based on intent and current stage
        response = await self._handle_intent(user_id, intent, message_text, state)

        # Add response to history
        state["history"].append({"role": "assistant", "content": response})

        # Keep only last 10 messages to manage context size
        if len(state["history"]) > 10:
            state["history"] = state["history"][-10:]

        return response

    async def _detect_intent(self, message_text: str, state: Dict) -> str:
        """
        Use OpenAI to detect user intent from message
        
        Returns one of: booking_inquiry, confirm_booking, cancel_booking, 
                       general_question, greeting, other
        """
        current_stage = state.get("stage", "initial")
        
        system_prompt = f"""You are an intent classifier for a barber appointment booking system.
Current conversation stage: {current_stage}

Classify the user's message into ONE of these intents:
- booking_inquiry: User wants to book an appointment or asking about availability
- confirm_booking: User is confirming a proposed appointment time
- cancel_booking: User wants to cancel or reschedule
- general_question: Asking about services, prices, location, etc.
- greeting: Just saying hi/hello
- other: Anything else

Respond with ONLY the intent name, nothing else."""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_text}
                ],
                temperature=0.3,
                max_tokens=20
            )

            intent = response.choices[0].message.content.strip().lower()
            return intent

        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return "other"

    async def _handle_intent(
        self,
        user_id: str,
        intent: str,
        message_text: str,
        state: Dict
    ) -> str:
        """Handle the detected intent and return appropriate response"""

        if intent == "greeting":
            state["stage"] = "greeted"
            return self.response_generator.greeting_response()

        elif intent == "booking_inquiry":
            # Extract preferred date/time if mentioned
            date_info = await self._extract_date_time(message_text)
            
            if date_info:
                # Provide available slots near requested time
                available_slots = self.booking_manager.get_available_slots(date_info)
                state["stage"] = "showing_availability"
                return self.response_generator.availability_response(available_slots)
            else:
                # Ask for preferred date/time
                state["stage"] = "asking_datetime"
                return self.response_generator.ask_datetime_response()

        elif intent == "confirm_booking" and state["stage"] in ["showing_availability", "awaiting_confirmation"]:
            # Extract confirmation and create booking
            confirmed_slot = await self._extract_confirmed_time(message_text, state)
            
            if confirmed_slot:
                booking_result = await self.booking_manager.create_booking(
                    user_id=user_id,
                    customer_name=state.get("customer_name", "Customer"),
                    appointment_time=confirmed_slot
                )
                
                if booking_result["success"]:
                    state["stage"] = "completed"
                    state["booking_data"] = booking_result
                    return self.response_generator.confirmation_response(
                        confirmed_slot,
                        booking_result.get("event_id")
                    )
                else:
                    return self.response_generator.booking_error_response()
            else:
                state["stage"] = "awaiting_confirmation"
                return self.response_generator.clarify_time_response()

        elif intent == "cancel_booking":
            # Handle cancellation
            state["stage"] = "cancelled"
            return self.response_generator.cancellation_response()

        elif intent == "general_question":
            # Use OpenAI to answer general questions
            answer = await self._answer_general_question(message_text, state["history"])
            return answer

        else:
            # Default fallback
            return self.response_generator.fallback_response()

    async def _extract_date_time(self, message_text: str) -> Optional[datetime]:
        """Extract date/time from user message using OpenAI"""
        
        system_prompt = """Extract the date and time from the user's message.
If no specific time is mentioned, assume they want afternoon (2 PM).
Return in format: YYYY-MM-DD HH:MM
If no date can be extracted, return "NONE"

Examples:
- "tomorrow at 3pm" -> 2025-11-02 15:00
- "next monday" -> (calculate next Monday) 14:00
- "this saturday morning" -> (calculate Saturday) 10:00
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Today is {datetime.now().strftime('%Y-%m-%d')}. Message: {message_text}"}
                ],
                temperature=0.3,
                max_tokens=50
            )

            result = response.choices[0].message.content.strip()
            
            if result == "NONE":
                return None
                
            # Parse the datetime
            return datetime.strptime(result, "%Y-%m-%d %H:%M")

        except Exception as e:
            logger.error(f"Error extracting date/time: {str(e)}")
            return None

    async def _extract_confirmed_time(self, message_text: str, state: Dict) -> Optional[datetime]:
        """Extract which time slot the user confirmed"""
        
        # This is a simplified version - you might want more sophisticated logic
        # to match user's confirmation to the slots you showed them
        
        message_lower = message_text.lower()
        if any(word in message_lower for word in ["yes", "confirm", "book", "that works", "sounds good"]):
            # Return the most recently proposed time
            # In a real implementation, you'd track the specific slots you showed
            return state.get("booking_data", {}).get("proposed_time")
        
        return None

    async def _answer_general_question(self, message_text: str, history: list) -> str:
        """Use OpenAI to answer general questions about the barbershop"""
        
        barber_name = os.getenv("BARBER_NAME", "our barber")
        
        system_prompt = f"""You are a helpful assistant for {barber_name}'s barbershop.
Answer questions about:
- Services: haircuts, trims, beard grooming, fades, lineups
- Typical prices: $30-50 depending on service
- General booking information
- Location: (mention they should ask for specific address)

Keep responses friendly, concise, and encourage booking an appointment.
If you don't know something specific, say so and offer to have them book a consultation."""

        try:
            # Use conversation history for context
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-4:])  # Last 4 messages for context

            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error answering general question: {str(e)}")
            return self.response_generator.fallback_response()

    def clear_conversation(self, user_id: str):
        """Clear conversation state for a user"""
        if user_id in self.conversation_state:
            del self.conversation_state[user_id]