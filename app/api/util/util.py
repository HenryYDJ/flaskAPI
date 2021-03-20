from flask import jsonify, request
from app import db
from app.models import Teacher, teacher_schema, teachers_schema
from app.api import bluePrint
from datetime import datetime

@bluePrint.route('/util/coverpic', methods=['POST'])
def add_cover_pic():
    """
    This api registers one teacher to the DB.
    """
    phone = request.json['phone']
    email = request.json['email']

    # First check if the phone number or email already exists.
    already_existed = Teacher.query.filter(Teacher.deleted==False).filter((Teacher.phone==phone)|(Teacher.email==email)).first()
    if already_existed:
        return jsonify(message='The phone number or email is already used.'), 409
    else:
        teacher = Teacher()
        teacher.phone = phone
        teacher.email = email
        teacher.name = request.json['name']
        teacher.set_pwhash(request.json['password'])
        teacher.register_time = datetime.utcnow()
        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher created successfully"), 201
