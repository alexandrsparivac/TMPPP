import asyncio
import logging
import os
from dotenv import load_dotenv

from .models.repositories import ITaskRepository, IUserRepository
from .repositories.mongodb_task_repository import MongoTaskRepository
from .repositories.mongodb_user_repository import MongoUserRepository
from .handlers.task_handler import TaskHandler
from .database.config import get_database, connect_to_mongo, disconnect_from_mongo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StudentLifeHelperBot:

    def __init__(self, token: str):
        self.token = token
        self.database = None
        self.task_repository = None
        self.user_repository = None
        self.task_handler = None

    async def initialize(self) -> bool:
        try:
            connected = await connect_to_mongo()
            if not connected:
                return False

            self.database = await get_database()

            self.task_repository = MongoTaskRepository(self.database)
            self.user_repository = MongoUserRepository(self.database)

            self.task_handler = TaskHandler(
                self.task_repository,
                self.user_repository
            )

            logger.info("✅ Bot initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False

    async def run(self) -> None:
        if not await self.initialize():
            return

        from telegram.ext import Application, CommandHandler, CallbackQueryHandler

        application = Application.builder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.task_handler.handle_start_command))
        application.add_handler(CommandHandler("help", self.task_handler.handle_help_command))
        application.add_handler(CommandHandler("tasks", self.task_handler.handle_tasks_command))
        application.add_handler(CommandHandler("add_task", self.task_handler.handle_add_task_command))
        application.add_handler(CommandHandler("deadline", self.task_handler.handle_deadline_command))
        application.add_handler(CommandHandler("search", self.task_handler.handle_search_command))

        from telegram.ext import MessageHandler, filters
        application.add_handler(CallbackQueryHandler(self.task_handler.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.task_handler.handle_message))

        logger.info("🤖 Starting Student Life Helper Bot...")

        try:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()

            from telegram import BotCommand
            await application.bot.set_my_commands([
                BotCommand("tasks", "View all your tasks"),
                BotCommand("add_task", "Add a new task"),
                BotCommand("deadline", "View upcoming deadlines"),
                BotCommand("search", "Search tasks"),
                BotCommand("help", "Show available commands"),
            ])

            logger.info("✅ Bot is running! Press Ctrl+C to stop.")

            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("👋 Shutting down bot...")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        try:
            await disconnect_from_mongo()
            logger.info("✅ Bot shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

async def main():
    try:
        load_dotenv()

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            return

        bot = StudentLifeHelperBot(token)
        await bot.run()

    except KeyboardInterrupt:
        logger.info("👋 Shutting down bot...")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
