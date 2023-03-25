from flask import request,Response
from models.students_model import students
from models.teachers_model import teachers
from models.classes_model import classes
from facedetection import init_face,compare_face
from dotenv import load_dotenv
import json
import jwt
import os
from datetime import datetime, timedelta
from bson import ObjectId
import base64
import pickle
from bson.binary import Binary
from controllers.jwt_auth import jwt_auth_post,jwt_auth_get

secret_key = os.getenv('secret_key')

async def handle_login():
    data = request.get_json(force=True)
    print(data)
    if "uname" not in data["formData"] and "email" not in data["formData"] :
        return Response(response=json.dumps({"Error": "Insufficent creds"}), status=400,mimetype='application/json')
    if "password" not in data["formData"]:
        return Response(response=json.dumps({"Error": "Insufficent creds"}), status=400,mimetype='application/json')
    res = await students.find(data['formData'])
    #print(res)
    if res:
        token = jwt.encode({'uname': data["formData"]["uname"],'exp' : datetime.utcnow() + timedelta(minutes = 180) }, secret_key,'HS256')
        return Response(response=json.dumps({"No Error": "provided valid credentials","token":token}), status=200,mimetype='application/json')
    return Response(response=json.dumps({"Error": "Please provide valid credentials"}),status=401, mimetype='application/json')

async def handle_register():
    data = request.get_json(force=True)
    if students.validate(data["formData"]):
        return Response(response=json.dumps({"Error": "Insufficent details"}),status=400, mimetype='application/json')
    if await students.check_unique(data["formData"]):
        return Response(response=json.dumps({"Error": "duplicate details"}),status=400, mimetype='application/json')
    student = students(data["formData"])
    if student.check_params():
        return Response(response=json.dumps({"Error": "Improper details"}),status=400, mimetype='application/json')
    res = await student.save()
    if res:
        token = jwt.encode({'uname': data["formData"]["uname"],'exp' : datetime.utcnow() + timedelta(minutes = 180) }, secret_key,'HS256')
        return Response(response=json.dumps({"No Error": "saved details","token":token}), status=201,mimetype='application/json')
    return Response(response=json.dumps({"Error": "failed to save details"}),status=400, mimetype='application/json')

async def handle_list_all_subjects():
    data = request.args
    status,res = jwt_auth_get(data,request)
    if status:
        return res
    res = await students.find({},{"uname":1,"subject":1},"teachers")
    if res:
        return Response(response=json.dumps({"No Error": "fetched all subjects that are avilable","data":res},default=str), status=200,mimetype='application/json')
    return Response(response=json.dumps({"Error": "failed to fetch all subjects that are avilable"}),status=400, mimetype='application/json')

async def handle_subscribe_to_class():
    data = request.get_json(force=True)
    status,res = jwt_auth_post(data,request)
    if status:
        return res
    if "subject_id" not in data["formData"]:
        return Response(response=json.dumps({"Error": "Insufficent details"}),status=400, mimetype='application/json')
    
    t_res = await teachers.find({"_id":ObjectId(data["formData"]["subject_id"])},{"_id":0})
    if not t_res:
        return Response(response=json.dumps({"Error": "subject_id is wrong or failed fetch teacher details"}), status=400,mimetype='application/json')
    
    res = await students.find({"uname":data["formData"]["uname"]},{"_id":0})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch all student details"}),status=400, mimetype='application/json')
    if data["formData"]["subject_id"] in res[0]["classes_sub"]:
        return Response(response=json.dumps({"Error": "already subscribed"}),status=200, mimetype='application/json')
    
    res[0]["classes_sub"][data["formData"]["subject_id"]] = 0
    print(res)
    t_res[0]["students_sub"][data["formData"]["uname"]] = 0
    print(t_res)
    t_res = await teachers.replace({"uname":t_res[0]["uname"]},t_res[0])
    if not t_res:
        return Response(response=json.dumps({"Error": "failed save teacher details"}), status=400,mimetype='application/json')

    #print(res,{"uname":data["formData"]["uname"]})
    res = await students.replace({"uname":data["formData"]["uname"]},res[0])
    if not res:
        return Response(response=json.dumps({"Error": "failed to subscribe to class"}), status=400,mimetype='application/json')
    
    return Response(response=json.dumps({"No Error": "sucessfully subscribed to class"}), status=201,mimetype='application/json')


async def handle_list_all_classes():
    data = request.args
    status,res = jwt_auth_get(data,request)
    if status:
        return res
    res = await students.find({"uname":data["uname"]},{"classes_sub":1})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch all student details"}),status=400, mimetype='application/json')
    print(res)
    res = res[0]["classes_sub"]
    cond = []
    for i in res.keys():
        cond.append(ObjectId(i))
    cond = {"subject_id" : {"$in":cond}}
    cond2 = {"attendance_before":{"$gte":datetime.today()}}
    print(cond2)
    doc = {
        "$and": [
            cond,
            cond2
        ]
    }
    try:
        res = await classes.find(doc)
        return Response(response=json.dumps({"No Error": "all classes are","data":res},default=str), status=200,mimetype='application/json')
    except:
        return Response(response=json.dumps({"No Error": "failed to fetch classes"},default=str), status=400,mimetype='application/json')

