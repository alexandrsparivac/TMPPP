TRANSLATIONS = {
    'en': {
        'welcome_new': "👋 Welcome, {name}!\n\n🌍 Please select your language:",
        'welcome_back': "👋 Welcome back, {name}!\n\n🤖 Ready to help!\n💡 Type /help for commands.",
        'language_set': "✅ Language set to: {language}",
        'help_text': "🤖 **Student Life Helper Bot - Available Commands**\n\n📋 **Task Management:**\n`/tasks` - View all your tasks\n`/add_task <title>` - Add a new task\n`/deadline <days>` - View deadlines in the next days\n`/search <word>` - Search tasks",
        'no_tasks': "📝 You have no tasks. Use /add_task to add one!",
        'task_added': "✅ Task added: **{title}**\n\n🎯 Now you can customize the task using the buttons below:",
        'error': "❌ An error occurred. Please try again.",
        'set_deadline': "⏰ **Set deadline for:** {title}\n\n📅 Send the date in format: DD.MM.YYYY HH:MM\nExample: 15.02.2026 14:30\n\nOr use quick format:\n• 'today 18:00'\n• 'tomorrow 12:00'\n• '3 days' (from now)\n• '1 week' (from now)",
        'deadline_set': "✅ **Deadline set for:** {title}\n📅 {deadline}",
        'add_tags': "🏷️ **Add tags for:** {title}\n\nSend tags separated by space or comma:\nExample: math exam important\nExample: homework, urgent, school",
        'tags_added': "✅ **Tags added for:** {title}\n🏷️ {tags}",
        'add_description': "📝 **Add description for:** {title}\n\nSend the task description:\nExample: Solving exercises 1-20 from chapter 5 about integrals",
        'description_added': "✅ **Description added for:** {title}\n📝 {description}",
        'set_priority': "🔥 **Set priority for:** {title}\n\nCurrent priority: {current}\n\nChoose new priority:",
        'priority_set': "✅ **Priority set for:** {title}\n{emoji} New priority: {priority}",
        'delete_confirm': "🗑️ **Are you sure you want to delete this task?**\n\nTask: {title}\n\n⚠️ This action cannot be undone!",
        'task_deleted': "✅ **Task deleted successfully!**\n\n🗑️ {title} has been removed.",
        'invalid_deadline': "❌ Invalid format. Try:\n• DD.MM.YYYY HH:MM\n• 'today 18:00'\n• 'tomorrow 12:00'\n• '3 days'\n• '1 week'",
        'invalid_tags': "❌ No valid tags found.",
        'task_not_found': "❌ Task not found.",
        'unknown_action': "❌ Unknown action.",
        'select_language': "🌍 Select your language:",
    }
}

LANGUAGE_NAMES = {
    'en': 'English 🇬🇧'
}

PRIORITY_NAMES = {
    'en': {
        'urgent': 'Urgent',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    text = TRANSLATIONS['en'].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

def get_priority_name(priority: str, lang: str = 'en') -> str:
    return PRIORITY_NAMES['en'].get(priority.lower(), priority)

def get_language_name(lang_code: str) -> str:
    return LANGUAGE_NAMES.get(lang_code, lang_code)
