


async def media_wizard(self,
        video: Union[InputFile, str],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        thumb: Optional[Union[InputFile, str]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = UNSET,
        supports_streaming: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_markup: Optional[
            Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
        ] = None,
    ) -> SendVideo:
        """
        Answer with video

        :param video:
        :param duration:
        :param width:
        :param height:
        :param thumb:
        :param caption:
        :param parse_mode:
        :param supports_streaming:
        :param disable_notification:
        :param reply_markup:
        :return:
        """
        from ..methods import SendVideo

        return SendVideo(
            chat_id=self.chat.id,
            video=video,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            caption=caption,
            parse_mode=parse_mode,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            reply_to_message_id=None,
            reply_markup=reply_markup,
        )