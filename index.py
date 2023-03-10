from flask import Flask,request,Response
from flask_cors import CORS
from dbclass import crudapi
from routes.students_bp import students_bp
from routes.teachers_bp import teachers_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(students_bp, url_prefix='/students')
app.register_blueprint(teachers_bp, url_prefix='/teachers')

@app.route("/")
def index():
    print("hi")
    return "<p>Hello, World!</p>"
