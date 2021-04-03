from flask import jsonify, request
from app import db
from app.models import Student, User, student_schema, students_schema
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required


# --------------------------Student Section----------------------------------------------------------
@bluePrint.route('/student', methods=['POST'])
@jwt_roles_required(4)  # At least teacher is required
def add_student():
    """
    This api adds one student to the DB.
    """

    # TODO:
    #   1. Figure out how to send Datetime in JSON request
    #   2. Parse the Date in JSON and decide the time zone
    #   3. Convert the datetime into UTC and store in DB

    realName = request.json['realName']
    dob = request.json['dob']
    gender = request.json['gender']

    student = Student()
    student.realName = realName
    student.dob = dob
    student.gender = gender

    db.session.add(student)
    db.session.commit()
    return jsonify(message="Student created successfully"), 201

#
# @bluePrint.route('/student', methods=['GET'])
# def get_student():
#     """
#     This api gets one student from the DB by the student's id.
#     """
#     id = request.args.get('student_id', None)
#
#     student = Student.query.filter_by(id=id, deleted=False).first()
#     if student:
#         return jsonify(student_schema.dump(student))
#     else:
#         return jsonify(message="Student not found"), 404
#
#
# @bluePrint.route('/students', methods=['GET'])
# def get_students():
#     """
#     This api gets all students from the DB.
#     """
#
#     students = Student.query.filter_by(deleted=False).all()
#     if students:
#         return jsonify(students_schema.dump(students))
#     else:
#         return jsonify(message="No students found"), 404
#
#
# @bluePrint.route('/student', methods=['PUT'])
# def update_student():
#     """
#     This api updates a student's information based on the student's id.
#     """
#     id = request.args.get('student_id', None)
#
#     student = Student.query.filter_by(id=id, deleted=False).first()
#     if student:
#         student.name = request.json["name"]
#         db.session.add(student)
#         db.session.commit()
#         return jsonify(student_schema.dump(student))
#     else:
#         return jsonify(message="Student not found"), 404
#
#
# @bluePrint.route('/student', methods=['DELETE'])
# def delete_student():
#     """
#     This api deletes a student by student's id from the DB.
#     """
#     id = request.args.get('student_id', None)
#
#     student = Student.query.filter_by(id=id, deleted=False).first()
#     if student:
#         student.deleted = True
#         db.session.add(student)
#         db.session.commit()
#         return jsonify(student_schema.dump(student))
#     else:
#         return jsonify(message="Student not found"), 404
