from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import random

TOKEN = "8619468927:AAHO36wRy6dYqhz0jvDRXvb8gCuD-49V7Xk"
ADMIN_CHAT_ID = 123456789  # đổi thành chat id của bạn

# ===== CONFIG BANK =====
BANK = "TCB"           # Vietcombank (có thể đổi: MBB, TCB,...)
ACCOUNT = "6302032003"  # STK của bạn

# ===== DATA =====
products = {
    "ai": [
        ("ChatGPT Plus", "50K"),
        ("ChatGPT Business", "50K"),
       # ("Gemini", "50K"),
       # ("Grok (7 ngày)", "10K"),
        #("Sora (7 ngày)", "10K"),
    ],
    "design": [
        ("Canva Pro", "20K"),
        ("CapCut Pro", "20K"),
        ("Veo 3 Ultra (45K Credit)", "120K"),
        ("Veo 3 Ultra (45K Credit)", "120K"),
        #("Veo 3 Pro (45K Credit)", "40K"),
       # ("Kling AI (215 Credit)", "10K"),
    ],
    "entertainment": [
        ("YouTube Premium", "30K"),
    ],
    "utility": [
        ("HMA VPN", "10K"),
        ("Gmail Pay", "5K"),
        ("Outlook US", "Free"),
    ],
    "gmail": [
        ("Mail 23-24", "19K"),
        ("Mail 2021-2022", "21K"),
        ("Mail 201x", "22K"),
        ("Mail 2010-2015", "23K"),
        ("Mail 200x", "27K"),
        ("Mail 2004-2005", "32K"),
    ]
}

# ===== START MENU =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
       # [InlineKeyboardButton("AI Tools (ChatGPT, Gemini, Grok, Sora)", callback_data="ai")], 
        [InlineKeyboardButton("ChatGPT", callback_data="ai")], 
        [InlineKeyboardButton("Canva, Veo 3, CapCut", callback_data="design")], 
        #[InlineKeyboardButton("Thiết kế - Video (Canva, Veo 3,Kling AI)", callback_data="design")], 
       # [InlineKeyboardButton("Giải trí (YouTube)", callback_data="entertainment")], 
       # [InlineKeyboardButton("Tiện ích (HMA VPN, Gmail Pay, Outlook US)", callback_data="utility")], 
        [InlineKeyboardButton("Gmail (Gmail)", callback_data="gmail")] 
    ]

    await update.message.reply_text(
        "🔥 CHÀO MỪNG BẠN ĐẾN SHOP 🔥\nChọn danh mục:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== SHOW PRODUCTS =====
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data
    items = products.get(category, [])

    keyboard = []
    for name, price in items:
        keyboard.append([
            InlineKeyboardButton(f"{name} - {price}", callback_data=f"buy|{name}|{price}")
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Quay lại", callback_data="back")])

    await query.edit_message_text(
        "📦 Chọn sản phẩm:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== BACK =====
async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update.callback_query, context)

# ===== BUY + QR =====
async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, name, price = query.data.split("|")

    # ===== convert giá =====
    try:
        amount = int(price.replace("K", "").replace("k", "")) * 1000
    except:
        amount = 0

    # ===== random mã đơn =====
    code = random.randint(1000, 9999)
    content = f"{name}_{code}"

    # ===== tạo QR =====
    qr_url = f"https://img.vietqr.io/image/{BANK}-{ACCOUNT}-compact2.png?amount={amount}&addInfo={content}"

    # ===== lưu state =====
    context.user_data["product"] = name
    context.user_data["price"] = price
    context.user_data["amount"] = amount
    context.user_data["code"] = code
    context.user_data["step"] = "waiting_payment"

    # ===== gửi QR =====
    await query.message.reply_photo(
        photo=qr_url,
        caption=(
            f"🛒 {name} - {price}\n\n"
            f"💳 STK: {ACCOUNT}\n"
            f"🏦 Bank: {BANK}\n"
            f"💰 Số tiền: {amount:,} VND\n\n"
            f"📌 Nội dung CK: {content}\n\n"
            "👉 Chuyển khoản xong, gửi 'done' để xác nhận"
        )
    )

# ===== HANDLE MESSAGE =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # ===== user báo đã chuyển tiền =====
    if text == "done" and context.user_data.get("step") == "waiting_payment":
        product = context.user_data.get("product")
        price = context.user_data.get("price")
        code = context.user_data.get("code")

        await update.message.reply_text("✅ Đã nhận thông tin, admin sẽ kiểm tra!")

        # gửi admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"💰 KHÁCH BÁO ĐÃ CK\n"
                f"Sản phẩm: {product}\n"
                f"Giá: {price}\n"
                f"Mã đơn: {code}"
            )
        )

        context.user_data["step"] = None

# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_category, pattern="^(ai|design|entertainment|utility|gmail)$"))
app.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))
app.add_handler(CallbackQueryHandler(handle_buy, pattern="^buy"))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()