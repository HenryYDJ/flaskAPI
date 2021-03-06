from flask import jsonify, request
from app import db
from app.models import Student, ParentHood
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from datetime import date, datetime
from flask_jwt_extended import get_jwt_identity
from app.utils.utils import Roles, Relationship, datetime_string_to_naive, datetime_string_to_utc
from app.dbUtils.dbUtils import query_validated_user, query_parent_hood, query_existing_student,\
    query_all_existing_students, query_student_parents, query_student_credits, query_student_sessions
from datetime import datetime

# --------------------------Student Section----------------------------------------------------------
@bluePrint.route('/student', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # At least teacher is required
def add_student():
    """
    This api adds one student to the DB.
    """
    real_name = request.json.get('real_name', None)
    dob = request.json.get('dob', None)
    gender = request.json.get('gender', None)
    creator_id = get_jwt_identity().get('id')

    # Convert DOB to naive datetime format to store in DB
    dob_naive = datetime_string_to_naive(dob)
    
    # Create student instance, fill in the values and add to DB
    student = Student()
    # Query the db to find the User who created this student.
    creator = query_validated_user(creator_id)
    if creator:
        # Check if the creator exists in the User table
        student.creator = creator
    else:
        return jsonify(message="Wrong input"), 400
    student.real_name = real_name
    student.dob = dob_naive
    student.gender = gender
    student.create_time = datetime.utcnow()

    db.session.add(student)
    db.session.commit()
    return jsonify(message="Student created successfully"), 201


@bluePrint.route('/parent_hood', methods=['PUT'])
@jwt_roles_required(Roles.PARENT)  # At least parent is required
def update_parent_hood():
    """
    This api adds parenthood relationship to the DB.
    """
    student_id = request.json.get('student_id', None)
    relation = request.json.get('relation', None)
    parent_id = get_jwt_identity().get('id')

    parent_hood = query_parent_hood(parent_id, student_id)

    if parent_hood:
        parent_hood.relation = relation  # get the int value of the ralation from the relation dict
    else:
        parent_hood = ParentHood()
        parent_hood.parent = query_validated_user(parent_id)
        parent_hood.student = query_existing_student(student_id)
        parent_hood.relation = relation

    db.session.add(parent_hood)
    db.session.commit()
    return jsonify(message="Updated parent hood info"), 201


@bluePrint.route('/student_parents', methods=['POST'])
@jwt_roles_required(Roles.PARENT)  # At least parent is required
def get_student_parents():
    """
    This api returns a list of parents and the relationship of the student_id
    """
    student_id = request.json.get('student_id', None)
    parents = query_student_parents(student_id)
    result = []
    for name, relation in parents:
        result.append({"parent_name": name, "relation": relation})
    return jsonify(message=result), 201


@bluePrint.route('/student_credits', methods=['POST'])
@jwt_roles_required(Roles.PARENT)  # Only parent and up can see a student's remaining credits
def get_student_credits():
    """
    This api gets the student's remaining credits.
    """
    # Check the requester's role, if only a parent, then can only access his/her own children course credits.
    # requester_id = get_jwt_identity().get('id')
    # requester = query_validated_user(requester_id)
    # student_id = request.json.get('student_id', None)
    # Parents can only get their associated students' course credits.
    # if requester.get_role_value() <= Roles.PARENT:

    student_id = request.json.get('student_id', None)
    course_credits = query_student_credits(student_id)
    result = []
    for course_name, course_credit in course_credits:
        result.append({"course_name": course_name, "course_credit": course_credit})
    return jsonify(message=result), 201


@bluePrint.route('/students', methods=['GET'])
@jwt_roles_required(Roles.TEACHER)
def get_students():
    """
    This api gets all undeleted students from the DB.
    """
    students = query_all_existing_students()
    if students:
        return jsonify(message=[student.to_dict() for student in students]), 201
    else:
        return jsonify(message=[]), 201


@bluePrint.route('/student_sessions', methods=['POST'])
@jwt_roles_required(Roles.PARENT)
def get_student_sessions():
    """
    This api returns the student's sessions within a time frame.
    """
    student_id = request.json.get('student_id', None)
    start_time = request.json.get('start_time', None)
    end_time = request.json.get('end_time', None)

    start_time_utc = datetime_string_to_utc(start_time)
    end_time_utc = datetime_string_to_utc(end_time)

    class_sessions = query_student_sessions(student_id, start_time_utc, end_time_utc)
    
    result = []
    for class_session, taking_class in class_sessions:
        result.append({"session_id": class_session.id, "course_name": class_session.course.name, "start_time": class_session.start_time, "duration": class_session.duration,\
            "series_id": class_session.series_id, "attended": taking_class.attended})

    return jsonify(message=result), 201
