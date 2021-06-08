from app.models import ParentHood
from datetime import datetime

from flask import jsonify, request

from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_user, query_unvalidated_parents, query_parent_hood,\
    query_parent_students
from app.utils.utils import Roles, VALIDATIONS


# -------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/parent', methods=['POST'])
@jwt_roles_required(Roles.EVERYBODY)
def register_parent():
    """
    This api adds parent's real information to the DB.
    """
    parent_id = get_jwt_identity().get('id')

    parent = query_existing_user(parent_id)

    if parent:
        parent.phone = request.json.get('phone', None)
        parent.nick_name = request.json.get('nick_name', None)
        parent.real_name = request.json.get('real_name', None)
        parent.gender = request.json.get('gender', None)
        parent.language = request.json.get('language', 'CN')
        parent.province = request.json.get('province', None)
        parent.city = request.json.get('city', None)
        parent.avatar = request.json.get('avatar', None)
        parent.roles = Roles.PARENT
        parent.register_time = datetime.utcnow()
        db.session.add(parent)
        db.session.commit()
        return jsonify(message="Parent created successfully"), 201
    else:
        return jsonify(message='User does not exist'), 409


@bluePrint.route('/validate_parent', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # Teacher and above can validate a parent
def validate_parent():
    """
    This api validates a parent in the DB.
    """
    parent_id = request.json.get('parent_id', None)
    decision = request.json.get('decision', 0)
    parent = query_existing_user(parent_id)

    if parent:
        parent.validated = decision
        parent.approver_id = get_jwt_identity().get('id')
        parent.approve_time = datetime.utcnow()
        db.session.add(parent)
        db.session.commit()
        return jsonify(message="Parent validation updated"), 201
    else:
        return jsonify(message='User does not exist'), 201


@bluePrint.route('/unvalidated_parents', methods=['GET'])
@jwt_roles_required(Roles.TEACHER)  # Teacher and above can get unvalidated parents.
def get_unvalidated_parents():
    """
    This API gets a list of all existing but unvalidated parents from the DB.
    """
    users = query_unvalidated_parents()

    if users:
        result = [user.validate_info() for user in users]
    else:
        result = []

    return jsonify(message=result), 201


@bluePrint.route('/bind_parents', methods=['POST'])
@jwt_required()
def bind_parents():
    """
    This API adds parent information into DB and binds a parent with a student.
    """
    parent_id = get_jwt_identity().get('id')
    student_id = request.json.get('student_id', None)
    teacher_id = request.json.get('teacher_id', None)
    relation = request.json.get('relation', None)

    parent_hood = query_parent_hood(parent_id, student_id)
    # First, find the parent based on the parent_id
    parent = query_existing_user(parent_id)
    if parent:
        # If the parent is already logged in, then add the info into db
        parent.phone = request.json.get('phone', None)
        parent.real_name = request.json.get('real_name', None)

        # The following info can be get from wechat
        parent.nick_name = request.json.get('nick_name', None)
        parent.gender = request.json.get('gender', None)
        parent.language = request.json.get('language', 'CN')
        parent.province = request.json.get('province', None)
        parent.city = request.json.get('city', None)
        parent.avatar = request.json.get('avatar', None)
        if parent.roles <= Roles.PARENT:
            # If the user's role is no larger than PARENT
            # Then change the user's role and register_time, validated status, approve_time, approver_id
            # Else, the following information stay the same.
            parent.roles = Roles.PARENT
            parent.register_time = datetime.utcnow()
            parent.validated = VALIDATIONS.APPROVED
            parent.approve_time = datetime.utcnow()
            parent.approver_id = teacher_id
        db.session.add(parent)
        db.session.commit()

        if parent_hood:
            # Second, find if there is already a parenthood record in the DB
            # If so, update the original parenthood to a new value
            original_relation = parent_hood.relation
            parent_hood.relation = relation
            db.session.add(parent_hood)
            db.session.commit()
            return jsonify(message="modified relation from " + str(original_relation) + " to " + str(relation)), 201
        else:
            # If no such parenthood in the DB
            # Create a new one in the DB
            parent_hood = ParentHood()
            parent_hood.parent_id = parent_id
            parent_hood.student_id = student_id
            parent_hood.relation = relation
            db.session.add(parent_hood)
            db.session.commit()
            return jsonify(message="Successfully binded parent"), 201
    else:
        return jsonify(message="No such user"), 201


@bluePrint.route('/parent_students', methods=['GET'])
@jwt_roles_required(Roles.PARENT)
def get_parent_students():
    """
    This api gets the students of a parent.
    """
    parent_id = get_jwt_identity().get('id')
    parent = query_existing_user(parent_id)
    if parent:
        students = query_parent_students(parent_id)
        return jsonify(message=[student.to_dict() for student, _ in students]), 201
    else:
        return jsonify(message='User does not exist'), 201