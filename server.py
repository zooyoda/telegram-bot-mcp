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

# Применяем патч для поддержки вложенных event loops
nest_asyncio.apply()

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация MCP
mcp = FastMCP(
    name="Telegram Bot API MCP",
    description="MCP для работы с Telegram Bot API. Предоставляет функции для отправки и получения сообщений через Telegram бота.",
    version="1.0.0",
    author="MCP Developer",
)

# Глобальные переменные
bot_instance = None


def get_bot():
    """Получает экземпляр бота, инициализируя его при необходимости."""
    global bot_instance
    
    if bot_instance is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not token:
            raise ValueError("Токен бота не найден. Установите переменную окружения TELEGRAM_BOT_TOKEN в .env файле.")
        
        # Создаем Bot напрямую вместо использования Updater
        bot_instance = Bot(token)
    
    return bot_instance


# Вспомогательная функция для запуска асинхронных задач
def run_async(coro):
    """Запускает асинхронную корутину в текущем event loop."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@mcp.tool("sendMessage")
def sendMessage(chatId: Union[str, int], text: str) -> Dict[str, Any]:
    """
    Отправляет текстовое сообщение в указанный чат.
    
    Параметры:
    - chatId: ID чата, куда отправить сообщение (строка или число)
    - text: Текст сообщения для отправки
    
    Возвращает:
    - Информацию об отправленном сообщении
    """
    try:
        bot = get_bot()
        # Запускаем асинхронный метод в текущем event loop
        message = run_async(bot.send_message(chat_id=chatId, text=text))
        return {
            "success": True,
            "message_id": message.message_id,
            "date": message.date.timestamp() if message.date else None,
            "chat_id": message.chat_id
        }
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("sendPhoto")
def sendPhoto(chatId: Union[str, int], photoUrl: str, caption: Optional[str] = None) -> Dict[str, Any]:
    """
    Отправляет фото в указанный чат.
    
    Параметры:
    - chatId: ID чата, куда отправить фото (строка или число)
    - photoUrl: URL фотографии или путь к локальному файлу
    - caption: Подпись к фотографии (опционально)
    
    Возвращает:
    - Информацию об отправленном фото
    """
    try:
        bot = get_bot()
        
        # Проверяем, это URL или локальный файл
        if photoUrl.startswith(('http://', 'https://')):
            photo = photoUrl
        else:
            if os.path.exists(photoUrl):
                photo = InputFile(photoUrl)
            else:
                return {
                    "success": False,
                    "error": f"Файл не найден: {photoUrl}"
                }
        
        # Запускаем асинхронный метод в текущем event loop
        message = run_async(bot.send_photo(chat_id=chatId, photo=photo, caption=caption))
        return {
            "success": True,
            "message_id": message.message_id,
            "date": message.date.timestamp() if message.date else None,
            "chat_id": message.chat_id
        }
    except Exception as e:
        logger.error(f"Ошибка при отправке фото: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("deleteMessage")
def deleteMessage(chatId: Union[str, int], messageId: int) -> Dict[str, Any]:
    """
    Удаляет сообщение из чата.
    
    Параметры:
    - chatId: ID чата, из которого нужно удалить сообщение (строка или число)
    - messageId: ID сообщения, которое нужно удалить (число)
    
    Возвращает:
    - Статус операции
    """
    try:
        bot = get_bot()
        # Запускаем асинхронный метод в текущем event loop
        result = run_async(bot.delete_message(chat_id=chatId, message_id=messageId))
        return {
            "success": True if result else False
        }
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("getMe")
def getMe() -> Dict[str, Any]:
    """
    Получает информацию о боте.
    
    Возвращает:
    - Информацию о боте (ID, имя, username и т.д.)
    """
    try:
        bot = get_bot()
        # Запускаем асинхронный метод в текущем event loop
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
        logger.error(f"Ошибка при получении информации о боте: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool("getUpdates")
def getUpdates(offset: Optional[int] = None, limit: int = 100, timeout: int = 0) -> Dict[str, Any]:
    """
    Получает обновления (сообщения, события) от Telegram Bot API.
    
    Параметры:
    - offset: ID первого обновления, которое нужно вернуть (опционально)
    - limit: Максимальное количество обновлений для возврата (по умолчанию 100)
    - timeout: Таймаут в секундах (по умолчанию 0)
    
    Возвращает:
    - Список обновлений
    """
    try:
        bot = get_bot()
        # Запускаем асинхронный метод в текущем event loop
        updates = run_async(bot.get_updates(offset=offset, limit=limit, timeout=timeout))
        return {
            "success": True,
            "updates": [update.to_dict() for update in updates]
        }
    except Exception as e:
        logger.error(f"Ошибка при получении обновлений: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    # Запускаем MCP сервер
    mcp.run()


if __name__ == "__main__":
    main() 