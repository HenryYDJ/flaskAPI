from flask import jsonify, request
from app import db
from app.models import Course
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required


# -------------------Courses Section--------------------------------------------------------
@bluePrint.route('/course', methods=['POST'])
@jwt_roles_required(16)  # Only admin and above can add a course
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
