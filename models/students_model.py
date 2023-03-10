import re
from dbclass import crudapi

class students():
    def __init__(self,document) -> None:
        self.email = document["email"]
        self.password = document["password"]
        self.roll_no = document["roll_no"]
        self.uname = document["uname"]
        self.classes_sub = dict()
        self.classes_attended = dict()

    def check_params(self):
        if not type(self.roll_no) is int or not type(self.uname) is str:
            return 1
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            return 1
        return 0


    async def save(self):
        db_obj = crudapi()
        res = await db_obj.insert("students",self.serialize)
        return res
    @property
    def serialize(self):
        return {
            "uname" : self.uname,
            "email" : self.email,
            "password" : self.password,
            "roll_no" : self.roll_no,
            "classes_sub" : self.classes_sub
        }

    @staticmethod
    def validate(document) -> bool:
        if "email" not in document or "password" not in document or "roll_no" not  in document or "uname" not  in document:
            return 1
        return 0

    @staticmethod
    async def check_unique(document) -> bool:
        print(document)
        doc = {
            "$or":[
                {"uname":document["uname"]},
                {"email":document["email"]},
                {"roll_no":document["roll_no"]}
            ]
        }
        db_obj = crudapi()
        res = await db_obj.find_one("students",doc)
        return res
    
    @staticmethod
    async def find(document,condition={},table="students"):
        db_obj = crudapi()
        res = await db_obj.find_many(table,document,condition)
        return res

    @staticmethod
    async def replace(id,document):
        db_obj = crudapi()
        res = await db_obj.replace_one("students",id,document)
        return res




    

