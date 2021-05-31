from datetime import datetime

from flask import jsonify, request

from flask_jwt_extended import get_jwt_identity

from app import db
from app.models import CourseCredit, TakingClass, User
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_teacher, query_class_session, query_existing_user,\
    query_teacher_sessions, query_student_credit, query_taking_class, query_existing_teachers
from app.utils.utils import Roles, datetime_string_to_utc


# -------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/teacher', methods=['POST'])
@jwt_roles_required(Roles.EVERYBODY)
def register_teacher():
    """
    This api adds teacher's real information to the DB.
    """
    teacher_id = get_jwt_identity().get('id')

    teacher = query_existing_user(teacher_id)

    if teacher:
        teacher.phone = request.json.get('phone', None)
        teacher.real_name = request.json.get('real_name', None)
        teacher.gender = request.json.get('gender', None)
        teacher.language = request.json.get('language', 'CN')
        teacher.province = request.json.get('province', None)
        teacher.city = request.json.get('city', None)
        teacher.avatar = request.json.get('avatar', None)
        teacher.roles = Roles.TEACHER
        teacher.register_time = datetime.utcnow()
        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher created successfully"), 201
    else:
        return jsonify(message='User does not exist'), 409


@bluePrint.route('/approve_teacher', methods=['POST'])
@jwt_roles_required(Roles.PRINCIPLE)  # At least a principle can approve a teacher
def approve_teacher():
    """
    This api approves a registered teacher in the DB.
    """
    teacher_id = request.json.get('teacher_id', None)
    decision = request.json.get('decision', 0)

    teacher = query_existing_teacher(teacher_id)

    if teacher:
        teacher.approver_id = get_jwt_identity().get('id')
        teacher.approve_time = datetime.utcnow()
        teacher.validated = decision

        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher validation status changed"), 200
    else:
        return jsonify(message="No such teacher"), 201


@bluePrint.route('/teacher_sessions', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # At least a principle can approve a teacher
def get_teacher_sessions():
    """
    This api returns the teacher's sessions within a time frame.
    """
    teacher_id = get_jwt_identity().get('id')
    start_time = request.json.get('start_time', None)
    end_time = request.json.get('end_time', None)

    start_time_utc = datetime_string_to_utc(start_time)
    end_time_utc = datetime_string_to_utc(end_time)

    class_sessions = query_teacher_sessions(teacher_id, start_time_utc, end_time_utc)
    
    result = []
    for class_session, _ in class_sessions:
        result.append({"session_id": class_session.id, "course_name": class_session.course.name, "start_time": class_session.start_time, "duration": class_session.duration, "series_id": class_session.series_id})

    return jsonify(message=result), 201


@bluePrint.route('/attendance_call', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # At least a principle can approve a teacher
def attendance_call():
    """
    This api takes the attendance call and substracts a course credit from the student's course credits.
    """
    teacher_id = get_jwt_identity().get('id')
    session_id = request.json.get('session_id', None)
    students = request.json.get('student_ids', None)
    # Format of students message:
    # {
    # "session_id": 125,
    # "student_ids": [{"student_id": 1, "attended": true}, {"student_id": 3, "attended": true}, {"student_id": 4, "attended": true}]
    # }

    class_session = query_class_session(session_id)
    
    if class_session:
        # Add attendance call info to class session
        class_session.attendance_call = True
        class_session.attendance_teacher_id = teacher_id
        class_session.attendance_time = datetime.utcnow()

        db.session.add(class_session)
        db.session.commit()

        course_id = class_session.course.id
        for student in students:
            # Deduct credit from student credits
            student_id = student.get('student_id')
            attended = student.get('attended')
            course_credit = query_student_credit(student_id, course_id)
            if course_credit:
                course_credit.credit = course_credit.credit - 1
            else:
                course_credit = CourseCredit()
                course_credit.student_id = student_id
                course_credit.course_id = course_id
                course_credit.credit = -1
            db.session.add(course_credit)
            db.session.commit()

            # Add student taking class information to db if attended
            if attended:
                taking_class = query_taking_class(student_id, session_id)
                if taking_class:
                    taking_class.attended = True
                else:
                    taking_class = TakingClass()
                    taking_class.student_id = student_id
                    taking_class.session_id = session_id
                    taking_class.attended = True
                db.session.add(taking_class)
                db.session.commit()
        return jsonify(message="Attendance call success"), 201
    else:
        return jsonify(message="Cannot find class session"), 201


@bluePrint.route('/teachers', methods=['GET'])
@jwt_roles_required(Roles.ADMIN)
def get_teachers():
    """
    This api gets all undeleted teachers from the DB.
    """
    teachers = query_existing_teachers()
    return jsonify(message=[teacher.validate_info() for teacher in teachers]), 201


# @bluePrint.route('/dbutilstest', methods=['POST'])
# def dbutil_test():
#     """
#     This api registers one teacher to the DB.
#     """
#     user_id = request.json['id']
#     user = query_validated_user(user_id)
#     print(user)
#     return jsonify(message="success"), 201


# @bluePrint.route('/teacher', methods=['GET'])
# def get_teacher():
#     """
#     This api gets one teacher from the DB by the teacher's id.
#     """
#     # id = request.args.get('teacher_id', None)
#
#     # teacher = Teacher.query.filter_by(id=id, deleted=False).first()
#     # if teacher:
#     #     return jsonify(teacher_schema.dump(teacher))
#     # else:
#     #     return jsonify(message="Teacher not found"), 404
#
#     return jsonify(message="hi")
#
#
# @bluePrint.route('/teachers', methods=['GET'])
# def get_teachers():
#     """
#     This api gets all teachers from the DB.
#     """
#     teachers = Teacher.query.filter_by(deleted=False).all()
#     if teachers:
#         return jsonify(teachers_schema.dump(teachers))
#     else:
#         return jsonify(message="No teachers found"), 404
#
#
# @bluePrint.route('/teacher', methods=['PUT'])
# def update_teacher():
#     """
#     This api updates a teacher's information based on the teacher's id
#     """
#     id = request.args.get('teacher_id', None)
#
#     teacher = Teacher.query.filter_by(id=id, deleted=False).first()
#     if teacher:
#         teacher.name = request.json["name"]
#         db.session.add(teacher)
#         db.session.commit()
#         return jsonify(teacher_schema.dump(teacher))
#     else:
#         return jsonify(message="Teacher not found"), 404
#
#
# @bluePrint.route('/teacher', methods=['DELETE'])
# def delete_teacher():
#     """
#     This api deletes a teacher by teacher's id from the DB.
#     """
#     id = request.args.get('teacher_id', None)
#
#     teacher = Teacher.query.filter_by(id=id, deleted=False).first()
#     if teacher:
#         teacher.deleted = True
#         db.session.add(teacher)
#         db.session.commit()
#         return jsonify(teacher_schema.dump(teacher))
#     else:
#         return jsonify(message="Teacher not found"), 404
