from mcp.server.fastmcp import FastMCP
import os
import logging
import asyncio
import nest_asyncio
from typing import Dict, Any, Optional, List, Union
from telegram import Bot, Update, InputFile, Message
from telegram.error import TelegramError
from telegram.ext import Updater
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Apply patch for nested event loops support
nest_asyncio.apply()

# Load environment variables
load_dotenv()

logger.info("TOKEN_PRESENT:", os.getenv("TELEGRAM_BOT_TOKEN") is not None)

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# MCP initialization
mcp = FastMCP(
    name="Telegram Bot API MCP",
    description="MCP for working with Telegram Bot API. Provides functions for sending and receiving messages through Telegram bot.",
    version="1.0.0",
    author="MCP Developer",
)

# Global variables
bot_instance = None


def get_bot():
    """Gets bot instance, initializing it if necessary."""
    global bot_instance
    
    if bot_instance is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not token:
            raise ValueError("Bot token not found. Set the TELEGRAM_BOT_TOKEN environment variable in the .env file.")
        
        # Create Bot directly instead of using Updater
        bot_instance = Bot(token)
    
    return bot_instance


# Helper function for running async tasks
def run_async(coro):
    """Runs an async coroutine in the current event loop."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@mcp.tool("sendMessage")
def sendMessage(chatId: str, text: str) -> Dict[str, Any]:
    """
    Sends a text message to the specified chat.
    
    Parameters:
    - chatId: Chat ID where to send the message (string)
    - text: Message text to send
    
    Returns:
    - Information about the sent message
    """
    try:
        bot = get_bot()
        # Run async method in current event loop
        message = run_async(bot.send_message(chat_id=chatId, text=text))
        return {
            "success": True,
            "message_id": message.message_id,
            "date": message.date.timestamp() if message.date else None,
            "chat_id": message.chat_id
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("sendPhoto")
def sendPhoto(chatId: str, photoUrl: str, caption: Optional[str] = None) -> Dict[str, Any]:
    """
    Sends a photo to the specified chat.
    
    Parameters:
    - chatId: Chat ID where to send the photo (string)
    - photoUrl: Photo URL or path to local file
    - caption: Photo caption (optional)
    
    Returns:
    - Information about the sent photo
    """
    try:
        bot = get_bot()
        
        # Check if it's a URL or local file
        if photoUrl.startswith(('http://', 'https://')):
            photo = photoUrl
        else:
            if os.path.exists(photoUrl):
                photo = InputFile(photoUrl)
            else:
                return {
                    "success": False,
                    "error": f"File not found: {photoUrl}"
                }
        
        # Run async method in current event loop
        message = run_async(bot.send_photo(chat_id=chatId, photo=photo, caption=caption))
        return {
            "success": True,
            "message_id": message.message_id,
            "date": message.date.timestamp() if message.date else None,
            "chat_id": message.chat_id
        }
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("deleteMessage")
def deleteMessage(chatId: str, messageId: int) -> Dict[str, Any]:
    """
    Deletes a message from the chat.
    
    Parameters:
    - chatId: Chat ID from which to delete the message (string)
    - messageId: Message ID to delete (number)
    
    Returns:
    - Operation status
    """
    try:
        bot = get_bot()
        # Run async method in current event loop
        result = run_async(bot.delete_message(chat_id=chatId, message_id=messageId))
        return {
            "success": True if result else False
        }
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("getMe")
def getMe() -> Dict[str, Any]:
    """
    Gets information about the bot.
    
    Returns:
    - Bot information (ID, name, username, etc.)
    """
    try:
        bot = get_bot()
        # Run async method in current event loop
        me = run_async(bot.get_me())
        return {
            "success": True,
            "id": me.id,
            "first_name": me.first_name,
            "username": me.username,
            "is_bot": me.is_bot,
            "can_join_groups": me.can_join_groups,
            "can_read_all_group_messages": me.can_read_all_group_messages,
            "supports_inline_queries": me.supports_inline_queries
        }
    except Exception as e:
        logger.error(f"Error getting bot information: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("getUpdates")
def getUpdates(offset: Optional[int] = None, limit: int = 100, timeout: int = 0) -> Dict[str, Any]:
    """
    Gets updates (messages, events) from Telegram Bot API.
    
    Parameters:
    - offset: ID of the first update to return (optional)
    - limit: Maximum number of updates to return (default 100)
    - timeout: Timeout in seconds (default 0)
    
    Returns:
    - List of updates
    """
    try:
        bot = get_bot()
        # Run async method in current event loop
        updates = run_async(bot.get_updates(offset=offset, limit=limit, timeout=timeout))
        return {
            "success": True,
            "updates": [update.to_dict() for update in updates]
        }
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    # Run MCP server
    mcp.run()


if __name__ == "__main__":
    main() 
