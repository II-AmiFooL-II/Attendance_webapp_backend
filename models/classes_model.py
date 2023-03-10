from dbclass import crudapi
from dateutil import parser

class classes():
    def __init__(self,document) -> None:
        self.subject_id = -1
        self.subject = ""
        self.duration = document["duration"]
        self.start_time = parser.parse(document["start_time"])
        self.location = document["location"]
        self.attendance_before = parser.parse(document["attendance_before"])
    
    async def save(self):
        db_obj = crudapi()
        res = await db_obj.insert("classes",self.serialize)
        return res
    
    @property
    def serialize(self):
        return {
            "subject_id" : self.subject_id,
            "subject" : self.subject,
            "duration" : self.duration,
            "start_time" : self.start_time,
            "location" : self.location,
            "attendance_before" : self.attendance_before
        }

    @staticmethod
    def validate(document) -> bool:
        if "duration" not in document or "start_time" not  in document or "location" not  in document or "attendance_before" not  in document:
            return 1
        return 0

    @staticmethod
    async def find(document,condition={},table="classes"):
        db_obj = crudapi()
        res = await db_obj.find_many(table,document,condition)
        return res