import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for managing Google Calendar appointments"""

    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", "credentials.json")
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Calendar API service"""
        try:
            # Use service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized successfully")
        except FileNotFoundError:
            logger.warning(f"Credentials file not found at {self.credentials_path}. Calendar features will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {str(e)}")

    def create_appointment(
        self,
        customer_name: str,
        customer_contact: str,
        start_time: datetime,
        duration_minutes: int = 60,
        service_type: str = "Haircut"
    ) -> Optional[str]:
        """
        Create a new appointment in Google Calendar
        
        Args:
            customer_name: Name of the customer
            customer_contact: Contact info (Instagram username or ID)
            start_time: Appointment start time
            duration_minutes: Duration of appointment
            service_type: Type of service (Haircut, Trim, etc.)
            
        Returns:
            str: Event ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Calendar service not initialized")
            return None

        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            'summary': f'{service_type} - {customer_name}',
            'description': f'Customer: {customer_name}\nContact: @{customer_contact}\nService: {service_type}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Adjust to your timezone
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        try:
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            logger.info(f"Appointment created: {event.get('htmlLink')}")
            return event.get('id')

        except HttpError as e:
            logger.error(f"Failed to create appointment: {str(e)}")
            return None

    def get_available_slots(
        self,
        date: datetime,
        business_hours_start: str = "09:00",
        business_hours_end: str = "18:00",
        slot_duration_minutes: int = 60
    ) -> List[datetime]:
        """
        Get available time slots for a given date
        Supports split schedules (e.g., morning and evening hours)
        
        Args:
            date: The date to check availability
            business_hours_start: Start of business hours (HH:MM or HH:MM;HH:MM for split schedule)
            business_hours_end: End of business hours (HH:MM or HH:MM;HH:MM for split schedule)
            slot_duration_minutes: Duration of each slot
            
        Returns:
            List of available datetime slots
        """
        if not self.service:
            logger.warning("Calendar service not initialized, returning empty slots")
            return []

        # Parse business hours - support split schedules
        start_times = business_hours_start.split(';')
        end_times = business_hours_end.split(';')
        
        if len(start_times) != len(end_times):
            logger.error("Mismatched business hours configuration")
            return []
        
        # Create time blocks
        time_blocks = []
        for start_str, end_str in zip(start_times, end_times):
            start_hour, start_minute = map(int, start_str.strip().split(':'))
            end_hour, end_minute = map(int, end_str.strip().split(':'))
            
            block_start = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            block_end = date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            time_blocks.append((block_start, block_end))
        
        # Use the first block for API query bounds (will filter by blocks later)
        day_start = time_blocks[0][0]
        day_end = time_blocks[-1][1]

        try:
            # Get existing events for the day
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=day_start.isoformat() + 'Z',
                timeMax=day_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Generate all possible slots across all time blocks
            all_slots = []
            for block_start, block_end in time_blocks:
                current_slot = block_start
                while current_slot + timedelta(minutes=slot_duration_minutes) <= block_end:
                    all_slots.append(current_slot)
                    current_slot += timedelta(minutes=slot_duration_minutes)

            # Remove slots that conflict with existing events
            available_slots = []
            for slot in all_slots:
                slot_end = slot + timedelta(minutes=slot_duration_minutes)
                is_available = True

                for event in events:
                    event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))

                    # Check if slot conflicts with event
                    if (slot < event_end and slot_end > event_start):
                        is_available = False
                        break

                if is_available:
                    available_slots.append(slot)

            return available_slots

        except HttpError as e:
            logger.error(f"Failed to get available slots: {str(e)}")
            return []

    def cancel_appointment(self, event_id: str) -> bool:
        """
        Cancel an appointment
        
        Args:
            event_id: The Google Calendar event ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            logger.error("Calendar service not initialized")
            return False

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"Appointment {event_id} cancelled")
            return True

        except HttpError as e:
            logger.error(f"Failed to cancel appointment: {str(e)}")
            return False

    def get_appointment(self, event_id: str) -> Optional[Dict]:
        """
        Get appointment details
        
        Args:
            event_id: The Google Calendar event ID
            
        Returns:
            dict: Event details or None if not found
        """
        if not self.service:
            logger.error("Calendar service not initialized")
            return None

        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            return event

        except HttpError as e:
            logger.error(f"Failed to get appointment: {str(e)}")
            return None