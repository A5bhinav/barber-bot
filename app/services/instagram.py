import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InstagramService:
    """Service for interacting with Instagram Graph API"""

    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.page_id = os.getenv("INSTAGRAM_PAGE_ID")
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        if not self.access_token or not self.page_id:
            logger.warning("Instagram credentials not fully configured")

    async def send_message(self, recipient_id: str, message_text: str) -> bool:
        """
        Send a message to an Instagram user via DM
        
        Args:
            recipient_id: The Instagram user ID (IGSID)
            message_text: The message to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                
                logger.info(f"Message sent successfully to {recipient_id}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to send message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return False

    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """
        Get user profile information
        
        Args:
            user_id: The Instagram user ID
            
        Returns:
            dict: User profile data or None if failed
        """
        url = f"{self.base_url}/{user_id}"
        params = {
            "fields": "name,username,profile_pic",
            "access_token": self.access_token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            return None

    async def reply_to_comment(self, comment_id: str, message_text: str) -> bool:
        """
        Reply to an Instagram comment
        
        Args:
            comment_id: The comment ID
            message_text: The reply text
            
        Returns:
            bool: True if reply sent successfully
        """
        url = f"{self.base_url}/{comment_id}/replies"
        
        payload = {
            "message": message_text,
            "access_token": self.access_token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                response.raise_for_status()
                
                logger.info(f"Replied to comment {comment_id}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to reply to comment: {str(e)}")
            return False