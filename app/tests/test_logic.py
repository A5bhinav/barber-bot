import pytest
from datetime import datetime, timedelta
from logic.responses import ResponseGenerator
from logic.booking import BookingManager
from services.calendar import CalendarService


class TestResponseGenerator:
    """Test response generation"""

    def test_greeting_response(self):
        generator = ResponseGenerator()
        response = generator.greeting_response()
        assert len(response) > 0
        assert isinstance(response, str)

    def test_availability_response_with_slots(self):
        generator = ResponseGenerator()
        slots = [
            {
                "datetime": datetime.now() + timedelta(days=1),
                "formatted": "Monday, November 4 at 02:00 PM",
                "short": "Mon 11/04 at 02:00PM"
            }
        ]
        response = generator.availability_response(slots)
        assert "Monday, November 4 at 02:00 PM" in response

    def test_availability_response_empty_slots(self):
        generator = ResponseGenerator()
        response = generator.availability_response([])
        assert "not seeing any available" in response.lower()

    def test_confirmation_response(self):
        generator = ResponseGenerator()
        test_time = datetime(2025, 11, 5, 14, 0)
        response = generator.confirmation_response(test_time)
        assert "confirmed" in response.lower() or "set" in response.lower()
        assert "November" in response


class TestBookingManager:
    """Test booking manager logic"""

    def test_is_business_hours(self):
        # Mock calendar service for testing
        calendar_service = CalendarService()
        booking_manager = BookingManager(calendar_service)
        
        # Test during business hours (2 PM)
        test_time = datetime.now().replace(hour=14, minute=0)
        assert booking_manager.is_business_hours(test_time) == True
        
        # Test outside business hours (8 PM)
        test_time = datetime.now().replace(hour=20, minute=0)
        assert booking_manager.is_business_hours(test_time) == False


# Run tests with: pytest app/tests/test_logic.py -v