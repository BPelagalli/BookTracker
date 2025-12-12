import os
import time
import random
import schedule
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# SMS notifications library
messages = [
    "Time for today’s story! A few minutes of reading makes a lifetime of difference 📚",
    "You’re on your way to 1,000 books! Let’s add one more to the count today 💫",
    "Story time is calling! Grab your little reader and an adventure awaits! 🏔️",
    "Time to cozy up and read with your little one! Let’s add one more story before lights out 🌙",
    "Don’t forget today’s story! Every book gets you closer to your goal of 1,000 books before kindergarten 🍎",
    "Time spent reading is never wasted. Shall we add another book to your count now? 📖",
    "Pause your day, open a book, and watch their imagination bloom 🌷",
    "Open up a book with your little one and blast off on an adventure! 🚀"
]


def send_daily_sms():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    to_numbers = [n.strip() for n in os.getenv("RECIPIENT_PHONE_NUMBER").split(",")]

    client = Client(account_sid, auth_token)
    message_body = random.choice(messages)

    for number in to_numbers:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=number
        )
        print(f"Sent message: {message.sid}")
        





if __name__ == "__main__":
    send_daily_sms()