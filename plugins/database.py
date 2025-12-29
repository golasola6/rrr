import motor.motor_asyncio
from bson import ObjectId
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

        self.buttons = self.db.buttons
        self.assets = self.db.assets

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user['session']
# ───────────── BUTTONS ─────────────
    async def get_buttons(self):
        return await self.buttons.find().to_list(None)

    async def add_button(self, text, url):
        await self.buttons.insert_one({"text": text, "url": url})

    async def delete_button(self, btn_id):
        await self.buttons.delete_one({"_id": ObjectId(btn_id)})

    async def update_button(self, btn_id, text, url):
        await self.buttons.update_one(
            {"_id": ObjectId(btn_id)},
            {"$set": {"text": text, "url": url}}
        )

    # ───────────── ASSETS ─────────────
    async def get_start_video(self):
        data = await self.assets.find_one({"_id": "start_video"})
        return data["video"] if data else None

    async def set_start_video(self, file_id):
        await self.assets.update_one(
            {"_id": "start_video"},
            {"$set": {"video": file_id}},
            upsert=True
        )

db = Database(DB_URI, DB_NAME)
