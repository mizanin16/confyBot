def register_all_handlers(dp):
    from bot.handlers.commands import register_command_handlers
    from bot.handlers.filters import register_filter_handlers
    from bot.handlers.subscriptions import register_subscription_handlers
    from bot.handlers.settings import register_settings_handlers
    from bot.handlers.data_updater import register_data_updater_handlers
    from bot.handlers.search_handlers import register_search_handlers

    register_search_handlers(dp)
    register_data_updater_handlers(dp)
    register_command_handlers(dp)
    register_filter_handlers(dp)
    register_subscription_handlers(dp)
    register_settings_handlers(dp)