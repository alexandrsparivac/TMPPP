"""
Internationalization (i18n) module for the Telegram bot
Supports: Romanian (ro), English (en), Russian (ru)
"""

# Translations dictionary
TRANSLATIONS = {
    'ro': {
        'welcome_new': "👋 Bun venit, {name}!\n\n🌍 Te rog să selectezi limba ta:",
        'welcome_back': "👋 Bun revenit, {name}!\n\n🤖 Sunt gata să te ajut!\n💡 Scrie /help pentru comenzi.",
        'language_set': "✅ Limba a fost setată la: {language}",
        'help_text': "🤖 **Student Life Helper Bot - Comenzi Disponibile**\n\n📋 **Management Task-uri:**\n`/tasks` - Vezi toate task-urile tale\n`/add_task <titlu>` - Adaugă un task nou\n`/deadline <zile>` - Vezi deadline-uri în următoarele zile\n`/search <cuvânt>` - Caută task-uri",
        'no_tasks': "📝 Nu ai niciun task. Folosește /add_task pentru a adăuga!",
        'task_added': "✅ Task adăugat: **{title}**\n\n🎯 Acum poți personaliza task-ul folosind butoanele de mai jos:",
        'error': "❌ A apărut o eroare. Te rog să încerci din nou.",
        'set_deadline': "⏰ **Setează deadline pentru:** {title}\n\n📅 Trimite data în formatul: DD.MM.YYYY HH:MM\nExemplu: 15.02.2026 14:30\n\nSau folosește format rapid:\n• 'azi 18:00'\n• 'mâine 12:00'\n• '3 zile' (de acum)\n• '1 săptămână' (de acum)",
        'deadline_set': "✅ **Deadline setat pentru:** {title}\n📅 {deadline}",
        'add_tags': "🏷️ **Adaugă tag-uri pentru:** {title}\n\nTrimite tag-urile separate prin spațiu sau virgulă:\nExemplu: matematică examen important\nExemplu: temă, urgent, facultate",
        'tags_added': "✅ **Tag-uri adăugate pentru:** {title}\n🏷️ {tags}",
        'add_description': "📝 **Adaugă descriere pentru:** {title}\n\nTrimite descrierea task-ului:\nExemplu: Rezolvarea exercițiilor 1-20 din capitolul 5 despre integrale",
        'description_added': "✅ **Descriere adăugată pentru:** {title}\n📝 {description}",
        'set_priority': "🔥 **Setează prioritate pentru:** {title}\n\nPrioritate curentă: {current}\n\nAlege noua prioritate:",
        'priority_set': "✅ **Prioritate setată pentru:** {title}\n{emoji} Noua prioritate: {priority}",
        'delete_confirm': "🗑️ **Ești sigur că vrei să ștergi task-ul?**\n\nTask: {title}\n\n⚠️ Această acțiune nu poate fi anulată!",
        'task_deleted': "✅ **Task șters cu succes!**\n\n🗑️ {title} a fost eliminat.",
        'invalid_deadline': "❌ Format invalid. Încearcă:\n• DD.MM.YYYY HH:MM\n• 'azi 18:00'\n• 'mâine 12:00'\n• '3 zile'\n• '1 săptămână'",
        'invalid_tags': "❌ Nu am găsit tag-uri valide.",
        'task_not_found': "❌ Task-ul nu a fost găsit.",
        'unknown_action': "❌ Acțiune necunoscută.",
        'select_language': "🌍 Selectează limba:",
    },
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
    },
    'ru': {
        'welcome_new': "👋 Добро пожаловать, {name}!\n\n🌍 Пожалуйста, выберите ваш язык:",
        'welcome_back': "👋 С возвращением, {name}!\n\n🤖 Готов помочь!\n💡 Напишите /help для команд.",
        'language_set': "✅ Язык установлен: {language}",
        'help_text': "🤖 **Student Life Helper Bot - Доступные Команды**\n\n📋 **Управление Задачами:**\n`/tasks` - Посмотреть все задачи\n`/add_task <название>` - Добавить новую задачу\n`/deadline <дни>` - Посмотреть дедлайны в ближайшие дни\n`/search <слово>` - Поиск задач",
        'no_tasks': "📝 У вас нет задач. Используйте /add_task, чтобы добавить!",
        'task_added': "✅ Задача добавлена: **{title}**\n\n🎯 Теперь вы можете настроить задачу с помощью кнопок ниже:",
        'error': "❌ Произошла ошибка. Пожалуйста, попробуйте снова.",
        'set_deadline': "⏰ **Установить дедлайн для:** {title}\n\n📅 Отправьте дату в формате: ДД.ММ.ГГГГ ЧЧ:ММ\nПример: 15.02.2026 14:30\n\nИли используйте быстрый формат:\n• 'сегодня 18:00'\n• 'завтра 12:00'\n• '3 дня' (от сейчас)\n• '1 неделя' (от сейчас)",
        'deadline_set': "✅ **Дедлайн установлен для:** {title}\n📅 {deadline}",
        'add_tags': "🏷️ **Добавить теги для:** {title}\n\nОтправьте теги через пробел или запятую:\nПример: математика экзамен важно\nПример: домашка, срочно, школа",
        'tags_added': "✅ **Теги добавлены для:** {title}\n🏷️ {tags}",
        'add_description': "📝 **Добавить описание для:** {title}\n\nОтправьте описание задачи:\nПример: Решение упражнений 1-20 из главы 5 про интегралы",
        'description_added': "✅ **Описание добавлено для:** {title}\n📝 {description}",
        'set_priority': "🔥 **Установить приоритет для:** {title}\n\nТекущий приоритет: {current}\n\nВыберите новый приоритет:",
        'priority_set': "✅ **Приоритет установлен для:** {title}\n{emoji} Новый приоритет: {priority}",
        'delete_confirm': "🗑️ **Вы уверены, что хотите удалить эту задачу?**\n\nЗадача: {title}\n\n⚠️ Это действие нельзя отменить!",
        'task_deleted': "✅ **Задача успешно удалена!**\n\n🗑️ {title} была удалена.",
        'invalid_deadline': "❌ Неверный формат. Попробуйте:\n• ДД.ММ.ГГГГ ЧЧ:ММ\n• 'сегодня 18:00'\n• 'завтра 12:00'\n• '3 дня'\n• '1 неделя'",
        'invalid_tags': "❌ Не найдено действительных тегов.",
        'task_not_found': "❌ Задача не найдена.",
        'unknown_action': "❌ Неизвестное действие.",
        'select_language': "🌍 Выберите язык:",
    }
}

