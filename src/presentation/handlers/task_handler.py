"""
Telegram Task Handler following SOLID principles
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from ...core.entities.task import Task, TaskStatus, TaskType, TaskPriority
from ...core.entities.user import User
from ...application.use_cases.task_use_cases import (
    CreateTaskUseCase,
    UpdateTaskUseCase,
    DeleteTaskUseCase,
    GetTasksUseCase
)
from ...core.interfaces.repositories import ITaskRepository, IUserRepository
from ...core.interfaces.services import INotificationService

from ...presentation.handlers.i18n import get_text, get_language_name

logger = logging.getLogger(__name__)

class TaskHandler:
    """
    Telegram task handler following SOLID principles:
    - Single Responsibility: Only handles Telegram task commands
    - Open/Closed: Can be extended with new commands
    - Liskov Substitution: Can replace any task handler
    - Interface Segregation: Depends only on needed interfaces
    - Dependency Inversion: Depends on abstractions
    """
    
    def __init__(
        self,
        task_repository: ITaskRepository,
        user_repository: IUserRepository,
        notification_service: INotificationService
    ):
        self._task_repository = task_repository
        self._user_repository = user_repository
        self._notification_service = notification_service
        
        # Initialize use cases
        self._create_task_use_case = CreateTaskUseCase(
            task_repository, notification_service
        )
        self._update_task_use_case = UpdateTaskUseCase(
            task_repository, notification_service
        )
        self._delete_task_use_case = DeleteTaskUseCase(
            task_repository, notification_service
        )
        self._get_tasks_use_case = GetTasksUseCase(task_repository)
    
    def _get_main_keyboard(self):
        """Create persistent reply keyboard with main commands"""
        keyboard = [
            [KeyboardButton("📋 Tasks"), KeyboardButton("➕ Add Task")],
            [KeyboardButton("📅 Deadlines"), KeyboardButton("🔍 Search"), KeyboardButton("❓ Help")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    
    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            user = update.effective_user
            
            # Check if user exists
            existing_user = await self._user_repository.get_by_telegram_id(user.id)
            
            if not existing_user:
                # Auto-create user with English
                from ...core.entities.user import UserPreferences
                
                new_user = User(
                    telegram_id=user.id,
                    username=user.username or "",
                    full_name=user.full_name or user.username or "",
                    preferences=UserPreferences(language='en')
                )
                
                user_id = await self._user_repository.create(new_user)
                new_user.id = user_id
                
                welcome_text = f"👋 Welcome, {new_user.full_name}!\n\n🤖 Ready to help!\n💡 Type /help for commands."
                await update.message.reply_text(welcome_text, reply_markup=self._get_main_keyboard())
                
                logger.info(f"✅ New user created: {new_user.full_name}")
            else:
                await update.message.reply_text(
                    f"👋 Welcome back, {existing_user.full_name}!\n\n🤖 Ready to help!\n💡 Type /help for commands.",
                    reply_markup=self._get_main_keyboard()
                )
                
        except Exception as e:
            logger.error(f"❌ Error in start command: {e}")
            await update.message.reply_text("❌ An error occurred. Please try again.")
    
    async def _handle_language_selection(self, update: Update, query, lang_code: str) -> None:
        """Handle language selection from keyboard (legacy)"""
        try:
            user = update.effective_user
            lang_code = 'en'
            
            from ...core.entities.user import UserPreferences
            
            new_user = User(
                telegram_id=user.id,
                username=user.username or "",
                full_name=user.full_name or user.username or "",
                preferences=UserPreferences(language=lang_code)
            )
            
            user_id = await self._user_repository.create(new_user)
            new_user.id = user_id
            
            await query.edit_message_text(
                f"👋 Welcome, {new_user.full_name}!\n\n🤖 Ready to help!\n💡 Type /help for commands."
            )
            
            logger.info(f"✅ User created")
            
        except Exception as e:
            logger.error(f"❌ Error in language selection: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        try:
            help_text = get_text('help_text', 'en')
            await update.message.reply_text(help_text)
            
        except Exception as e:
            logger.error(f"❌ Error in help command: {e}")
            await update.message.reply_text("❌ An error occurred.")
    
    async def handle_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /tasks command"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Get tasks using use case
            tasks = await self._get_tasks_use_case.execute(user)
            
            if not tasks:
                await update.message.reply_text("📝 You have no tasks. Use /add_task to add one!")
                return
            
            await update.message.reply_text(f"📋 **Your tasks ({len(tasks)}):**")
            
            # Send each task as a separate message with inline buttons
            for task in tasks[:10]:
                status_emoji = {
                    TaskStatus.TODO: "⏳",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.CANCELLED: "❌"
                }
                priority_emoji = {
                    TaskPriority.LOW: "🟢",
                    TaskPriority.MEDIUM: "🟡",
                    TaskPriority.HIGH: "🟠",
                    TaskPriority.URGENT: "🔴"
                }
                
                task_text = f"{status_emoji[task.status]} {priority_emoji[task.priority]} **{task.title}**\n"
                if task.description:
                    task_text += f"📝 {task.description[:80]}{'...' if len(task.description) > 80 else ''}\n"
                if task.deadline:
                    task_text += f"📅 {task.deadline.strftime('%d %b %Y %H:%M')}\n"
                if task.tags:
                    task_text += f"🏷️ {', '.join(task.tags)}\n"
                
                keyboard = [
                    [
                        InlineKeyboardButton("✏️ Edit", callback_data=f"editselect_{task.id}"),
                        InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{task.id}")
                    ]
                ]
                
                await update.message.reply_text(
                    task_text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            if len(tasks) > 10:
                await update.message.reply_text(f"... and {len(tasks) - 10} more tasks")
            
        except Exception as e:
            logger.error(f"❌ Error in tasks command: {e}")
            await update.message.reply_text("❌ An error occurred while loading tasks.")
    
    async def handle_add_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /add_task command"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Extract task title from command (only if it starts with /add_task)
            command_text = update.message.text.strip()
            
            if command_text.startswith('/add_task') and len(command_text.split(' ', 1)) >= 2:
                task_title = command_text.split(' ', 1)[1].strip()
                if task_title:
                    await self._create_and_confirm_task(update, user, task_title)
                    return
            
            # No title provided or called from keyboard - ask for it
            context.user_data['pending_action'] = 'new_task_title'
            await update.message.reply_text("📝 Enter the task name:")
            
        except Exception as e:
            logger.error(f"❌ Error in add_task command: {e}")
            await update.message.reply_text("❌ An error occurred while adding the task.")
    
    async def _create_and_confirm_task(self, update: Update, user, task_title: str) -> None:
        """Create a task and send confirmation with action buttons"""
        task = await self._create_task_use_case.execute(
            user=user,
            title=task_title,
            task_type=TaskType.ASSIGNMENT,
            priority=TaskPriority.MEDIUM
        )
        
        keyboard = self._create_task_actions_keyboard(task.id)
        
        await update.message.reply_text(
            f"✅ Task added: **{task.title}**\n\n"
            f"🎯 Customize your task using the buttons below:",
            reply_markup=keyboard
        )
    
    async def handle_deadline_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /deadline command"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Extract days from command
            command_text = update.message.text
            parts = command_text.split()
            
            if len(parts) > 1 and parts[1].isdigit():
                days = int(parts[1])
            else:
                days = 7  # Default to 7 days
            
            # Get upcoming deadlines using use case
            deadlines = await self._get_tasks_use_case.get_upcoming_deadlines(user, days)
            
            if not deadlines:
                await update.message.reply_text(f"📅 No deadlines in the next {days} days!")
                return
            
            # Format deadlines message
            message = self._format_deadlines_list(deadlines, days)
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"❌ Error in deadline command: {e}")
            await update.message.reply_text("❌ An error occurred while loading deadlines.")
    
    async def handle_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /search command"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Extract search term (only from /search command)
            command_text = update.message.text.strip()
            
            if command_text.startswith('/search') and len(command_text.split(' ', 1)) >= 2:
                search_term = command_text.split(' ', 1)[1].strip()
                if search_term:
                    await self._execute_search(update, user, search_term)
                    return
            
            # No search term - ask for it
            context.user_data['pending_action'] = 'search_keyword'
            await update.message.reply_text("🔍 Enter the keyword to search for:")
            
        except Exception as e:
            logger.error(f"❌ Error in search command: {e}")
            await update.message.reply_text("❌ An error occurred while searching tasks.")
    
    async def _execute_search(self, update: Update, user, search_term: str) -> None:
        """Execute search and send results"""
        tasks = await self._get_tasks_use_case.search_tasks(user, search_term)
        
        if not tasks:
            await update.message.reply_text(f"🔍 No tasks found containing: **{search_term}**")
            return
        
        message = self._format_search_results(tasks, search_term)
        await update.message.reply_text(message)
    
    async def handle_edit_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /edit_task <task_id> command - edit specific task by ID"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Extract task ID from command
            command_text = update.message.text
            parts = command_text.split(' ', 1)
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify the task ID:\n"
                    "`/edit_task <task_id>`\n\n"
                    "💡 Use `/tasks` to see your task IDs."
                )
                return
            
            task_id = parts[1].strip()
            
            # Get task by ID
            task = await self._task_repository.get_by_id(task_id)
            
            if not task:
                await update.message.reply_text(
                    f"❌ Task with ID `{task_id}` not found.\n\n"
                    f"💡 Use `/tasks` to see available tasks."
                )
                return
            
            # Show edit options for the task
            await self._show_task_edit_options(update, task)
            
        except Exception as e:
            logger.error(f"❌ Error in edit_task command: {e}")
            await update.message.reply_text("❌ An error occurred while editing the task.")
    
    async def _show_task_edit_options(self, update: Update, task: Task) -> None:
        """Show edit options for a specific task"""
        # Create edit options keyboard
        keyboard = [
            [
                InlineKeyboardButton("📝 Title", callback_data=f"edittitle_{task.id}"),
                InlineKeyboardButton("⏰ Deadline", callback_data=f"editdeadline_{task.id}")
            ],
            [
                InlineKeyboardButton("🏷️ Tags", callback_data=f"edittags_{task.id}"),
                InlineKeyboardButton("📄 Description", callback_data=f"editdesc_{task.id}")
            ],
            [
                InlineKeyboardButton("🔥 Priority", callback_data=f"editpriority_{task.id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"editcancel_{task.id}")
            ]
        ]
        
        # Show current task info
        task_info = f"✏️ **Edit task:** {task.title}\n\n"
        if task.deadline:
            task_info += f"⏰ Deadline: {task.deadline.strftime('%d %b %Y %H:%M')}\n"
        if task.tags:
            task_info += f"🏷️ Tags: {', '.join(task.tags)}\n"
        if task.description:
            task_info += f"📄 Description: {task.description[:50]}...\n" if len(task.description) > 50 else f"📄 Description: {task.description}\n"
        task_info += f"🔥 Priority: {task.priority.value}\n\n"
        task_info += "**Select what to edit:**"
        
        await update.message.reply_text(
            task_info,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /edit command - show list of tasks to edit"""
        try:
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            # Get user's tasks
            tasks = await self._get_tasks_use_case.execute(user)
            
            if not tasks:
                await update.message.reply_text("📝 No tasks to edit. Use /add_task to add one!")
                return
            
            # Create task selection keyboard
            keyboard = self._create_task_selection_keyboard(tasks)
            
            await update.message.reply_text(
                "✏️ **Select the task you want to edit:**",
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"❌ Error in edit command: {e}")
            await update.message.reply_text("❌ An error occurred while loading tasks.")
    
    def _create_task_selection_keyboard(self, tasks: List[Task]) -> InlineKeyboardMarkup:
        """Create keyboard for selecting a task to edit"""
        keyboard = []
        
        for task in tasks:
            # Show task title and truncate if too long
            title = task.title[:30] + "..." if len(task.title) > 30 else task.title
            keyboard.append([
                InlineKeyboardButton(f"✏️ {title}", callback_data=f"editselect_{task.id}")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def _handle_edit_selection(self, query, task: Task, user: User) -> None:
        """Show edit options for selected task"""
        try:
            logger.info(f"✏️ Edit requested for task: {task.title}")
            
            # Create edit options keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📝 Title", callback_data=f"edittitle_{task.id}"),
                    InlineKeyboardButton("⏰ Deadline", callback_data=f"editdeadline_{task.id}")
                ],
                [
                    InlineKeyboardButton("🏷️ Tags", callback_data=f"edittags_{task.id}"),
                    InlineKeyboardButton("📄 Description", callback_data=f"editdesc_{task.id}")
                ],
                [
                    InlineKeyboardButton("🔥 Priority", callback_data=f"editpriority_{task.id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data=f"editcancel_{task.id}")
                ]
            ]
            
            # Show current task info
            task_info = f"✏️ **Edit task:** {task.title}\n\n"
            if task.deadline:
                task_info += f"⏰ Deadline: {task.deadline.strftime('%d %b %Y %H:%M')}\n"
            if task.tags:
                task_info += f"🏷️ Tags: {', '.join(task.tags)}\n"
            if task.description:
                task_info += f"📄 Description: {task.description[:50]}...\n" if len(task.description) > 50 else f"📄 Description: {task.description}\n"
            task_info += f"🔥 Priority: {task.priority.value}\n\n"
            task_info += "**Select what to edit:**"
            
            await query.edit_message_text(
                task_info,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"❌ Error in edit selection: {e}")
            await query.edit_message_text("❌ An error occurred while editing.")
    
    async def _get_user_from_update(self, update: Update) -> Optional[User]:
        """Get user from update"""
        user = update.effective_user
        if not user:
            return None
        
        existing_user = await self._user_repository.get_by_telegram_id(user.id)
        if not existing_user:
            # Handle both regular messages and callback queries
            message = update.message or (update.callback_query.message if update.callback_query else None)
            if message:
                await message.reply_text("❌ You need to register first with /start")
            return None
        
        return existing_user
    
    def _format_tasks_list(self, tasks: List[Task]) -> str:
        """Format tasks list for display"""
        message = "📋 **Your tasks:**\n\n"
        
        for task in tasks[:10]:  # Limit to 10 tasks
            status_emoji = {
                TaskStatus.TODO: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.CANCELLED: "❌"
            }
            
            priority_emoji = {
                TaskPriority.LOW: "🟢",
                TaskPriority.MEDIUM: "🟡",
                TaskPriority.HIGH: "🟠",
                TaskPriority.URGENT: "🔴"
            }
            
            deadline_text = ""
            if task.deadline:
                deadline_text = f"📅 {task.deadline.strftime('%d %b %H:%M')}"
            
            message += f"{status_emoji[task.status]} {priority_emoji[task.priority]} **{task.title}**\n"
            message += f"   🆔 `{task.id}`\n"
            if task.description:
                message += f"   📝 {task.description}\n"
            if deadline_text:
                message += f"   {deadline_text}\n"
            message += "\n"
        
        if len(tasks) > 10:
            message += f"... and {len(tasks) - 10} more tasks"
        
        return message
    
    def _format_deadlines_list(self, deadlines: List[Task], days: int) -> str:
        """Format deadlines list for display"""
        message = f"📅 **Deadlines in the next {days} days:**\n\n"
        
        for task in deadlines:
            days_left = (task.deadline - datetime.utcnow()).days
            
            if days_left == 0:
                time_left = f"Today at {task.deadline.strftime('%H:%M')}"
            elif days_left == 1:
                time_left = "Tomorrow"
            else:
                time_left = f"In {days_left} days"
            
            priority_emoji = {
                TaskPriority.LOW: "🟢",
                TaskPriority.MEDIUM: "🟡",
                TaskPriority.HIGH: "🟠",
                TaskPriority.URGENT: "🔴"
            }
            
            message += f"🔴 {time_left} - **{task.title}**\n"
            message += f"   {priority_emoji[task.priority]} Priority: {task.priority.value}\n"
            message += f"   📅 {task.deadline.strftime('%d %b %H:%M')}\n\n"
        
        return message
    
    def _format_search_results(self, tasks: List[Task], search_term: str) -> str:
        """Format search results for display"""
        message = f"🔍 **Search results for '{search_term}':**\n\n"
        
        for task in tasks:
            status_emoji = {
                TaskStatus.TODO: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.CANCELLED: "❌"
            }
            
            message += f"{status_emoji[task.status]} **{task.title}**\n"
            if task.description:
                # Simple highlighting
                desc = task.description
                if search_term.lower() in desc.lower():
                    desc = desc.replace(search_term, f"**{search_term}**", 1)
                message += f"   📝 {desc}\n"
            message += "\n"
        
        return message
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Parse callback data
            callback_data = query.data
            if not callback_data:
                return
            
            logger.info(f"🔄 Callback received: {callback_data}")
            
            # Special handling for language selection (format: lang_code)
            if callback_data.startswith('lang_'):
                lang_code = callback_data.split('_')[1]
                await self._handle_language_selection(update, query, lang_code)
                return
            
            # Special handling for priority callbacks (format: priority_value_taskid)
            if callback_data.startswith('priority_'):
                parts = callback_data.split('_')
                if len(parts) >= 3:
                    priority_value = parts[1]
                    # Reconstruct task ID from remaining parts
                    actual_task_id = '_'.join(parts[2:])
                    
                    logger.info(f"🎯 Priority action: {priority_value}, Task ID: {actual_task_id}")
                    
                    task = await self._task_repository.get_by_id(actual_task_id)
                    if task:
                        await self._process_set_priority(query, task, priority_value)
                    else:
                        logger.error(f"❌ Task not found for priority: {actual_task_id}")
                        await query.edit_message_text("❌ Task not found.")
                else:
                    logger.error(f"❌ Invalid priority callback format: {callback_data}")
                return
            
            # General parsing for other callbacks (format: action_taskid)
            parts = callback_data.split('_')
            if len(parts) < 2:
                logger.error(f"❌ Invalid callback format: {callback_data}")
                return
            
            action = parts[0]
            task_id = '_'.join(parts[1:])  # Join remaining parts for task ID
            
            logger.info(f"🎯 Action: {action}, Task ID: {task_id}")
            
            user = await self._get_user_from_update(update)
            if not user:
                logger.error("❌ User not found")
                return
            
            # Get task
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                logger.error(f"❌ Task not found: {task_id}")
                await query.edit_message_text("❌ Task not found.")
                return
            
            logger.info(f"✅ Found task: {task.title}")
            
            if action == "setdeadline":
                await self._handle_set_deadline(query, task, user, context)
            elif action == "addtags":
                await self._handle_add_tags(query, task, user, context)
            elif action == "adddescription":
                await self._handle_add_description(query, task, user, context)
            elif action == "setpriority":
                await self._handle_set_priority(query, task, user, context)
            elif action == "delete":
                await self._handle_delete_task(query, task, user)
            elif action == "confirmdelete":
                await self._process_delete_task(query, task, user)
            elif action == "editselect":
                await self._handle_edit_selection(query, task, user)
            elif action == "edittitle":
                await self._handle_edit_title(query, task, user, context)
            elif action == "editdeadline":
                await self._handle_edit_deadline(query, task, user, context)
            elif action == "edittags":
                await self._handle_edit_tags(query, task, user, context)
            elif action == "editdesc":
                await self._handle_edit_description(query, task, user, context)
            elif action == "editpriority":
                await self._handle_edit_priority(query, task, user, context)
            elif action == "editcancel":
                await query.edit_message_text("✏️ Edit cancelled.")
            else:
                logger.error(f"❌ Unknown action: {action}")
                await query.edit_message_text("❌ Unknown action.")
            
        except Exception as e:
            logger.error(f"❌ Error in callback query: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    async def _process_set_priority(self, query, task: Task, priority_value: str) -> None:
        """Process priority setting"""
        try:
            # Convert string to TaskPriority enum
            priority_map = {
                'urgent': TaskPriority.URGENT,
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }
            
            new_priority = priority_map.get(priority_value, TaskPriority.MEDIUM)
            
            # Update task priority
            task.priority = new_priority
            await self._task_repository.update(task)
            
            priority_emoji = {
                TaskPriority.URGENT: "🔴",
                TaskPriority.HIGH: "🟠",
                TaskPriority.MEDIUM: "🟡",
                TaskPriority.LOW: "🟢"
            }
            
            await query.edit_message_text(
                f"✅ **Priority set for:** {task.title}\n"
                f"{priority_emoji[new_priority]} New priority: {new_priority.value}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error setting priority: {e}")
            await query.edit_message_text("❌ An error occurred while setting priority.")
    
    async def _handle_set_deadline(self, query, task: Task, user: User, context) -> None:
        """Handle set deadline action"""
        try:
            # Store task ID in context for next step
            user_data = context.user_data
            user_data['pending_action'] = 'set_deadline'
            user_data['task_id'] = task.id
            
            logger.info(f"📝 Setting deadline for task: {task.title}")
            
            await query.edit_message_text(
                f"⏰ **Set deadline for:** {task.title}\n\n"
                f"📅 Send the date in format: DD.MM.YYYY HH:MM\n"
                f"Example: 15.02.2026 14:30\n\n"
                f"Or use quick format:\n"
                f"• 'today 18:00'\n"
                f"• 'tomorrow 12:00'\n"
                f"• '3 days' (from now)\n"
                f"• '1 week' (from now)"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in handle_set_deadline: {e}")
            await query.edit_message_text("❌ An error occurred while setting the deadline.")
    
    async def _handle_add_tags(self, query, task: Task, user: User, context) -> None:
        """Handle add tags action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'add_tags'
            user_data['task_id'] = task.id
            
            logger.info(f"🏷️ Adding tags for task: {task.title}")
            
            await query.edit_message_text(
                f"🏷️ **Add tags for:** {task.title}\n\n"
                f"Send tags separated by space or comma:\n"
                f"Example: math exam important\n"
                f"Example: homework, urgent, school"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in handle_add_tags: {e}")
            await query.edit_message_text("❌ An error occurred while adding tags.")
    
    async def _handle_add_description(self, query, task: Task, user: User, context) -> None:
        """Handle add description action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'add_description'
            user_data['task_id'] = task.id
            
            logger.info(f"📝 Adding description for task: {task.title}")
            
            await query.edit_message_text(
                f"📝 **Add description for:** {task.title}\n\n"
                f"Send the task description:\n"
                f"Example: Solve exercises 1-20 from chapter 5 about integrals"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in handle_add_description: {e}")
            await query.edit_message_text("❌ An error occurred while adding description.")
    
    async def _handle_set_priority(self, query, task: Task, user: User, context) -> None:
        """Handle set priority action"""
        try:
            # Create priority selection keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🔴 Urgent", callback_data=f"priority_urgent_{task.id}"),
                    InlineKeyboardButton("🟠 High", callback_data=f"priority_high_{task.id}")
                ],
                [
                    InlineKeyboardButton("🟡 Medium", callback_data=f"priority_medium_{task.id}"),
                    InlineKeyboardButton("🟢 Low", callback_data=f"priority_low_{task.id}")
                ]
            ]
            
            current_priority = task.priority.value
            logger.info(f"🔥 Setting priority for task: {task.title}, current: {current_priority}")
            
            await query.edit_message_text(
                f"🔥 **Set priority for:** {task.title}\n\n"
                f"Current priority: {current_priority}\n\n"
                f"Choose new priority:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"❌ Error in handle_set_priority: {e}")
            await query.edit_message_text("❌ An error occurred while setting priority.")
    
    async def _handle_delete_task(self, query, task: Task, user: User) -> None:
        """Handle delete task action with confirmation"""
        try:
            logger.info(f"🗑️ Delete requested for task: {task.title}")
            
            # Create confirmation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Yes, delete", callback_data=f"confirmdelete_{task.id}"),
                    InlineKeyboardButton("❌ No, cancel", callback_data=f"canceldelete_{task.id}")
                ]
            ]
            
            await query.edit_message_text(
                f"🗑️ **Are you sure you want to delete this task?**\n\n"
                f"Task: {task.title}\n\n"
                f"⚠️ This action cannot be undone!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"❌ Error in handle_delete_task: {e}")
            await query.edit_message_text("❌ An error occurred.")
    
    async def _process_delete_task(self, query, task: Task, user: User) -> None:
        """Process task deletion"""
        try:
            logger.info(f"🗑️ Deleting task: {task.title}")
            
            # Delete task using repository
            success = await self._task_repository.delete(task.id)
            
            if success:
                await query.edit_message_text(
                    f"✅ **Task deleted successfully!**\n\n"
                    f"🗑️ {task.title} has been removed."
                )
                logger.info(f"✅ Task deleted: {task.title}")
            else:
                await query.edit_message_text(
                    f"❌ **Could not delete task**\n\n"
                    f"Task was not found in the database."
                )
                
        except Exception as e:
            logger.error(f"❌ Error deleting task: {e}")
            await query.edit_message_text("❌ An error occurred while deleting the task.")
    
    async def _handle_edit_title(self, query, task: Task, user: User, context) -> None:
        """Handle edit title action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'edit_title'
            user_data['task_id'] = task.id
            
            await query.edit_message_text(
                f"📝 **Edit title for:** {task.title}\n\n"
                f"Send the new title:"
            )
        except Exception as e:
            logger.error(f"❌ Error in edit title: {e}")
            await query.edit_message_text("❌ An error occurred.")
    
    async def _handle_edit_deadline(self, query, task: Task, user: User, context) -> None:
        """Handle edit deadline action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'edit_deadline'
            user_data['task_id'] = task.id
            
            current_deadline = task.deadline.strftime('%d.%m.%Y %H:%M') if task.deadline else "Not set"
            
            await query.edit_message_text(
                f"⏰ **Edit deadline for:** {task.title}\n\n"
                f"Current deadline: {current_deadline}\n\n"
                f"📅 Send the new date in format: DD.MM.YYYY HH:MM\n"
                f"Or use: 'today 18:00', 'tomorrow 12:00', '3 days'"
            )
        except Exception as e:
            logger.error(f"❌ Error in edit deadline: {e}")
            await query.edit_message_text("❌ A apărut o eroare.")
    
    async def _handle_edit_tags(self, query, task: Task, user: User, context) -> None:
        """Handle edit tags action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'edit_tags'
            user_data['task_id'] = task.id
            
            current_tags = ', '.join(task.tags) if task.tags else "No tags"
            
            await query.edit_message_text(
                f"🏷️ **Edit tags for:** {task.title}\n\n"
                f"Current tags: {current_tags}\n\n"
                f"Send new tags (replaces old ones):\n"
                f"Example: math, exam, important"
            )
        except Exception as e:
            logger.error(f"❌ Error in edit tags: {e}")
            await query.edit_message_text("❌ A apărut o eroare.")
    
    async def _handle_edit_description(self, query, task: Task, user: User, context) -> None:
        """Handle edit description action"""
        try:
            user_data = context.user_data
            user_data['pending_action'] = 'edit_description'
            user_data['task_id'] = task.id
            
            current_desc = task.description if task.description else "No description"
            
            await query.edit_message_text(
                f"📄 **Edit description for:** {task.title}\n\n"
                f"Current description: {current_desc[:100]}{'...' if len(current_desc) > 100 else ''}\n\n"
                f"Send the new description:"
            )
        except Exception as e:
            logger.error(f"❌ Error in edit description: {e}")
            await query.edit_message_text("❌ A apărut o eroare.")
    
    async def _handle_edit_priority(self, query, task: Task, user: User, context) -> None:
        """Handle edit priority action"""
        try:
            # Create priority selection keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🔴 Urgent", callback_data=f"priority_urgent_{task.id}"),
                    InlineKeyboardButton("🟠 High", callback_data=f"priority_high_{task.id}")
                ],
                [
                    InlineKeyboardButton("🟡 Medium", callback_data=f"priority_medium_{task.id}"),
                    InlineKeyboardButton("🟢 Low", callback_data=f"priority_low_{task.id}")
                ]
            ]
            
            await query.edit_message_text(
                f"🔥 **Edit priority for:** {task.title}\n\n"
                f"Current priority: {task.priority.value}\n\n"
                f"Choose new priority:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"❌ Error in edit priority: {e}")
            await query.edit_message_text("❌ A apărut o eroare.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages for task actions"""
        try:
            message_text = update.message.text.strip() if update.message.text else ""
            
            # Handle persistent keyboard buttons
            keyboard_routes = {
                "📋 Tasks": self.handle_tasks_command,
                "➕ Add Task": self.handle_add_task_command,
                "📅 Deadlines": self.handle_deadline_command,
                "🔍 Search": self.handle_search_command,
                "❓ Help": self.handle_help_command,
            }
            
            if message_text in keyboard_routes:
                await keyboard_routes[message_text](update, context)
                return
            
            user = await self._get_user_from_update(update)
            if not user:
                return
            
            user_data = context.user_data
            pending_action = user_data.get('pending_action')
            task_id = user_data.get('task_id')
            
            if not pending_action:
                return  # Not in a pending action state
            
            # Handle new task title (no task_id needed)
            if pending_action == 'new_task_title':
                user_data.pop('pending_action', None)
                await self._create_and_confirm_task(update, user, message_text)
                return
            
            # Handle search keyword (no task_id needed)
            if pending_action == 'search_keyword':
                user_data.pop('pending_action', None)
                await self._execute_search(update, user, message_text)
                return
            
            if not task_id:
                return
            
            # Get task
            task = await self._task_repository.get_by_id(task_id)
            if not task:
                await update.message.reply_text("❌ Task not found.")
                return
            
            message_text = update.message.text
            
            if pending_action == 'set_deadline':
                await self._process_set_deadline(update, task, message_text)
            elif pending_action == 'add_tags':
                await self._process_add_tags(update, task, message_text)
            elif pending_action == 'add_description':
                await self._process_add_description(update, task, message_text)
            elif pending_action == 'edit_title':
                await self._process_edit_title(update, task, message_text)
            elif pending_action == 'edit_deadline':
                await self._process_edit_deadline(update, task, message_text)
            elif pending_action == 'edit_tags':
                await self._process_edit_tags(update, task, message_text)
            elif pending_action == 'edit_description':
                await self._process_edit_description(update, task, message_text)
            
            # Clear pending action
            user_data.pop('pending_action', None)
            user_data.pop('task_id', None)
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
    
    async def _process_set_deadline(self, update, task: Task, message_text: str) -> None:
        """Process deadline setting"""
        try:
            deadline = self._parse_deadline(message_text)
            if not deadline:
                await update.message.reply_text(
                    "❌ Invalid format. Try:\n"
                    "• DD.MM.YYYY HH:MM\n"
                    "• 'today 18:00'\n"
                    "• 'tomorrow 12:00'\n"
                    "• '3 days'\n"
                    "• '1 week'"
                )
                return
            
            # Update task deadline
            task.deadline = deadline
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Deadline set for:** {task.title}\n"
                f"📅 {deadline.strftime('%d %b %Y %H:%M')}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error setting deadline: {e}")
            await update.message.reply_text("❌ An error occurred while setting the deadline.")
    
    async def _process_add_tags(self, update, task: Task, message_text: str) -> None:
        """Process tags addition"""
        try:
            # Parse tags
            tags = [tag.strip().strip(',') for tag in message_text.replace(',', ' ').split() if tag.strip()]
            
            if not tags:
                await update.message.reply_text("❌ No valid tags found.")
                return
            
            # Add tags to task
            task.tags.extend(tags)
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Tags added for:** {task.title}\n"
                f"🏷️ {', '.join(tags)}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error adding tags: {e}")
            await update.message.reply_text("❌ An error occurred while adding tags.")
    
    async def _process_add_description(self, update, task: Task, message_text: str) -> None:
        """Process description addition"""
        try:
            # Update task description
            task.description = message_text
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Description added for:** {task.title}\n"
                f"📝 {message_text}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error adding description: {e}")
            await update.message.reply_text("❌ An error occurred while adding description.")
    
    async def _process_edit_title(self, update, task: Task, message_text: str) -> None:
        """Process title edit"""
        try:
            old_title = task.title
            task.title = message_text
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Title updated!**\n\n"
                f"📝 Old: {old_title}\n"
                f"📝 New: {message_text}"
            )
        except Exception as e:
            logger.error(f"❌ Error editing title: {e}")
            await update.message.reply_text("❌ An error occurred while editing the title.")
    
    async def _process_edit_deadline(self, update, task: Task, message_text: str) -> None:
        """Process deadline edit"""
        try:
            deadline = self._parse_deadline(message_text)
            if not deadline:
                await update.message.reply_text(
                    "❌ Invalid format. Try:\n"
                    "• DD.MM.YYYY HH:MM\n"
                    "• 'today 18:00'\n"
                    "• 'tomorrow 12:00'\n"
                    "• '3 days'\n"
                    "• '1 week'"
                )
                return
            
            task.deadline = deadline
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Deadline updated for:** {task.title}\n"
                f"📅 {deadline.strftime('%d %b %Y %H:%M')}"
            )
        except Exception as e:
            logger.error(f"❌ Error editing deadline: {e}")
            await update.message.reply_text("❌ An error occurred while editing the deadline.")
    
    async def _process_edit_tags(self, update, task: Task, message_text: str) -> None:
        """Process tags edit"""
        try:
            tags = [tag.strip().strip(',') for tag in message_text.replace(',', ' ').split() if tag.strip()]
            
            if not tags:
                await update.message.reply_text("❌ No valid tags found.")
                return
            
            old_tags = task.tags.copy() if task.tags else []
            task.tags = tags
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Tags updated for:** {task.title}\n\n"
                f"🏷️ Old: {', '.join(old_tags) if old_tags else 'None'}\n"
                f"🏷️ New: {', '.join(tags)}"
            )
        except Exception as e:
            logger.error(f"❌ Error editing tags: {e}")
            await update.message.reply_text("❌ An error occurred while editing tags.")
    
    async def _process_edit_description(self, update, task: Task, message_text: str) -> None:
        """Process description edit"""
        try:
            old_desc = task.description if task.description else "No description"
            task.description = message_text
            await self._task_repository.update(task)
            
            await update.message.reply_text(
                f"✅ **Description updated for:** {task.title}\n\n"
                f"📝 Old: {old_desc[:100]}{'...' if len(old_desc) > 100 else ''}\n\n"
                f"📝 New: {message_text[:200]}{'...' if len(message_text) > 200 else ''}"
            )
        except Exception as e:
            logger.error(f"❌ Error editing description: {e}")
            await update.message.reply_text("❌ An error occurred while editing description.")
    
    def _parse_deadline(self, text: str) -> Optional[datetime]:
        """Parse deadline from various text formats"""
        import re
        from datetime import datetime, timedelta
        
        text = text.lower().strip()
        now = datetime.utcnow()
        
        # Format: DD.MM.YYYY HH:MM
        match = re.match(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})', text)
        if match:
            day, month, year, hour, minute = map(int, match.groups())
            try:
                return datetime(year, month, day, hour, minute)
            except ValueError:
                pass
        
        # Format: today HH:MM
        match = re.match(r'today\s+(\d{2}):(\d{2})', text)
        if match:
            hour, minute = map(int, match.groups())
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Format: tomorrow HH:MM
        match = re.match(r'tomorrow\s+(\d{2}):(\d{2})', text)
        if match:
            hour, minute = map(int, match.groups())
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Format: X days
        match = re.match(r'(\d+)\s*days?', text)
        if match:
            days = int(match.group(1))
            return now + timedelta(days=days)
        
        # Format: X week(s)
        match = re.match(r'(\d+)\s*weeks?', text)
        if match:
            weeks = int(match.group(1))
            return now + timedelta(weeks=weeks)
        
        return None
    
    def _create_task_actions_keyboard(self, task_id: str) -> InlineKeyboardMarkup:
        """Create inline keyboard for task actions - all visible on screen"""
        keyboard = [
            # Row 1: Deadline and Tags (most used)
            [
                InlineKeyboardButton("⏰ Deadline", callback_data=f"setdeadline_{task_id}"),
                InlineKeyboardButton("🏷️ Tags", callback_data=f"addtags_{task_id}")
            ],
            # Row 2: Description and Priority
            [
                InlineKeyboardButton("📝 Description", callback_data=f"adddescription_{task_id}"),
                InlineKeyboardButton("🔥 Priority", callback_data=f"setpriority_{task_id}")
            ],
            # Row 3: Delete action (separate for safety)
            [
                InlineKeyboardButton("❌ Cancel", callback_data=f"delete_{task_id}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
