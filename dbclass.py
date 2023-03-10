from motor import motor_asyncio 
from dotenv import load_dotenv
import os


db_url = os.getenv('db_url')
db = os.getenv('db')


class crudapi:
    
    def __init__(self) -> None:
        self.client = motor_asyncio.AsyncIOMotorClient(db_url)
        self.database = self.client[db]
    
    async def insert(self,collection,document):
        result = await self.database[collection].insert_one(document)
        return result

    async def find_one(self,collection,document):
        print(document)
        document = await self.database[collection].find_one(document)
        return document

    async def find_many(self,collection,document,condition={}):
        documents = []
        cursor = self.database[collection].find(document,condition)
        for document in await cursor.to_list(length=100):
            documents.append(document)
        return documents

    async def replace_one(self,collection,id,new_document):
        result = await self.database[collection].replace_one(id,new_document)
        return result

        
