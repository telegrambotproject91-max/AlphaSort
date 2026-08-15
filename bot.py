import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

WELCOME = (
    "👋 Welcome to Alphabet Sort Bot!\n\n"
    "A simple Telegram utility for organizing text alphabetically.\n\n"
    "🔤 <b>A–Z Sort</b>\n"
    "Arrange words or lines from A to Z.\n\n"
    "🔡 <b>Z–A Sort</b>\n"
    "Arrange words or lines from Z to A.\n\n"
    "📖 <b>Quick guide</b>\n"
    "1. Choose a sorting option below.\n"
    "2. Send your words, names, or lines.\n"
    "3. The bot returns the organized result.\n\n"
    "Example:\n"
    "banana\napple\norange\n\n"
    "Result:\n"
    "apple\nbanana\norange\n\n"
    "Choose a tool to get started."
)

MENU = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔤 A–Z Sort", callback_data="sort_az")],
    [InlineKeyboardButton(text="🔡 Z–A Sort", callback_data="sort_za")],
    [InlineKeyboardButton(text="❓ How to Use", callback_data="help")],
])

BACK = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu")]
])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME, reply_markup=MENU, parse_mode="HTML")

@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME, reply_markup=MENU, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_menu(callback: CallbackQuery):
    text = (
        "📖 <b>How to Use</b>\n\n"
        "Choose A–Z Sort or Z–A Sort, then send your text.\n\n"
        "You can send one item per line for the clearest result.\n\n"
        "The bot only sorts the text you provide and does not publish or share your content."
    )
    await callback.message.edit_text(text, reply_markup=BACK, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.in_({"sort_az", "sort_za"}))
async def choose_sort(callback: CallbackQuery):
    direction = "A–Z" if callback.data == "sort_az" else "Z–A"
    callback.message.chat  # keep callback message context available
    await callback.message.edit_text(
        f"{direction} Sort selected.\n\nSend the words or lines you want to sort.",
        reply_markup=BACK,
    )
    await callback.answer()
    # Store the selected direction per user in dispatcher workflow data.
    dp.workflow_data.setdefault("modes", {})[callback.from_user.id] = direction

@dp.message(F.text)
async def sort_text(message: Message):
    modes = dp.workflow_data.setdefault("modes", {})
    direction = modes.get(message.from_user.id)
    if not direction:
        await message.answer("Please choose a sorting option first.", reply_markup=MENU)
        return

    lines = [line.strip() for line in message.text.splitlines() if line.strip()]
    if not lines:
        await message.answer("Please send some words or lines to sort.", reply_markup=BACK)
        return

    reverse = direction == "Z–A"
    sorted_lines = sorted(lines, key=lambda value: value.casefold(), reverse=reverse)
    result = "\n".join(sorted_lines)
    await message.answer(
        f"✅ <b>{direction} result:</b>\n\n<code>{result}</code>",
        reply_markup=MENU,
        parse_mode="HTML",
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
