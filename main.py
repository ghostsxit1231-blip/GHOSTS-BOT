import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# وضع بياناتك التي أرسلتها بالكامل
BOT_TOKEN = "8831438839:AAHGrZ8_IYiupKHsFocPov7vupx9M-4_Sb8"
CHANNEL_1 = "@ghostsxit1"
CHANNEL_2 = "@ghostsxit2"

bot = telebot.TeleBot(BOT_TOKEN)

# المتغيرات لتخزين المحتوى المحدث تلقائياً
LATEST_VIDEO_URL = "لم يتم الرفع بعد / Not Uploaded Yet"
LATEST_FILE_URL = "لم يتم الرفع بعد / Not Uploaded Yet"
LATEST_PASSWORD = "لا يوجد / No Password"

# متغير لحفظ آيدي الجروب الخاص تلقائياً بمجرد إرسال أول رسالة فيه
PRIVATE_GROUP_ID = None

# دالة للتحقق من إشتراك المستخدم في القناتين معاً
def is_user_subscribed(user_id):
    try:
        # فحص القناة الأولى
        member1 = bot.get_chat_member(CHANNEL_1, user_id)
        # فحص القناة الثانية
        member2 = bot.get_chat_member(CHANNEL_2, user_id)
        
        check1 = member1.status in ['member', 'administrator', 'creator']
        check2 = member2.status in ['member', 'administrator', 'creator']
        
        return check1 and check2
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# 1. قائمة اختيار اللغة
def language_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇮🇳 हिंदी (Hindi)", callback_data="lang_hi")
    )
    return markup

# 2. قائمة الخيارات حسب اللغة المختارها
def options_menu(lang):
    markup = InlineKeyboardMarkup(row_width=2)
    
    if lang == "ar":
        btn_video = InlineKeyboardButton(text="🎬 آخر فيديو", callback_data="get_video_ar")
        btn_file = InlineKeyboardButton(text="📁 آخر ملف", callback_data="get_file_ar")
        btn_pass = InlineKeyboardButton(text="🔑 الباسورد", callback_data="get_pass_ar")
        btn_back = InlineKeyboardButton(text="🌍 تغيير اللغة", callback_data="change_lang")
    elif lang == "en":
        btn_video = InlineKeyboardButton(text="🎬 Latest Video", callback_data="get_video_en")
        btn_file = InlineKeyboardButton(text="📁 Latest File", callback_data="get_file_en")
        btn_pass = InlineKeyboardButton(text="🔑 Password", callback_data="get_pass_en")
        btn_back = InlineKeyboardButton(text="🌍 Change Language", callback_data="change_lang")
    else: # هندي
        btn_video = InlineKeyboardButton(text="🎬 नवीनतम वीडियो", callback_data="get_video_hi")
        btn_file = InlineKeyboardButton(text="📁 नवीनतम फ़ाइल", callback_data="get_file_hi")
        btn_pass = InlineKeyboardButton(text="🔑 पासवर्ड", callback_data="get_pass_hi")
        btn_back = InlineKeyboardButton(text="🌍 भाषा बदलें", callback_data="change_lang")

    markup.add(btn_video, btn_file)
    markup.add(btn_pass)
    markup.add(btn_back)
    return markup

# الرد على أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_subscribed(user_id):
        bot.send_message(message.chat.id, "🌐 Please choose your language / الرجاء اختيار لغتك:", reply_markup=language_menu())
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        btn_ch1 = InlineKeyboardButton(text="📢 اشترك في القناة الأولى", url="https://t.me/ghostsxit1")
        btn_ch2 = InlineKeyboardButton(text="📢 اشترك في القناة الثانية", url="https://t.me/ghostsxit2")
        btn_check = InlineKeyboardButton(text="✅ تحقق الآن / Check Now", callback_data="check_sub")
        markup.add(btn_ch1, btn_ch2, btn_check)
        bot.send_message(message.chat.id, "⚠️ عذراً، يجب عليك الاشتراك في قنوات البوت أولاً لتتمكن من استخدامه!", reply_markup=markup)

