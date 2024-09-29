from abc import ABC, abstractmethod
import telegram
import asyncio

class MessageStrategy(ABC):
    @abstractmethod
    async def send_message(self, bot, chat_id):
        pass

class TextMessage(MessageStrategy):
    def __init__(self, text):
        self.text = text

    async def send_message(self, bot, chat_id):
        await bot.send_message(chat_id=chat_id, text=self.text)

class ImageMessage(MessageStrategy):
    def __init__(self, photo_url, caption=None):
        self.photo_url = photo_url
        self.caption = caption

    async def send_message(self, bot, chat_id):
        await bot.send_photo(chat_id=chat_id, photo=self.photo_url, caption=self.caption)

class MessageContext:
    def __init__(self, strategy: MessageStrategy, bot_token: str):
        self._strategy = strategy
        self._bot_token = bot_token

    async def execute_send(self, chat_id):
        bot = telegram.Bot(self._bot_token)
        await self._strategy.send_message(bot, chat_id)

async def send_notifications_to_multiple_chats(strategy, bot_token, chat_ids):
    tasks = [MessageContext(strategy, bot_token).execute_send(chat_id) for chat_id in chat_ids]
    await asyncio.gather(*tasks)

# Synchronous function to trigger async calls
def send_notifications(strategy, bot_token, chat_ids):
    asyncio.run(send_notifications_to_multiple_chats(strategy, bot_token, chat_ids))