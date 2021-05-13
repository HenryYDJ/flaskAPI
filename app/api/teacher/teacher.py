from datetime import datetime

from flask import jsonify, request

from flask_jwt_extended import get_jwt_identity

from app import db
from app.models import User
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_teacher, query_validated_user, query_existing_phone_user, query_existing_user
from app.utils.utils import Roles


# -------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/teacher', methods=['POST'])
@jwt_roles_required(Roles.EVERYBODY)
def register_teacher():
    """
    This api adds teacher's real information to the DB.
    """
    teacher_id = get_jwt_identity().get('id')

    teacher = query_existing_user(teacher_id)
    phone = request.json['phone']

    if teacher:
        teacher.phone = request.json.get('phone', None)
        teacher.realName = request.json.get('realName', None)
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
    teacher_id = request.json['teacher_id']

    teacher = query_existing_teacher(teacher_id)

    if teacher:
        teacher.approver = get_jwt_identity().get('id')
        teacher.approve_time = datetime.utcnow()
        teacher.validated = True

        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher approved"), 200
    else:
        return jsonify(message="No such teacher"), 404


@bluePrint.route('/dbutilstest', methods=['POST'])
def dbutil_test():
    """
    This api registers one teacher to the DB.
    """
    user_id = request.json['id']
    user = query_validated_user(user_id)
    print(user)
    return jsonify(message="success"), 201


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
