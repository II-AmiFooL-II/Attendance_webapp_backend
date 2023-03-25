from flask import Response
import json
import jwt
import os

secret_key = os.getenv('secret_key')

def jwt_auth_post(data,request):
    try:
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            token = jwt.decode(token, secret_key,algorithms=['HS256'])
            if "uname" not in data['formData'] or token['uname']!=data['formData']["uname"]:
                return 1,Response(response=json.dumps({"Error": 'Token details missmatch !!'}), status=401,mimetype='application/json')
            return 0,None
        else:
            return 1,Response(response=json.dumps({"Error": 'Token is missing !!'}), status=401,mimetype='application/json')
    except:
        return 1,Response(response=json.dumps({"Error": 'Invalid Token!!'}), status=401,mimetype='application/json')
def jwt_auth_get(data,request):
    try:
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            token = jwt.decode(token, secret_key,algorithms=['HS256'])
            if "uname" not in data or token['uname']!=data["uname"]:
                return 1,Response(response=json.dumps({"Error": 'Token details missmatch !!'}), status=401,mimetype='application/json')
            return 0,None
        else:
            return 1,Response(response=json.dumps({"Error": 'Token is missing !!'}), status=401,mimetype='application/json')
    except:
        return 1,Response(response=json.dumps({"Error": 'Invalid Token!!'}), status=401,mimetype='application/json')