import os
import requests
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters, CallbackQueryHandler
)
import logging


from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

load_dotenv()

API_URL = os.getenv("API_URL").rstrip("/")
BOT_TOKEN = os.getenv("BOT_TOKEN")

LOGIN_USERNAME, LOGIN_PASSWORD = range(2)
ADD_TITLE, ADD_CONTENT = range(2, 4)
EDIT_TITLE, EDIT_CONTENT = range(4, 6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /start:", update.message.text)
    await update.message.reply_text("Привет! Я - бот блогов.")


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите логин:")
    return LOGIN_USERNAME


async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Введите пароль:")
    return LOGIN_PASSWORD


async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data["username"]
    password = update.message.text
    res = requests.post(f"{API_URL}/login",
                        json={"username": username, "password": password})
    if res.status_code == 200:
        token = res.json()["token"]
        context.user_data["token"] = token
        await update.message.reply_text("✅ Успешный вход!")
    else:
        await update.message.reply_text("❌ Неверный логин или пароль.")
    return ConversationHandler.END


async def posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resp = requests.get(f"{API_URL}/posts")
    data = resp.json()
    buttons = [[InlineKeyboardButton(
        f"{p['id']}: {p['title']}", callback_data=str(p["id"]))] for p in data]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Выберите пост:", reply_markup=reply_markup)


async def show_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    post_id = query.data
    resp = requests.get(f"{API_URL}/posts/{post_id}")
    p = resp.json()
    dt = datetime.fromisoformat(p['created_at'].replace("Z", "+00:00"))
    dt_moscow = dt.astimezone(timezone(timedelta(hours=3)))
    formatted_date = dt_moscow.strftime("%d.%m.%Y %H:%M")
    text = f"{p['content']}\n\n🕒 Дата: {formatted_date} (МСК)"
    await query.edit_message_text(text)


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "token" not in context.user_data:
        await update.message.reply_text("Сначала выполните вход /login")
        return ConversationHandler.END
    await update.message.reply_text("Введите заголовок поста:")
    return ADD_TITLE


async def add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Введите текст поста:")
    return ADD_CONTENT


async def add_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data["token"]
    payload = {
        "title": context.user_data["title"],
        "content": update.message.text
    }
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{API_URL}/posts", json=payload, headers=headers)
    if res.status_code == 200:
        await update.message.reply_text("✅ Пост добавлен!")
    else:
        await update.message.reply_text(f"❌ Ошибка: {res.status_code}\n{res.text}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


async def edit_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "token" not in context.user_data:
        await update.message.reply_text("❗ Сначала выполните вход /login")
        return ConversationHandler.END

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажи ID поста: /edit <id>")
        return ConversationHandler.END

    context.user_data["edit_post_id"] = context.args[0]
    await update.message.reply_text("Введите новый заголовок поста:")
    return EDIT_TITLE


async def edit_post_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_title"] = update.message.text
    await update.message.reply_text("Введите новый текст поста:")
    return EDIT_CONTENT


async def edit_post_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data["token"]
    post_id = context.user_data["edit_post_id"]
    new_title = context.user_data["new_title"]
    new_content = update.message.text

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": new_title, "content": new_content}
    response = requests.put(
        f"{API_URL}/posts/{post_id}", json=payload, headers=headers)

    if response.status_code == 200:
        await update.message.reply_text("✅ Пост успешно обновлён.")
    elif response.status_code == 403:
        await update.message.reply_text("⛔ У вас нет прав на редактирование этого поста.")
    elif response.status_code == 404:
        await update.message.reply_text("❌ Пост не найден.")
    else:
        await update.message.reply_text(f"❌ Ошибка: {response.status_code}\n{response.text}")
    return ConversationHandler.END


async def delete_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("❗ Сначала авторизуйтесь командой /login")
        return

    headers = {"Authorization": f"Bearer {token}"}
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажи ID поста: /delete <id>")
        return

    post_id = context.args[0]
    response = requests.delete(f"{API_URL}/posts/{post_id}", headers=headers)

    if response.status_code == 200:
        await update.message.reply_text(f"✅ Пост с ID {post_id} удалён.")
    else:
        await update.message.reply_text(f"❌ Не удалось удалить пост с ID {post_id}. Код: {response.status_code}")
        await update.message.reply_text(response.text)


async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("➡ Получено сообщение:", update.message)


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    login_handler = ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            LOGIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_username)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    add_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title)],
            ADD_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_content)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_post_start)],
        states={
            EDIT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_post_title)],
            EDIT_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_post_content)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(login_handler)
    app.add_handler(add_handler)
    app.add_handler(edit_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("posts", posts))
    app.add_handler(CommandHandler("delete", delete_post))
    app.add_handler(CallbackQueryHandler(show_post))
    app.add_handler(MessageHandler(filters.ALL, debug_all))

    print("✅ Бот запущен и слушает команды (polling)...")

    app.run_polling()


if __name__ == "__main__":
    main()