# التقاط تحديثات الجروب الخاص تلقائياً بدون الحاجة لمعرفة الآيدي مسبقاً
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def update_data_from_group(message):
    global LATEST_VIDEO_URL, LATEST_FILE_URL, LATEST_PASSWORD, PRIVATE_GROUP_ID
    
    # التحقق من النص للتأكد أنها رسالة تحديث
    text = message.text if message.text else ""
    if "|" in text:
        parts = text.split('|')
        if len(parts) == 3:
            # حفظ آيدي الجروب تلقائياً لاعتماده كجروب الإدارة الرسمي
            if PRIVATE_GROUP_ID is None:
                PRIVATE_GROUP_ID = message.chat.id
                print(f"🎯 تم التعرف على آيدي الجروب الخاص بك بنجاح وهو: {PRIVATE_GROUP_ID}")
            
            # التأكد أن الرسالة قادمة من نفس الجروب المعتمد
            if message.chat.id == PRIVATE_GROUP_ID:
                LATEST_VIDEO_URL = parts[0].strip()
                LATEST_FILE_URL = parts[1].strip()
                LATEST_PASSWORD = parts[2].strip()
                bot.reply_to(message, "✅ تم تحديث البيانات بنجاح وبشكل تلقائي في البوت!")

# التحكم بالأزرار (Callback Queries)
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    if call.data == "check_sub":
        if is_user_subscribed(user_id):
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🌐 Please choose your language / الرجاء اختيار لغتك:", reply_markup=language_menu())
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القنوات بعد! فضلاً اشترك ثم اضغط تحقق مجدداً.", show_alert=True)
            
    elif not is_user_subscribed(user_id):
        bot.answer_callback_query(call.id, "⚠️ لقد غادرت إحدى القنوات، يرجى الاشتراك مجدداً للاستفادة من البوت.", show_alert=True)
        return

    # اللغات
    elif call.data == "lang_ar":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="مرحباً بك! اختر ما تريد من الأسفل:", reply_markup=options_menu("ar"))
    elif call.data == "lang_en":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Welcome! Choose from below:", reply_markup=options_menu("en"))
    elif call.data == "lang_hi":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="स्वागत है! नीचे से चुनें:", reply_markup=options_menu("hi"))
        
    elif call.data == "change_lang":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🌐 Choose language / اختر اللغة:", reply_markup=language_menu())

    # إرسال البيانات
    elif "get_video" in call.data:
        msg = {"ar": f"🎬 تفضل رابط آخر فيديو:\n{LATEST_VIDEO_URL}", "en": f"🎬 Here is the latest video link:\n{LATEST_VIDEO_URL}", "hi": f"🎬 यहाँ नवीनतम वीडियो लिंक है:\n{LATEST_VIDEO_URL}"}
        lang = call.data.split('_')[-1]
        bot.send_message(chat_id, msg[lang])
        bot.answer_callback_query(call.id)
        
    elif "get_file" in call.data:
        msg = {"ar": f"📁 تفضل رابط آخر ملف:\n{LATEST_FILE_URL}", "en": f"📁 Here is the latest file link:\n{LATEST_FILE_URL}", "hi": f"📁 यहाँ नवीनतम फ़ाइल लिंक है:\n{LATEST_FILE_URL}"}
        lang = call.data.split('_')[-1]
        bot.send_message(chat_id, msg[lang])
        bot.answer_callback_query(call.id)

    elif "get_pass" in call.data:
        msg = {"ar": f"🔑 كلمة السر للملف هي:\n`{LATEST_PASSWORD}`", "en": f"🔑 The file password is:\n`{LATEST_PASSWORD}`", "hi": f"🔑 फ़ाइल का पासवर्ड है:\n`{LATEST_PASSWORD}`"}
        lang = call.data.split('_')[-1]
        bot.send_message(chat_id, msg[lang], parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# حماية النصوص العامة للمستخدمين
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_private_text(message):
    if not is_user_subscribed(message.from_user.id):
        send_welcome(message)
    else:
        bot.reply_to(message, "⚠️ الرجاء استخدام الأزرار المتاحة للتنقل.")

print("👻 بوت GHOSTSXITBOT يعمل الآن بنجاح...")
bot.polling()
