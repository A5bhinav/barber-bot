import os
import random
from datetime import datetime
from typing import List, Dict, Optional


class ResponseGenerator:
    """Generates natural, friendly responses for different conversation stages"""

    def __init__(self):
        self.barber_name = os.getenv("BARBER_NAME", "our barber")

    def greeting_response(self) -> str:
        """Response to initial greeting"""
        greetings = [
            f"Hey! Thanks for reaching out. I'm here to help you book an appointment with {self.barber_name}. When would you like to come in?",
            f"What's up! Looking to book a cut with {self.barber_name}? Let me know what day works for you!",
            f"Hey there! Ready to get fresh? When are you looking to book an appointment?",
            f"Hello! I can help you schedule an appointment with {self.barber_name}. What day were you thinking?"
        ]
        return random.choice(greetings)

    def ask_datetime_response(self) -> str:
        """Ask user for preferred date and time"""
        responses = [
            "What day and time work best for you? Just let me know like 'tomorrow at 2pm' or 'next Monday morning'",
            "When would you like to come in? Give me a day and time, like 'Saturday at 3pm' or 'next week'",
            "What's your preferred day and time? I can check availability for you.",
            "When are you free? Let me know a day and time that works for you!"
        ]
        return random.choice(responses)

    def availability_response(self, available_slots: List[Dict]) -> str:
        """Show available time slots"""
        if not available_slots:
            return "Sorry, I'm not seeing any available slots right now. Could you try a different day or time?"

        response = "Here are the next available times:\n\n"
        for i, slot in enumerate(available_slots[:3], 1):
            response += f"{i}. {slot['formatted']}\n"

        response += "\nWhich one works for you? Just reply with the number or the time!"
        return response

    def confirmation_response(self, appointment_time: datetime, event_id: Optional[str] = None) -> str:
        """Confirm booking is complete"""
        formatted_time = appointment_time.strftime("%A, %B %d at %I:%M %p")
        
        confirmations = [
            f"✅ You're all set! Your appointment is confirmed for {formatted_time}. See you then!",
            f"🔥 Booked! You're scheduled for {formatted_time}. Looking forward to it!",
            f"✂️ Perfect! You're confirmed for {formatted_time}. We'll see you there!",
            f"📅 Done! Your appointment is locked in for {formatted_time}. Can't wait to see you!"
        ]
        
        response = random.choice(confirmations)
        
        # Add reminder info
        response += f"\n\nYou'll get a reminder before your appointment. If you need to cancel or reschedule, just let me know!"
        
        return response

    def booking_error_response(self) -> str:
        """Response when booking fails"""
        return "Oops, something went wrong creating your appointment. Can you try again? If this keeps happening, please DM us directly."

    def clarify_time_response(self) -> str:
        """Ask for clarification on the time"""
        responses = [
            "Just to confirm - which time slot did you want? Let me know the specific time!",
            "Which one of those times works for you? Just tell me the day and time you prefer.",
            "Can you confirm which time you'd like? Just let me know!",
        ]
        return random.choice(responses)

    def cancellation_response(self) -> str:
        """Response for cancellation request"""
        return "No problem! If you have an existing appointment you'd like to cancel, please send me the date and time. Or if you want to reschedule, just let me know when works better for you!"

    def fallback_response(self) -> str:
        """Fallback for unclear messages"""
        responses = [
            "Sorry, I didn't quite catch that. Are you looking to book an appointment? Let me know what day works for you!",
            "I want to make sure I help you right! Are you trying to book, reschedule, or cancel an appointment?",
            "Hmm, I'm not sure I understood. Want to book an appointment? Just tell me when you're free!",
        ]
        return random.choice(responses)

    def out_of_hours_response(self) -> str:
        """Response when user requests time outside business hours"""
        start = os.getenv("BARBER_BUSINESS_HOURS_START", "9:00 AM")
        end = os.getenv("BARBER_BUSINESS_HOURS_END", "6:00 PM")
        
        return f"We're typically open from {start} to {end}. Can you choose a time during those hours?"

    def service_info_response(self) -> str:
        """General service information"""
        return f"""Here's what {self.barber_name} offers:

✂️ Haircuts - Full service cuts
🧔 Beard Trims & Grooming
🔥 Fades & Tapers
✨ Lineups & Edge-ups

Prices typically range from $30-50 depending on the service.

Want to book an appointment? Let me know when you're free!"""

    def waiting_response(self) -> str:
        """Acknowledgment while processing"""
        responses = [
            "One sec, let me check that for you...",
            "Checking the schedule...",
            "Give me just a moment...",
        ]
        return random.choice(responses)