async def handle_view_attendance():
    data = request.args
    status,res = jwt_auth_get(data,request)
    if status:
        return res
    res = await students.find({"uname":data["uname"]},{"classes_sub":1})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch students details"}), status=400,mimetype='application/json')
    condition = []
    #print(res)
    for key, value in res[0]["classes_sub"].items():
        condition.append(ObjectId(key))
    doc = {
        "_id":{"$in":condition}
    }
    print(doc)
    res2 = await students.find(doc,{"subject":1,"uname":1,"classes_taken":1,"_id":1},"teachers")
    #print(res2)
    if not res2:
        return Response(response=json.dumps({"Error": "failed to fetch teachers classes_sub"}), status=400,mimetype='application/json')
    attendance = []
    for key, value in res[0]["classes_sub"].items():
        for j in res2:
            if key == str(j["_id"]):
                val = {}
                val["_id"] = str(j["_id"])
                val["subject"] = j["subject"]
                val["uname"] = j["uname"]
                val["classes_taken"] = j["classes_taken"]
                val["classes_attended"] = value
                attendance.append(val)
    return Response(response=json.dumps({"No Error": "fetched student attendance details","data":attendance},default=str), status=200,mimetype='application/json')

async def handle_link_face():
    data = request.get_json(force=True)
    status,res = jwt_auth_post(data,request)
    if status:
        return res
    if "img" not in data["formData"]:
        return Response(response=json.dumps({"Error": 'img is missing !!'}), status=401,mimetype='application/json')
    
    res = await students.find({"uname":data["formData"]["uname"]},{"_id":0})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch all student details"}),status=400, mimetype='application/json')
    if "face_encode" in res[0]:
        return Response(response=json.dumps({"Error": "face already Linked"}),status=200, mimetype='application/json')
    
    name = "./images/" + data["formData"]["uname"] +".jpg"
    decodeit = open(name,"wb+")
    decodeit.write(base64.b64decode((data["formData"]["img"][23:])))
    decodeit.close()

    status,encode = init_face(name)
    if status == -1:
        os.remove(name)
        return Response(response=json.dumps({"Error": 'failed to save face !!'}), status=401,mimetype='application/json')
    
    res[0]["face_encode"] = Binary(pickle.dumps(encode, protocol=2), subtype=128 )
    #print(res,{"uname":data["formData"]["uname"]})
    res = await students.replace({"uname":data["formData"]["uname"]},res[0])
    if res:
        return Response(response=json.dumps({"No Error": "sucessfully Linked Face"}), status=201,mimetype='application/json')
    return Response(response=json.dumps({"Error": "failed to Link Face"}), status=400,mimetype='application/json')

async def handle_attend_class():
    data = request.get_json(force=True)
    status,res = jwt_auth_post(data,request)
    if status:
        return res
    if "img" not in data["formData"] or "subject_id" not  in data["formData"] or "class_id" not  in data["formData"]:
        return Response(response=json.dumps({"Error": 'details are missing !!'}), status=401,mimetype='application/json')

    res = await students.find({"uname":data['formData']["uname"]},{"_id":0})
    if not res:
        return Response(response=json.dumps({"Error": "failed to fetch student details"}), status=400,mimetype='application/json')
    
    if  data["formData"]["class_id"] in res[0]["classes_attended"]:
        return Response(response=json.dumps({"Error": "class already attended"}), status=400,mimetype='application/json')

    if data["formData"]["subject_id"] not in res[0]["classes_sub"]:
        return Response(response=json.dumps({"Error": "need to subscribe before attending"}), status=400,mimetype='application/json')

    if "face_encode" not  in res[0]:
        return Response(response=json.dumps({"Error": "need to link face before attending"}), status=400,mimetype='application/json')
    
    t_res = await teachers.find({"_id":ObjectId(data["formData"]["subject_id"])},{"_id":0})
    if not t_res:
        return Response(response=json.dumps({"Error": "teachers details does not exist or failed fetch teacher details"}), status=400,mimetype='application/json')
    if data["formData"]["uname"] not  in t_res[0]["students_sub"]:
        return Response(response=json.dumps({"Error": "student not in teachers records"}), status=400,mimetype='application/json')

    cond = {"_id" : ObjectId(data["formData"]["class_id"]) }
    cond2 = {"attendance_before":{"$gte":datetime.today()}}

    #print(cond2)
    doc = {
        "$and": [
            cond,
            cond2
        ]
    }
    c_res = await classes.find(doc)
    if not c_res:
        return Response(response=json.dumps({"Error": "class does not exist or failed to fetch all classes"}), status=400,mimetype='application/json')
    
    temp = open("./images/temp.jpg","wb+")
    temp.write(base64.b64decode((data["formData"]["img"][23:])))
    temp.close()

    if compare_face("./images/temp.jpg",pickle.loads(res[0]["face_encode"])):
        return Response(response=json.dumps({"Error": "invalid image"}), status=400,mimetype='application/json')
    
    res[0]["classes_sub"][data["formData"]["subject_id"]] += 1
    res[0]["classes_attended"][data["formData"]["class_id"]] = 1
    res = await students.replace({"uname":data["formData"]["uname"]},res[0])
    if not res:
        return Response(response=json.dumps({"Error": "failed save details"}), status=400,mimetype='application/json')
    
    t_res[0]["students_sub"][data["formData"]["uname"]] +=1
    t_res = await teachers.replace({"_id":ObjectId(data["formData"]["subject_id"])},t_res[0])
    if not t_res:
        return Response(response=json.dumps({"Error": "failed save teacher details"}), status=400,mimetype='application/json')
    return Response(response=json.dumps({"No Error": "Marked attendance"}), status=200,mimetype='application/json')