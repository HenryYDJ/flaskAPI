from flask import jsonify, request
from app import db
from app.models import Student, ParentHood
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt_claims
from app.utils.utils import datetime_string_to_utc, Roles, Relationship
from app.dbUtils.dbUtils import query_validated_user, query_parent_hood, query_existing_student


# --------------------------Student Section----------------------------------------------------------
@bluePrint.route('/student', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # At least teacher is required
def add_student():
    """
    This api adds one student to the DB.
    """
    realName = request.json.get('realName', None)
    dob = request.json.get('dob', None)
    gender = request.json.get('gender', None)
    creator_id = get_jwt_identity().get('id')

    # Convert DOB to UTC format to store in DB
    dob_utc = datetime_string_to_utc(dob)
    student = Student()
    # Query the db to find the User who created this student.
    creator = query_validated_user(creator_id)
    if creator:
        # Check if the creator exists in the User table
        student.creator = creator
    else:
        return jsonify(message="Wrong input"), 400
    student.realName = realName
    student.dob = dob_utc
    student.gender = gender

    db.session.add(student)
    db.session.commit()
    return jsonify(message="Student created successfully"), 201


@bluePrint.route('/parent_hood', methods=['PUT'])
@jwt_roles_required(Roles.PARENT)  # At least parent is required
def update_parent_hood():
    """
    This api adds parenthood relationship to the DB.
    """
    parent_id = request.json.get('parent_id', None)
    student_id = request.json.get('student_id', None)
    relation = request.json.get('relation', None)

    parent_hood = query_parent_hood(parent_id, student_id)

    if parent_hood:
        parent_hood.relation = Relationship.get(relation)  # get the int value of the ralation from the relation dict
    else:
        parent_hood = ParentHood()
        parent_hood.parent = query_validated_user(parent_id)
        parent_hood.student = query_existing_student(student_id)
        parent_hood.relation = Relationship.get(relation)

    db.session.add(parent_hood)
    db.session.commit()
    return jsonify(message="Updated parent hood info"), 201


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
