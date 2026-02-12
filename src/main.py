"""
Main application entry point following SOLID principles
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

from .core.interfaces.repositories import ITaskRepository, IUserRepository
from .core.interfaces.services import INotificationService
from .infrastructure.repositories.mongodb_task_repository import MongoTaskRepository
from .infrastructure.repositories.mongodb_user_repository import MongoUserRepository
from .presentation.handlers.task_handler import TaskHandler
from .database.config import get_database, connect_to_mongo, disconnect_from_mongo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockNotificationService(INotificationService):
    """Mock notification service for testing"""
    
    async def send_deadline_notification(self, user, task) -> bool:
        logger.info(f"📱 Mock deadline notification to {user.full_name}: {task.title}")
        return True
    
    async def send_task_update_notification(self, user, task, message) -> bool:
        logger.info(f"📱 Mock task update to {user.full_name}: {message}")
        return True
    
    async def send_daily_summary(self, user, tasks) -> bool:
        logger.info(f"📱 Mock daily summary to {user.full_name}: {len(tasks)} tasks")
        return True

class StudentLifeHelperBot:
    """
    Main bot class following SOLID principles:
    - Single Responsibility: Coordinates bot components
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Can replace any bot implementation
    - Interface Segregation: Depends only on needed interfaces
    - Dependency Inversion: Depends on abstractions
    """
    
    def __init__(self, token: str):
        self.token = token
        self.database = None
        self.task_repository = None
        self.user_repository = None
        self.notification_service = None
        self.task_handler = None
    
    async def initialize(self) -> bool:
        """Initialize bot components"""
        try:
            # Connect to database
            connected = await connect_to_mongo()
            if not connected:
                return False
            
            # Get database
            self.database = await get_database()
            
            # Initialize repositories (Dependency Inversion)
            self.task_repository = MongoTaskRepository(self.database)
            self.user_repository = MongoUserRepository(self.database)
            
            # Initialize services (Dependency Inversion)
            self.notification_service = MockNotificationService()
            
            # Initialize handlers (Dependency Inversion)
            self.task_handler = TaskHandler(
                self.task_repository,
                self.user_repository,
                self.notification_service
            )
            
            logger.info("✅ Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    async def run(self) -> None:
        """Run the bot"""
        if not await self.initialize():
            return
        
        # Create telegram application
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler
        
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.task_handler.handle_start_command))
        application.add_handler(CommandHandler("help", self.task_handler.handle_help_command))
        application.add_handler(CommandHandler("tasks", self.task_handler.handle_tasks_command))
        application.add_handler(CommandHandler("add_task", self.task_handler.handle_add_task_command))
        application.add_handler(CommandHandler("deadline", self.task_handler.handle_deadline_command))
        application.add_handler(CommandHandler("search", self.task_handler.handle_search_command))
        application.add_handler(CommandHandler("edit", self.task_handler.handle_edit_command))
        application.add_handler(CommandHandler("edit_task", self.task_handler.handle_edit_task_command))
        
        # Add callback handlers
        from telegram.ext import MessageHandler, filters
        application.add_handler(CallbackQueryHandler(self.task_handler.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.task_handler.handle_message))
        
        logger.info("🤖 Starting Student Life Helper Bot...")
        
        try:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
            # Set bot menu commands
            from telegram import BotCommand
            await application.bot.set_my_commands([
                BotCommand("tasks", "View all your tasks"),
                BotCommand("add_task", "Add a new task"),
                BotCommand("deadline", "View upcoming deadlines"),
                BotCommand("search", "Search tasks"),
                BotCommand("edit", "Edit a task"),
                BotCommand("help", "Show available commands"),
            ])
            
            logger.info("✅ Bot is running! Press Ctrl+C to stop.")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("👋 Shutting down bot...")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the bot"""
        try:
            # Disconnect from database
            await disconnect_from_mongo()
            logger.info("✅ Bot shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

async def main():
    """Main function"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get bot token
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            logger.info("💡 Please set TELEGRAM_BOT_TOKEN in your .env file")
            return
        
        # Create and run bot
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
