from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, LOGGER

class Bot(Client):

    def __init__(self):
        super().__init__(
        "LazyDeveloeprr_REQUEST_ACCEPTOR_BOT",
         api_id=API_ID,
         api_hash=API_HASH,
         bot_token=BOT_TOKEN,
         plugins=dict(root="plugins"),
         workers=50,
         sleep_threshold=10
        )
        self.LOGGER = LOGGER

    async def start(self):
            
        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
            
        print('Bot Started Successfully')

        self.LOGGER(__name__).info(f"Bot Running..!\n\n❤ with love  \n ıllıllı🚀🌟 L͙a͙z͙y͙D͙e͙v͙e͙l͙o͙p͙e͙r͙r͙ 🌟🚀ıllıllı")
        print(f"{me.first_name} 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 ⚡️⚡️⚡️")

    async def stop(self, *args):

        await super().stop()
        print('Bot Stopped Bye')

Bot().run()
