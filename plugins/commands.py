import asyncio 
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE, LOG_TEXT, JOINLINK,START_TEXT,ADMINS,BOT_USERNAME,ACCEPTED_TEXT
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    user_id = m.from_user.id
    name = m.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, name)

    # buttons
    channel_and_group_btn = [[
        InlineKeyboardButton("➕ Add me to your Channel ➕", url=f"https://t.me/{BOT_USERNAME}?startchannel=true")
    ], [
        InlineKeyboardButton("➕ Add me to your Group ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
    ]]

    lazydeveloper_btn = [[
        InlineKeyboardButton("🆎 ABOUT 🎃", callback_data="about_bot")
    ]]

    dynamic_buttons = []
    buttons = await db.get_buttons()

    for i in range(0, len(buttons), 2):
        row = [InlineKeyboardButton(buttons[i]["text"], url=buttons[i]["url"])]
        if i + 1 < len(buttons):
            row.append(InlineKeyboardButton(buttons[i+1]["text"], url=buttons[i+1]["url"]))
        dynamic_buttons.append(row)

    final_keyboard = channel_and_group_btn + dynamic_buttons + lazydeveloper_btn

    video = await db.get_start_video()
    joinlink = f"{JOINLINK}"

    if video:
        await c.send_video(
            user_id,
            video,
            caption=START_TEXT.format(m.from_user.mention, joinlink),
            reply_markup=InlineKeyboardMarkup(final_keyboard),
            supports_streaming=True,
            protect_content=True
        )
    else:
        await m.reply_photo(f"https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
            caption=f"{START_TEXT.format(m.from_user.mention, joinlink)}",
            reply_markup=InlineKeyboardMarkup(final_keyboard)
        )

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepte Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinpendings", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")

@Client.on_message(filters.command("set_video") & filters.user(ADMINS))
async def set_video(c, m):
    try:
        if not m.reply_to_message or not m.reply_to_message.video:
            return await m.reply("🎬 Reply to a video to set as the intro video.")

        file_id = m.reply_to_message.video.file_id
        await db.set_start_video(file_id)

        await m.reply("✅ Start intro video saved/updated successfully!")
    except Exception as e:
        await m.reply(f"⚠️ Error: {e}")

@Client.on_message(filters.command("add_btn") & filters.user(ADMINS))
async def add_btn_handler(client, message):
    await message.reply_text(
        "Send me button(s) in format:\n\n`Button Text - URL`\n\nYou can add multiple lines like this too.",
        quote=True
    )
    client.add_btn_state = message.from_user.id

