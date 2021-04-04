from flask import jsonify, request
from app import db
from app.models import User
from app.api import bluePrint
from datetime import datetime
import pytz
from app.api.auth.auth_utils import jwt_roles_required

from app.dbUtils.dbUtils import query_existing_user, query_validated_user, query_existing_phone_user


# -------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/teacher', methods=['POST'])
def register_teacher():
    """
    This api registers one teacher to the DB.
    """
    phone = request.json['phone']

    # First check if the phone number or email already exists.
    already_existed = query_existing_phone_user(phone)
    if already_existed:
        return jsonify(message='The phone number or email is already used.'), 409
    else:
        teacher = User()
        teacher.phone = phone
        teacher.realName = request.json['realName']
        teacher.set_pwhash(request.json['password'])
        teacher.register_time = datetime.utcnow()
        teacher.roles = 4  # The role number for teachers are >= 4
        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher created successfully"), 201


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
