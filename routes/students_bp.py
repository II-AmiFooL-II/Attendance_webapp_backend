from flask import Blueprint
from controllers.students_controller import handle_login,handle_register,handle_list_all_subjects,handle_view_attendance,handle_subscribe_to_class,handle_list_all_classes,handle_link_face,handle_attend_class

students_bp = Blueprint('students_bp', __name__)

students_bp.route('/login',methods=['POST'])(handle_login)
students_bp.route('/register',methods=['POST'])(handle_register)
students_bp.route('/list_all_subjects',methods=['GET'])(handle_list_all_subjects)
students_bp.route('/subscribe_to_class',methods=['POST'])(handle_subscribe_to_class)
students_bp.route('/list_all_classes',methods=['GET'])(handle_list_all_classes)
students_bp.route('/view_attendance',methods=['GET'])(handle_view_attendance)
students_bp.route('/link_face',methods=['POST'])(handle_link_face)
students_bp.route('/attend_class',methods=['POST'])(handle_attend_class)