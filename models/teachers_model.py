import re
from dbclass import crudapi


class teachers():
    def __init__(self,document) -> None:
        self.email = document["email"]
        self.password = document["password"]
        self.subject = document["subject"]
        self.uname = document["uname"]
        self.classes_taken = 0
        self.students_sub = dict()

    def check_params(self):
        if not type(self.subject) is str or not type(self.uname) is str:
            return 1
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            return 1
        return 0


    async def save(self):
        db_obj = crudapi()
        res = await db_obj.insert("teachers",self.serialize)
        return res
    
    @property
    def serialize(self):
        return {
            "uname" : self.uname,
            "email" : self.email,
            "password" : self.password,
            "subject" : self.subject,
            "classes_taken" : self.classes_taken,
            "students_sub" : self.students_sub
        }

    @staticmethod
    def validate(document) -> bool:
        if "email" not in document or "password" not in document or "subject" not  in document or "uname" not  in document:
            return 1
        return 0

    @staticmethod
    async def check_unique(document) -> bool:
        print(document)
        doc = {
            "$or":[
                {"uname":document["uname"]},
                {"email":document["email"]}
            ]
        }
        db_obj = crudapi()
        res = await db_obj.find_one("teachers",doc)
        return res

    @staticmethod
    async def find(document,condition={},table="teachers"):
        db_obj = crudapi()
        res = await db_obj.find_many(table,document,condition)
        return res

    @staticmethod
    async def replace(id,document):
        db_obj = crudapi()
        res = await db_obj.replace_one("teachers",id,document)
        return res


    