@Client.on_message(filters.command("all_btns") & filters.user(ADMINS))
async def all_btns_handler(client, message):
    buttons = await db.get_buttons()

    if not buttons:
        await message.reply_text("No buttons added yet.")
        return

    keyboard = []
    for btn in buttons:
        btn_id = str(btn["_id"])
        keyboard.append([
            InlineKeyboardButton(btn["text"], url=btn["url"]),
            InlineKeyboardButton("✏️ Update", callback_data=f"update_btn_{btn_id}"),
            InlineKeyboardButton("❌ Delete", callback_data=f"delete_btn_{btn_id}")
        ])

    await message.reply_text(
        "🧩 All Buttons:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex("delete_btn_"))
async def delete_button(client, callback_query):
    btn_id = callback_query.data.split("_")[-1]

    await db.delete_button(btn_id)

    await callback_query.answer("Button deleted.")
    await callback_query.message.delete()

@Client.on_callback_query(filters.regex("home"))
async def home_handler(c, cb):
    try:
        # Default button
        lazydeveloper_btn = [[
            InlineKeyboardButton('🆎 ABOUT 🎃', callback_data="about_bot")
        ]]

        # ADD Channel / Group buttons
        channel_and_group_btn = [[
            InlineKeyboardButton(
                '➕ Add me to your Channel ➕',
                url=f"https://t.me/{BOT_USERNAME}?startchannel=true"
            )
        ], [
            InlineKeyboardButton(
                '➕ Add me to your Group ➕',
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ]]

        # Fetch dynamic buttons from DB (via db.py)
        dynamic_buttons = []
        buttons = await db.get_buttons()

        for i in range(0, len(buttons), 2):
            row = [
                InlineKeyboardButton(
                    buttons[i]["text"],
                    url=buttons[i]["url"]
                )
            ]
            if i + 1 < len(buttons):
                row.append(
                    InlineKeyboardButton(
                        buttons[i + 1]["text"],
                        url=buttons[i + 1]["url"]
                    )
                )
            dynamic_buttons.append(row)

        # Combine all buttons
        final_keyboard = channel_and_group_btn + dynamic_buttons + lazydeveloper_btn

        joinlink = f"{JOINLINK}"

        await cb.message.edit_text(
            START_TEXT.format(cb.message.from_user.mention, joinlink),
            reply_markup=InlineKeyboardMarkup(final_keyboard),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        print(e)


@Client.on_message(
    filters.text
    & filters.user(ADMINS)
    & ~filters.command(["start", "all_btns", "broadcast", "users", "accept_old_request"])
)
async def admin_text_handler(client, message):
    user_id = message.from_user.id

    # 🟩 UPDATE BUTTON LOGIC
    if getattr(client, "update_btn_state", None):
        state = client.update_btn_state

        if state["user"] == user_id:
            if " - " in message.text:
                text, url = message.text.split(" - ", 1)

                await db.update_button(
                    state["btn_id"],
                    text.strip(),
                    url.strip()
                )

                await message.reply_text("✅ Button updated.")
            else:
                await message.reply_text("⚠️ Invalid format. Use `Text - URL`")

            client.update_btn_state = None
            return

    # 🟨 ADD BUTTON LOGIC
    if getattr(client, "add_btn_state", None) == user_id:
        btns = message.text.strip().split("\n")
        inserted = 0

        for btn in btns:
            if " - " in btn:
                text, url = btn.split(" - ", 1)
                await db.add_button(text.strip(), url.strip())
                inserted += 1

        await message.reply_text(f"✅ {inserted} button(s) saved.")
        client.add_btn_state = None



@Client.on_chat_join_request()
async def req_accept(client, m):
    try:
        if NEW_REQ_MODE == False:
            return
        user_id = m.from_user.id
        chat_id = m.chat.id
        name = m.from_user.first_name

        # ✅ Add user if not exists (new db schema)
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, name)

        # ✅ Approve request
        await client.approve_chat_join_request(chat_id, user_id)

        # 🎃 ABOUT button
        lazydeveloper_btn = [[
            InlineKeyboardButton('🆎 ABOUT 🎃', callback_data="about_bot")
        ]]

        # ➕ Channel / Group buttons
        channel_and_group_btn = [[
            InlineKeyboardButton(
                '➕ Add me to your Channel ➕',
                url=f"https://t.me/{BOT_USERNAME}?startchannel=true"
            )
        ], [
            InlineKeyboardButton(
                '➕ Add me to your Group ➕',
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ]]

        # 🔘 Dynamic buttons (from db)
        dynamic_buttons = []
        buttons = await db.get_buttons()

        for i in range(0, len(buttons), 2):
            row = [
                InlineKeyboardButton(buttons[i]["text"], url=buttons[i]["url"])
            ]
            if i + 1 < len(buttons):
                row.append(
                    InlineKeyboardButton(buttons[i + 1]["text"], url=buttons[i + 1]["url"])
                )
            dynamic_buttons.append(row)

        final_keyboard = channel_and_group_btn + dynamic_buttons + lazydeveloper_btn

        # 🎬 Start video
        video = await db.get_start_video()
        joinlink = f"{JOINLINK}"

        if video:
            await client.send_video(
                chat_id=user_id,
                video=video,
                caption=ACCEPTED_TEXT.format(
                    user=m.from_user.mention,
                    chat=m.chat.title,
                    joinlink=joinlink
                ),
                reply_markup=InlineKeyboardMarkup(final_keyboard),
                supports_streaming=True,
                protect_content=True,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await client.send_message(
                chat_id=user_id,
                text=ACCEPTED_TEXT.format(
                    user=m.from_user.mention,
                    chat=m.chat.title,
                    joinlink=joinlink
                ),
                reply_markup=InlineKeyboardMarkup(final_keyboard),
                disable_web_page_preview=True
            )

    except Exception as e:
        print(e)




# @Client.on_chat_join_request(filters.group | filters.channel)
# async def approve_new(client, m):
#     if NEW_REQ_MODE == False:
#         return 
#     try:
#         if not await db.is_user_exist(m.from_user.id):
#             await db.add_user(m.from_user.id, m.from_user.first_name)
#             await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.mention, m.from_user.id))
#         await client.approve_chat_join_request(m.chat.id, m.from_user.id)
#         try:
#             await client.send_message(m.from_user.id, "**Hello {}!\nWelcome To {}**".format(m.from_user.mention, m.chat.title))
#         except:
#             pass
#     except Exception as e:
#         print(str(e))
#         pass
