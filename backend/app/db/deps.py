from app.db.mongo import mongo_db


async def get_mongo():
    return mongo_db