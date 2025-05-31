import os
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError

class TelegramManager:
    """
    Manages communication with Telegram to send charts and notifications.
    """
    def __init__(self, token, chat_id=None):
        """
        Initialize the Telegram manager.
        
        Args:
            token (str): The Telegram bot token obtained from BotFather
            chat_id (str, optional): Default chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        self._loop = None
        logging.info("Telegram bot initialized")
        
    async def send_message(self, message, chat_id=None):
        """
        Send a text message to a Telegram chat.
        
        Args:
            message (str): The message to send
            chat_id (str, optional): Override the default chat ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logging.error("No chat ID provided for message delivery")
            return False
            
        try:
            # Send the message asynchronously
            await self.bot.send_message(chat_id=target_chat_id, text=message)
            logging.info(f"Message sent to Telegram chat {target_chat_id}")
            return True
        except TelegramError as e:
            logging.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending message: {str(e)}")
            return False
    
    async def send_chart(self, chart_path, caption=None, chat_id=None):
        """
        Send a chart image to a Telegram chat.
        
        Args:
            chart_path (str): Path to the chart image file
            caption (str, optional): Caption for the image
            chat_id (str, optional): Override the default chat ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logging.error("No chat ID provided for chart delivery")
            return False
            
        if not os.path.exists(chart_path):
            logging.error(f"Chart file not found: {chart_path}")
            return False
            
        try:
            with open(chart_path, 'rb') as chart:
                # Send the photo asynchronously
                await self.bot.send_photo(
                    chat_id=target_chat_id,
                    photo=chart,
                    caption=caption
                )
            logging.info(f"Chart sent to Telegram chat {target_chat_id}")
            return True
        except TelegramError as e:
            logging.error(f"Failed to send chart to Telegram: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending chart: {str(e)}")
            return False
            
    async def send_stock_analysis(self, symbol, chart_path, analysis_text=None):
        """
        Send a complete stock analysis with chart and text.
        
        Args:
            symbol (str): Stock symbol
            chart_path (str): Path to the chart image
            analysis_text (str, optional): Additional analysis text
            
        Returns:
            bool: True if successful, False otherwise
        """
        caption = f"Stock Analysis: {symbol}"
        if analysis_text:
            caption += f"\n\n{analysis_text}"
            
        return await self.send_chart(chart_path, caption)

def create_telegram_manager(config):
    """
    Create a TelegramManager instance from configuration.
    
    Args:
        config (dict): Configuration containing Telegram settings
        
    Returns:
        TelegramManager or None: Initialized manager or None if configuration is invalid
    """
    if 'telegram' not in config or 'token' not in config['telegram']:
        logging.error("Telegram configuration missing required fields")
        return None
        
    token = config['telegram']['token']
    chat_id = config['telegram'].get('chat_id')
    
    # Check for None or placeholder values
    if not token or token in ['YOUR_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE']:
        logging.error("Telegram bot token is not properly configured")
        return None
        
    if not chat_id or chat_id in ['YOUR_CHAT_ID', 'YOUR_CHAT_ID_HERE']:
        logging.error("Telegram chat ID is not properly configured")
        return None
    
    return TelegramManager(token, chat_id) 