

def setup_middleware(bot):
    @bot.middleware_handler(update_types=['message'])
    def log_messages(bot_instance, message):
        print(f"[LOG] {message.from_user.id} says: {message.text}")
