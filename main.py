"""
Main entry point for Student Life Helper Bot
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to initialize and run the bot"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get bot token
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            logger.info("💡 Please set TELEGRAM_BOT_TOKEN in your .env file")
            return
        
        # Import and run the SOLID bot
        from src.main import StudentLifeHelperBot
        
        # Create and run bot
        logger.info("🤖 Starting Student Life Helper Bot (SOLID Architecture)...")
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
