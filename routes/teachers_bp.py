from flask import Blueprint
from controllers.teachers_controller import handle_login,handle_register,handle_create_class,handle_view_attendance
teachers_bp = Blueprint('teachers_bp', __name__)

teachers_bp.route('/login',methods=['POST'])(handle_login)
teachers_bp.route('/register',methods=['POST'])(handle_register)
teachers_bp.route('/create_class',methods=['POST'])(handle_create_class)
teachers_bp.route('/view_attendance',methods=['GET'])(handle_view_attendance)