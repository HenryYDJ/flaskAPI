from app.models import ParentHood
from datetime import datetime

from flask import jsonify, request

from flask_jwt_extended import get_jwt_identity

from app import db
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_user, query_unvalidated_parents, query_parent_hood
from app.utils.utils import Roles


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
@jwt_roles_required(Roles.PARENT)  # Bind the parents to the students.
def bind_parents():
    """
    This API binds a parent with the student.
    """
    parent_id = get_jwt_identity().get('id')
    student_id = request.json.get('student_id', None)
    relation = request.json.get('relation', None)

    parent_hood = query_parent_hood(parent_id, student_id)

    if parent_hood:
        original_relation = parent_hood.relation
        parent_hood.relation = relation
        db.session.add(parent_hood)
        db.session.commit()
        return jsonify(message="modified relation from " + str(original_relation) + " to " + str(relation)), 201
    else:
        parent_hood = ParentHood()
        parent_hood.parent_id = parent_id
        parent_hood.student_id = student_id
        parent_hood.relation = relation
        db.session.add(parent_hood)
        db.session.commit()
        return jsonify(message="Successfully binded parent"), 201