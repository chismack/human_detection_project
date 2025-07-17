
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(_name_)

pi = pigpio.pi()
SERVO_PIN = 18
pi.set_mode(SERVO_PIN, pigpio.OUTPUT)

def move_servo(position: int):
    if position == 90:
        pulse_width = 2000
    elif position == 0:
        pulse_width = 1500
    elif position == -90:
        pulse_width = 1000
    else:
        return

    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    time.sleep(1)
    pi.set_servo_pulsewidth(SERVO_PIN, 0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot siap menerima perintah! Gunakan /lihathalaman untuk menggerakkan servo dan memotret.')

async def lihathalaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Lihat Halaman -90 Derajat", callback_data='-90')],
        [InlineKeyboardButton("Lihat Halaman 0 Derajat", callback_data='0')],
        [InlineKeyboardButton("Lihat Halaman 90 Derajat", callback_data='90')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Pilih sudut untuk melihat halaman:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    angle = int(query.data)
    move_servo(angle)
    requests.post('http://localhost:5000/capture')
    await query.edit_message_text(text=f'Servo bergerak ke {angle} derajat dan memotret gambar...')

def main():
    bot_token = '7154177514:AAF2QlEefSfRsQIFcVYjjGTH73a7tgGqgiY' 
    
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lihathalaman", lihathalaman))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if _name_ == '_main_':
    main()
