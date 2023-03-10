from flask import request,Response
from models.teachers_model import teachers
from models.classes_model import classes
from dotenv import load_dotenv
import json
import jwt
import os
from datetime import datetime, timedelta,timezone
from dateutil import parser
from bson import ObjectId

secret_key = os.getenv('secret_key')

async def handle_login():
    data = request.get_json(force=True)
    print(data)
    #print(parser.parse(data["value"][:-1]))
    if "uname" not in data["formData"] and "email" not in data["formData"] :
        return Response(response=json.dumps({"Error": "Insufficent creds"}), status=400,mimetype='application/json')
    if "password" not in data["formData"]:
        return Response(response=json.dumps({"Error": "Insufficent creds"}), status=400,mimetype='application/json')
    res = await teachers.find(data['formData'])
    #print(res)
    if res:
        token = jwt.encode({'uname': data["formData"]["uname"],'exp' : datetime.utcnow() + timedelta(minutes = 180) }, secret_key,'HS256')
        return Response(response=json.dumps({"No Error": "provided valid credentials","token":token}), status=200,mimetype='application/json')
    return Response(response=json.dumps({"Error": "Please provide valid credentials"}),status=401, mimetype='application/json')

async def handle_register():
    data = request.get_json(force=True)
    if teachers.validate(data["formData"]):
        return Response(response=json.dumps({"Error": "Insufficent details"}),status=400, mimetype='application/json')
    if await teachers.check_unique(data["formData"]):
        return Response(response=json.dumps({"Error": "duplicate details"}),status=400, mimetype='application/json')
    teacher = teachers(data["formData"])
    if teacher.check_params():
        return Response(response=json.dumps({"Error": "Improper details"}),status=400, mimetype='application/json')
    res = await teacher.save()
    if res:
        token = jwt.encode({'uname': teacher.uname,'exp' : datetime.utcnow() + timedelta(minutes = 180) }, secret_key,'HS256')
        return Response(response=json.dumps({"No Error": "saved details","token":token}), status=201,mimetype='application/json')
    return Response(response=json.dumps({"Error": "failed to save details"}),status=400, mimetype='application/json')

async def handle_create_class():
    data = request.get_json(force=True)
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not  token:
            return Response(response=json.dumps({"Error": 'Token is missing !!'}), status=401,mimetype='application/json')
        print(token)
        token = jwt.decode(token, secret_key,algorithms=['HS256'])
        if "uname" not in data['formData'] or token['uname']!=data['formData']["uname"]:
            return Response(response=json.dumps({"Error": 'Token details missmatch !!'}), status=401,mimetype='application/json')
    if classes.validate(data["formData"]):
        return Response(response=json.dumps({"Error": 'Insufficent creds'}), status=401,mimetype='application/json')
    class_obj = classes(data["formData"])
    res = await teachers.find({"uname":data['formData']['uname']},{"subject":1,"_id":1})
    class_obj.subject = res[0]['subject']
    class_obj.subject_id = ObjectId(res[0]['_id'])
    res = await class_obj.save()
    if not res:
        return Response(response=json.dumps({"Error": "failed to save class details"}),status=400, mimetype='application/json')
        
    res = await teachers.find({"uname":data['formData']["uname"]},{"_id":0})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch teacher details"}),status=400, mimetype='application/json')
    res[0]["classes_taken"] += 1
    res = await teachers.replace({"uname":data['formData']["uname"]},res[0])
    if not res:
        return Response(response=json.dumps({"Error": "failed to save teacher details"}),status=400, mimetype='application/json')
    return Response(response=json.dumps({"No Error": "saved class details"}), status=201,mimetype='application/json')


async def handle_view_attendance():
    data = request.get_json(force=True)
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not  token:
            return Response(response=json.dumps({"Error": 'Token is missing !!'}), status=401,mimetype='application/json')
        print(token)
        token = jwt.decode(token, secret_key,algorithms=['HS256'])
        if "uname" not in data['formData'] or token['uname']!=data['formData']["uname"]:
            return Response(response=json.dumps({"Error": 'Token details missmatch !!'}), status=401,mimetype='application/json')
    
    res = await teachers.find({"uname":data["formData"]["uname"]},{"_id":0})

    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch teacher details"}),status=400, mimetype='application/json')
    attendance = []
    return Response(response=json.dumps({"No Error": "fetched teacher details","attendence_data":res[0]["students_sub"],"classes_taken":res[0]["classes_taken"]}),status=200, mimetype='application/json')


