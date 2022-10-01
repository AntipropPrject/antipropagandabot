from datetime import datetime

from aiogram.types import Update, Message, User, Chat


def fake_message(user: User, text: str):
    return Update(
        update_id=100000,
        message=Message(
            message_id=1,
            date=datetime.utcnow(),
            from_user=user,
            chat=Chat(
                id=user.id,
                type="private"
            ),
            text=text
        )
    )
