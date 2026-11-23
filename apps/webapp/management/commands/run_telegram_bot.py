import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import (
    Update,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    BotCommand,
    MenuButtonWebApp,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Telegram Botini yurgizish (python-telegram-bot kutubxonasi orqali): /start va /order komandalari."

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            default='',
            help="Telegram Bot Token (agar ko'rsatilmasa settings yoki env dan olinadi)",
        )
        parser.add_argument(
            '--url',
            type=str,
            default='',
            help="Telegram WebApp URL manzili (masalan: https://domain/webapp/ yoki ngrok)",
        )

    def handle(self, *args, **options):
        token = options['token'] or getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        webapp_url = options['url'] or getattr(settings, 'TELEGRAM_WEBAPP_URL', 'http://127.0.0.1:8000/webapp/')

        if not token:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ TELEGRAM_BOT_TOKEN topilmadi!\n"
                    "Iltimos, .env faylida TELEGRAM_BOT_TOKEN ni ko'rsating yoki quyidagicha yurgizing:\n"
                    "  python manage.py run_telegram_bot --token='SIZNING_BOT_TOKENINGIZ' --url='https://sizning-domen/webapp/'"
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f"🚀 Telegram Bot (python-telegram-bot) ishga tushirilmoqda..."))
        self.stdout.write(self.style.NOTICE(f"📌 WebApp URL: {webapp_url}"))
        self.stdout.write(self.style.NOTICE("📌 Buyruqlar: /start va /order"))

        # Asinxron post_init orqali buyruqlar va menyu tugmasini sozlash
        async def post_init(application):
            try:
                # 1. Bot komandalarini Telegram menyusiga kiritish
                await application.bot.set_my_commands([
                    BotCommand("start", "Bot haqida ma'lumot"),
                    BotCommand("order", "Menyuni ochish va buyurtma berish"),
                ])

                # 2. Chat menyu tugmasini WebApp qilib sozlash
                await application.bot.set_chat_menu_button(
                    menu_button=MenuButtonWebApp(
                        text="Menyu 🍔",
                        web_app=WebAppInfo(url=webapp_url)
                    )
                )
                self.stdout.write(self.style.SUCCESS("✅ Telegram komandalari va WebApp Menyu tugmasi muvaffaqiyatli sozlandi!"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Bot menyusini sozlashda ogohlantirish: {e}"))

        # /start komandasi
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_name = update.effective_user.first_name if update.effective_user else "Qadrli mijoz"
            welcome_text = (
                f"Assalomu alaykum, {user_name}! 🍔\n\n"
                f"*Fast-Food Express* rasmiy buyurtma botiga xush kelibsiz!\n\n"
                f"Bizda eng mazali burgerlar, lavashlar va salqin ichimliklar mavjud.\n\n"
                f"Buyurtma berish uchun **/order** komandasini yuboring yoki quyidagi tugmani bosing!"
            )
            reply_keyboard = [
                [KeyboardButton(text="🛍 Buyurtma berish", web_app=WebAppInfo(url=webapp_url))]
            ]
            await update.message.reply_text(
                welcome_text,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
            )

        # /order komandasi
        async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            order_text = "Quyidagi tugma orqali menyuni ochishingiz va buyurtma berishingiz mumkin: 👇"
            inline_keyboard = [
                [InlineKeyboardButton(text="🍔 Menyuni ochish va Buyurtma berish", web_app=WebAppInfo(url=webapp_url))]
            ]
            await update.message.reply_text(
                order_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard),
            )

        # Application yaratish va handlerlarni ro'yxatga olish
        application = (
            ApplicationBuilder()
            .token(token)
            .post_init(post_init)
            .build()
        )

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("order", order_command))
        application.add_handler(MessageHandler(filters.Regex("^🛍 Buyurtma berish$"), order_command))

        self.stdout.write(self.style.SUCCESS("Bot faol! To'xtatish uchun Ctrl+C bosing."))

        # Botni polling rejimida ishga tushirish
        application.run_polling(drop_pending_updates=True)
