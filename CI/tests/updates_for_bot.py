import os
from datetime import datetime

from aiogram.types import Update, Chat, User, Message

test_message = Update(
    update_id=1,
    message=Message(
        message_id=1,
        date=datetime.utcnow(),
        from_user=User(
            id=os.getenv('TEST_USER_ID'),
            is_bot=False,
            first_name=''
        ),
        chat=Chat(
            id=os.getenv('TEST_CHANNEL_ID'),
            type="channel"
        ),
        text='/smoke_test'
    )
)