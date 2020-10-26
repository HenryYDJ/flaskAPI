from flask import Blueprint, jsonify, request
from app import db
from app.models import Teacher, teacher_schema, teachers_schema
from app.api.teacher import bluePrint

#-------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/api/v1.0/teacher', methods=['POST'])
def add_teacher():
    """
    This api adds one teacher to the DB.
    """
    name = request.json['name']

    already_existed = Teacher.query.filter_by(name=name, deleted=False).first()
    if already_existed:
        return jsonify(message='The teacher already exists'), 409
    else:
        teacher = Teacher(name=name)
        db.session.add(teacher)
        db.session.commit()
        return jsonify(message="Teacher created successfully"), 201


@bluePrint.route('/api/v1.0/teacher', methods=['GET'])
def get_teacher():
    """
    This api gets one teacher from the DB by the teacher's id.
    """
    id = request.args.get('teacher_id', None)

    teacher = Teacher.query.filter_by(id=id, deleted=False).first()
    if teacher:
        return jsonify(teacher_schema.dump(teacher))
    else:
        return jsonify(message="Teacher not found"), 404


@bluePrint.route('/api/v1.0/teachers', methods=['GET'])
def get_teachers():
    """
    This api gets all teachers from the DB.
    """
    teachers = Teacher.query.filter_by(deleted=False).all()
    if teachers:
        return jsonify(teachers_schema.dump(teachers))
    else:
        return jsonify(message="No teachers found"), 404


@bluePrint.route('/api/v1.0/teacher', methods=['PUT'])
def update_teacher():
    """
    This api updates a teacher's information based on the teacher's id
    """
    id = request.args.get('teacher_id', None)

    teacher = Teacher.query.filter_by(id=id, deleted=False).first()
    if teacher:
        teacher.name = request.json["name"]
        db.session.add(teacher)
        db.session.commit()
        return jsonify(teacher_schema.dump(teacher))
    else:
        return jsonify(message="Teacher not found"), 404


@bluePrint.route('/api/v1.0/teacher', methods=['DELETE'])
def delete_teacher():
    """
    This api deletes a teacher by teacher's id from the DB.
    """
    id = request.args.get('teacher_id', None)

    teacher = Teacher.query.filter_by(id=id, deleted=False).first()
    if teacher:
        teacher.deleted = True
        db.session.add(teacher)
        db.session.commit()
        return jsonify(teacher_schema.dump(teacher))
    else:
        return jsonify(message="Teacher not found"), 404