# Language names for display
LANGUAGE_NAMES = {
    'ro': 'Română 🇷🇴',
    'en': 'English 🇬🇧',
    'ru': 'Русский 🇷🇺'
}

# Priority translations
PRIORITY_NAMES = {
    'ro': {
        'urgent': 'Urgent',
        'high': 'Ridicat',
        'medium': 'Mediu',
        'low': 'Scăzut'
    },
    'en': {
        'urgent': 'Urgent',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
    },
    'ru': {
        'urgent': 'Срочно',
        'high': 'Высокий',
        'medium': 'Средний',
        'low': 'Низкий'
    }
}


def get_text(key: str, lang: str = 'ro', **kwargs) -> str:
    """
    Get translated text by key and language.
    
    Args:
        key: The translation key
        lang: Language code ('ro', 'en', 'ru')
        **kwargs: Format arguments for the translation string
    
    Returns:
        Translated text with applied formatting
    """
    # Default to Romanian if language not found
    if lang not in TRANSLATIONS:
        lang = 'ro'
    
    # Get text or return key if not found
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['ro'].get(key, key))
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text


def get_priority_name(priority: str, lang: str = 'ro') -> str:
    """Get translated priority name"""
    if lang not in PRIORITY_NAMES:
        lang = 'ro'
    return PRIORITY_NAMES[lang].get(priority.lower(), priority)


def get_language_name(lang_code: str) -> str:
    """Get display name for language code"""
    return LANGUAGE_NAMES.get(lang_code, lang_code)
