import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services.calendar import CalendarService

logger = logging.getLogger(__name__)


class BookingManager:
    """Manages booking logic and coordinates with calendar service"""

    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
        self.business_hours_start = os.getenv("BARBER_BUSINESS_HOURS_START", "09:00")
        self.business_hours_end = os.getenv("BARBER_BUSINESS_HOURS_END", "18:00")
        self.appointment_duration = int(os.getenv("APPOINTMENT_DURATION_MINUTES", "60"))

    def get_available_slots(
        self,
        requested_date: datetime,
        num_days: int = 3
    ) -> List[Dict[str, str]]:
        """
        Get available appointment slots starting from requested date
        
        Args:
            requested_date: Starting date to check availability
            num_days: Number of days to check
            
        Returns:
            List of available slots with formatted strings
        """
        available_slots = []

        for day_offset in range(num_days):
            check_date = requested_date + timedelta(days=day_offset)
            
            # Skip if it's in the past
            if check_date.date() < datetime.now().date():
                continue

            # Get slots for this day
            day_slots = self.calendar_service.get_available_slots(
                check_date,
                self.business_hours_start,
                self.business_hours_end,
                self.appointment_duration
            )

            for slot in day_slots:
                # Only show slots that are in the future
                if slot > datetime.now():
                    available_slots.append({
                        "datetime": slot,
                        "formatted": slot.strftime("%A, %B %d at %I:%M %p"),
                        "short": slot.strftime("%a %m/%d at %I:%M%p")
                    })

        return available_slots[:5]  # Return top 5 slots

    async def create_booking(
        self,
        user_id: str,
        customer_name: str,
        appointment_time: datetime,
        service_type: str = "Haircut"
    ) -> Dict:
        """
        Create a new booking
        
        Args:
            user_id: Instagram user ID
            customer_name: Customer's name
            appointment_time: Scheduled appointment time
            service_type: Type of service
            
        Returns:
            dict: Booking result with success status and event_id
        """
        # Validate the time is still available
        check_date = appointment_time.replace(hour=0, minute=0, second=0, microsecond=0)
        available_slots = self.calendar_service.get_available_slots(
            check_date,
            self.business_hours_start,
            self.business_hours_end,
            self.appointment_duration
        )

        # Check if requested time is still available
        is_available = any(
            abs((slot - appointment_time).total_seconds()) < 60
            for slot in available_slots
        )

        if not is_available:
            logger.warning(f"Requested time {appointment_time} is no longer available")
            return {
                "success": False,
                "error": "time_not_available",
                "message": "Sorry, that time slot is no longer available."
            }

        # Create the calendar event
        event_id = self.calendar_service.create_appointment(
            customer_name=customer_name,
            customer_contact=user_id,
            start_time=appointment_time,
            duration_minutes=self.appointment_duration,
            service_type=service_type
        )

        if event_id:
            logger.info(f"Booking created for {customer_name} at {appointment_time}")
            return {
                "success": True,
                "event_id": event_id,
                "appointment_time": appointment_time,
                "customer_name": customer_name,
                "service_type": service_type
            }
        else:
            logger.error("Failed to create calendar event")
            return {
                "success": False,
                "error": "calendar_error",
                "message": "Sorry, there was an error creating your appointment."
            }

    def cancel_booking(self, event_id: str) -> bool:
        """Cancel an existing booking"""
        return self.calendar_service.cancel_appointment(event_id)

    def is_business_hours(self, check_time: datetime) -> bool:
        """Check if a given time falls within business hours (supports split schedules)"""
        start_times = self.business_hours_start.split(';')
        end_times = self.business_hours_end.split(';')
        
        time_minutes = check_time.hour * 60 + check_time.minute
        
        # Check if time falls in any of the business hour blocks
        for start_str, end_str in zip(start_times, end_times):
            start_hour, start_minute = map(int, start_str.strip().split(':'))
            end_hour, end_minute = map(int, end_str.strip().split(':'))
            
            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute
            
            if start_minutes <= time_minutes < end_minutes:
                return True
        
        return False