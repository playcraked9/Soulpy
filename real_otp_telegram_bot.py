import logging
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = 'ACdb504a3a22a24d6dcd969f4cf9a6ddb6'
TWILIO_AUTH_TOKEN = '079c500e4cc0fbcce41e2f1d3a4b736f'
TWILIO_PHONE_NUMBER = '+12093539917'

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Store the generated OTP for each user
user_otps = {}

# Function to handle the /start command
def start(update, context):
    update.message.reply_text("Welcome! Please use /getotp <phone_number> to receive an OTP via SMS.")

# Function to generate and send OTP via SMS
def get_otp(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Please provide your phone number using the format: /getotp <phone_number>")
        return

    phone_number = context.args[0]

    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)

    # Store the OTP for the user (Telegram user ID as the key)
    user_otps[update.message.chat_id] = otp

    try:
        # Send the OTP via SMS using Twilio
        message = client.messages.create(
            body=f"Your OTP code is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        update.message.reply_text(f"OTP has been sent to {phone_number}. Please check your SMS.")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        update.message.reply_text("Failed to send OTP. Please try again later.")

# Function to verify the OTP entered by the user
def verify_otp(update, context):
    if len(context.args) != 1:
        update.message.reply_text("Please provide the OTP using the format: /verifyotp <otp>")
        return

    user_id = update.message.chat_id
    entered_otp = int(context.args[0])

    # Check if the OTP matches
    if user_id in user_otps and user_otps[user_id] == entered_otp:
        update.message.reply_text("✅ OTP is valid!")
        # Remove OTP after successful verification
        del user_otps[user_id]
    else:
        update.message.reply_text("❌ Invalid OTP. Please try again.")

# Main function to start the bot
def main():
    TOKEN = '7729338094:AAH0-e-bVHjOA_V-ykT6z9i1BfFiamchhuo'  # Replace with your Telegram bot token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the /start, /getotp, and /verifyotp commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getotp", get_otp))
    dp.add_handler(CommandHandler("verifyotp", verify_otp))

    # Start the bot
    updater.start_polling()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
