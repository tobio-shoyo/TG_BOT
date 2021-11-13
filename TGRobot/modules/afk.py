import random, html

from TGRobot import dispatcher
from TGRobot.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from TGRobot.modules.sql import afk_sql as sql
from TGRobot.modules.users import get_user_id
from telegram import MessageEntity, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, MessageHandler, run_async

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:
        return

    notice = ""
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nYour afk reason was shortened to 100 characters."
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    fname = update.effective_user.first_name
    try:
        awee = [
            "{} will be busy with his irl GF!{}",
            "{} your friends here will miss you!{}",
            "{} is too tired to talk...{}",
            "{} wants to tour the hell!",
            "Cya 👋 {}!",
            "Byebye {}.",
            "See you later {}!",
            "Goodbye {}!",
            "Come back soon {}!",
            "Kthnxbye {}..",
        ]
        chosen_awee = random.choice(awee)
        update.effective_message.reply_text(chosen_awee.format(fname, notice))    
        #update.effective_message.reply_text("{} is now away!{}".format(fname, notice))
    except BadRequest:
        pass


@run_async
def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            options = [
                "{} is here to entertain us!",
                "{} is living his online life!",
                "{} ain't stalking anymore!",
                "{} is here to spam lemme call Durov!",
                "{} is here to summon the demons!",
                "{} the star of the group is here!",
                "Welcome sweetie! {}",
                "What are doing here {}?\nWhat about your Girlfriend!",
                "Beware! {} is here to summon the Demons...",
                "{} is here to talk shit and get banned...",
                "{} is here!",
                "{} is back!",
                "{} is now in the chat!",
                "{} is awake!",
                "{} is back online!",
                "{} is finally here!",
                "Welcome back! {}",
                "OwO {} is here!",
            ]
            chosen_option = random.choice(options)
            update.effective_message.reply_text(chosen_option.format(firstname))
        except:
            return


@run_async
def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            if ent.type != MessageEntity.MENTION:
                return

            user_id = get_user_id(message.text[ent.offset : ent.offset + ent.length])
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = bot.get_chat(user_id)
            except BadRequest:
                print("Error: Could not fetch userid {} for AFK module".format(user_id))
                return
            fst_name = chat.first_name

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, context, user_id, fst_name, userc_id):
    if sql.is_afk(user_id):
        user = sql.check_afk_status(user_id)
        if int(userc_id) == int(user_id):
            return
        if not user.reason:
            rest = [
            "{} is afk",
            "<b>{}</b> is busy right now. Please talk in a bag and when they come back you can just give him the bag!",
            "<b>{}</b> is away right now. If you need anything, leave a message after the beep:\n<code>beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep</code>!",
            "You just missed <b>{}</b>, next time aim better.",
            "{} will be back in a few minutes and if not...,\nwait longer.",
            "Roses are red,\nViolets are blue,\nLeave me a message,\nAnd {} will get back to you.",
            "If you haven't figured it out already,\n{} is not here.",
            "{} went that way\n---->",
            "{} went went this way\n<----",
            "{} is not here so stop writing to them,\nor else you will find yourself with a screen full of your own messages.",
            "Life is so short, there are so many things to do...\n{} is away doing one of them..",
            "{} is away from the keyboard at the moment, but if you'll scream loud enough at your screen, they might just hear you.",
         ]
            chosen_option = random.choice(rest)
            update.effective_message.reply_text(chosen_option.format(firstname))
        else:
            res = "{} is afk.\nReason: <code>{}</code>".format(
                html.escape(fst_name), html.escape(user.reason)
            )
            update.effective_message.reply_text(res, parse_mode="html")



AFK_HANDLER = DisableAbleCommandHandler("afk", afk)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"^(?i)brb(.*)$"), afk, friendly="afk"
)
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.group, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.all & Filters.group, reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__mod_name__ = "AFK"
__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (AFK_REGEX_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]

