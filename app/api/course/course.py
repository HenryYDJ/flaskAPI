from flask import jsonify, request
from app import db
from app.models import Course, ClassSession
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_course, query_course_credit
from app.utils.utils import datetime_string_to_utc, Roles


# -------------------Courses Section--------------------------------------------------------
@bluePrint.route('/course', methods=['POST'])
@jwt_roles_required(Roles.ADMIN)  # Only admin and above can add a course
def add_course():
    """
    This api adds one course to the DB.
    """
    name = request.json['name']

    already_existed = Course.query.filter_by(name=name, deleted=False).first()
    if already_existed:
        return jsonify(message='The course already exists'), 409
    else:
        course = Course(name=name)
        db.session.add(course)
        db.session.commit()
        return jsonify(message="Course created successfully"), 201


@bluePrint.route('/class_session', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # Only teacher and above can add a course
def add_class_session():
    """
    This api adds one class session to the DB.
    """
    course_id = request.json.get('course_id', None)
    course = query_existing_course(course_id)
    if course:
        class_session = ClassSession()
        class_session.course = course
        class_session.startTime = datetime_string_to_utc(request.json.get('start_time', None))
        class_session.endTime = datetime_string_to_utc(request.json.get('end_time', None))
        class_session.info = request.json.get('info', None)

        db.session.add(class_session)
        db.session.commit()
        return jsonify(message="Class session added successfully"), 201
    else:
        return jsonify(message="Course does not exist"), 400


@bluePrint.route('/course_credit', methods=['PUT'])
@jwt_roles_required(Roles.PRINCIPLE)  # Only teacher and above can add a course
def update_course_credit():
    """
    This api updates the course credit of a student in the DB.
    """
    course_id = request.json.get('course_id', None)
    student_id = request.json.get('student_id', None)
    credit = request.json.get('course_credit', None)

    course_credit = query_course_credit(course_id, student_id)

    if course_credit:
        course_credit.credit = credit
        db.session.add(course_credit)
        db.session.commit()
        return jsonify(message="Course credit updated"), 201
    else:
        return jsonify(message="Course credit does not exist"), 400

# @bluePrint.route('/course', methods=['GET'])
# def get_course():
#     """
#     This api gets one course from the DB by the course's id.
#     """
#     id = request.args.get('course_id', None)
#
#     course = Course.query.filter_by(id=id, deleted=False).first()
#     if course:
#         return jsonify(course_schema.dump(course))
#     else:
#         return jsonify(message="Course not found"), 404
#
#
# @bluePrint.route('/courses', methods=['GET'])
# def get_courses():
#     """
#     This api gets all courses from the DB.
#     """
#     courses = Course.query.filter_by(deleted=False).all()
#     if courses:
#         return jsonify(courses_schema.dump(courses))
#     else:
#         return jsonify(message="No courses found"), 404
#
#
# @bluePrint.route('/course', methods=['PUT'])
# def update_course():
#     """
#     This api updates a course's information based on the course's id
#     """
#     id = request.args.get('course_id', None)
#
#     course = Course.query.filter_by(id=id, deleted=False).first()
#     if course:
#         course.name = request.json["name"]
#         db.session.add(course)
#         db.session.commit()
#         return jsonify(course_schema.dump(course))
#     else:
#         return jsonify(message="Course not found"), 404
#
#
# @bluePrint.route('/course', methods=['DELETE'])
# def delete_course():
#     """
#     This api deletes a course by course's id from the DB.
#     """
#     id = request.args.get('course_id', None)
#
#     course = Course.query.filter_by(id=id, deleted=False).first()
#     if course:
#         course.deleted = True
#         db.session.add(course)
#         db.session.commit()
#         return jsonify(course_schema.dump(course))
#     else:
#         return jsonify(message="Course not found"), 404
