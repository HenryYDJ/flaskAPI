from flask import jsonify, request
from dateutil.rrule import *
from uuid import uuid4
from datetime import timedelta
from app import db
from app.models import Course, ClassSession, Teaching, TakingClass, CourseCredit
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_course, query_course_credit, query_existing_taking_class, \
    query_existing_class_sessions, query_existing_courses_all
from app.utils.utils import datetime_string_to_utc, Roles, \
    datetime_string_to_datetime, convert_to_UTC,dt_list_to_UTC_list
from flask_jwt_extended import get_jwt_identity


@bluePrint.route('/course', methods=['POST'])
@jwt_roles_required(Roles.ADMIN)  # Only admin and above can add a course
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


@bluePrint.route('/courses', methods=['GET'])
def get_courses():
    """
    This api gets all courses from the DB.
    """
    courses = query_existing_courses_all()
    if courses:
        return jsonify(message=[course.to_dict() for course in courses]), 201
    else:
        return jsonify(message="No courses found"), 404


@bluePrint.route('/class_session', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # Only teacher and above can add a class session
def add_class_session():
    """
    This api adds one class session or recurring class sessions to the DB.
    This api will take into account whether the event is a recurring one.
    The repeat wkdays from request need to be in 0, 1, 2, ... 6 for Mon, Tue, Wed, ... Sun
    This api will also add associated teaching information into DB.
    This api also adds the students taking the class session into DB.
    """
    one_year = timedelta(days = 365)
    course_id = request.json.get('course_id', None)
    # start_time and end_time needs to be in original timezone to preserve information
    start_time_local = datetime_string_to_datetime(request.json.get('start_time', None))
    end_time_local = datetime_string_to_datetime(request.json.get('end_time', None))
    duration = request.json.get('duration', None)  # duration is in minutes
    info = request.json.get('info', None)
    student_ids = request.json.get('student_ids', None)
    course = query_existing_course(course_id)
    teacher_id = get_jwt_identity().get('id')
    repeat_weekly = request.json.get('repeat_weekly', None)

    if duration <= 0:
        return jsonify(message="Duration must be greater than 0"), 400

    if end_time_local < start_time_local:
        return jsonify(message="End time must be after start time"), 400

    if course:
        if repeat_weekly:
            if end_time_local - start_time_local > one_year:
                return jsonify(message="Can not add more than one years sessions"), 400
            else:
                series_id = str(uuid4())
                repeat_wkdays = request.json.get('repeat_wkdays', None)  # weekdays are in: MO, TU, WE, TH, FR, SA, SU
                start_time_local_list = list(rrule(WEEKLY, interval=1, until=end_time_local, 
                    wkst=MO, byweekday=repeat_wkdays, dtstart=start_time_local))
                start_time_utc_list = dt_list_to_UTC_list(start_time_local_list)
                for start_time_utc in start_time_utc_list:
                    class_session = ClassSession()
                    class_session.course = course
                    class_session.series_id = series_id
                    class_session.startTime = start_time_utc
                    class_session.duration = duration
                    class_session.info = info
                    
                    # Add teacher information to the class_session
                    teaching = Teaching()
                    teaching.class_session = class_session
                    teaching.teacher_id = teacher_id
                    
                    # Add taking class info to the DB
                    if student_ids:
                        for student_id in student_ids:
                            taking_class = TakingClass()
                            taking_class.class_session = class_session
                            taking_class.student_id = student_id
                            db.session.add(taking_class)

                    db.session.add(class_session)
                    db.session.add(teaching)

                db.session.commit()
                return jsonify(message="Recurring class sessions added successfully"), 201
        else:
            class_session = ClassSession()
            class_session.course = course
            class_session.startTime = convert_to_UTC(start_time_local)
            class_session.duration = duration
            class_session.info = info

            # Add teacher information to the class_session
            teaching = Teaching()
            teaching.class_session = class_session
            teaching.teacher_id = teacher_id

            db.session.add(class_session)
            db.session.add(teaching)
            db.session.commit()
            return jsonify(message="Class session added successfully"), 201
    else:
        return jsonify(message="Course does not exist"), 400


@bluePrint.route('/class_sessions', methods=['GET'])
@jwt_roles_required(Roles.TEACHER)  # Only teacher and above
def get_class_sessions():
    """
    This API gets all the class sessions that the teacher is teaching within a time frame
    """
    # Get the start time and end time in UTC so we can query the DB easily.
    start_time_utc = datetime_string_to_utc(request.json.get('start_time', None))
    end_time_utc = datetime_string_to_utc(request.json.get('end_time', None))
    teacher_id = get_jwt_identity().get('id')
    print(start_time_utc)
    print(end_time_utc)
    print(teacher_id)
    
    class_sessions = query_existing_class_sessions(start_time_utc, end_time_utc, teacher_id)
    print(class_sessions)
    # class_sessions = query_existing_class_sessions()
    return jsonify(message=[class_session.to_dict() for class_session in class_sessions]), 201


@bluePrint.route('/course_credit', methods=['PUT'])
@jwt_roles_required(Roles.ADMIN)  # Only admin can adjust a course credit info
def update_course_credit():
    """
    This api updates the course credit of a student in the DB.
    If no previous course credit was in the DB, then a new record is created and stored.
    """
    course_id = request.json.get('course_id', None)
    student_id = request.json.get('student_id', None)
    credit = request.json.get('course_credit', None)

    course_credit = query_course_credit(course_id, student_id)

    if course_credit:
        course_credit.credit = credit
        db.session.add(course_credit)
        db.session.commit()
        return jsonify(message="Course credit updated"), 201
    else:
        course_credit = CourseCredit()
        course_credit.course_id = course_id
        course_credit.student_id = student_id
        course_credit.credit = credit
        db.session.add(course_credit)
        db.session.commit()
        return jsonify(message="Course credit added"), 201


@bluePrint.route('/taking_class', methods=['POST'])
@jwt_roles_required(Roles.TEACHER)  # Only teacher and above can add a course
def add_taking_class_session():
    """
    This api add students who are taking a class session into the DB.
    """
    class_session_id = request.json.get('class_session_id', None)
    student_ids = request.json.get('student_ids', None)
    comments = request.json.get('comments', None)

    for student_id in student_ids:
        taking_class = query_existing_taking_class(class_session_id, student_id)
        if taking_class:
            taking_class.comments = comments
        else:
            taking_class = TakingClass()
            taking_class.session_id = class_session_id
            taking_class.student_id = student_id
            taking_class.comments = comments

        db.session.add(taking_class)
        db.session.commit()
    return jsonify(message="Taking class information added"), 201
# @bluePrint.route('/student_course_credits', methods=['GET'])
# @jwt_roles_required(Roles.TEACHER)  # Only teacher and above can add a course
# def get_student_course_credits():
#     """
#     This api gets all the course credits of a student.
#     """
#     student_id = request.json.get('student_id', None)

#     course_credit = query_course_credit(course_id, student_id)

#     if course_credit:
#         course_credit.credit = credit
#         db.session.add(course_credit)
#         db.session.commit()
#         return jsonify(message="Course credit updated"), 201
#     else:
#         return jsonify(message="Course credit does not exist"), 400


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


# @bluePrint.route('/class_session', methods=['PUT'])
# @jwt_roles_required(Roles.TEACHER)  # Only teacher and above
# def teacher_update_class_sessions():
#     """
#     This API lets a teacher to update his/her own class session information.
#     This API updates one class session instead a series of sessions.
#     """
#     teacher_id = get_jwt_identity().get('id')
#     session_id = request.json.get('session_id', None)

#     start_time_local = datetime_string_to_datetime(request.json.get('start_time', None))
#     end_time_local = datetime_string_to_datetime(request.json.get('end_time', None))
#     duration = request.json.get('duration', None)  # duration is in minutes

#     class_session = query_existing_class_session(session_id, teacher_id)
#     if class_session:

#     return jsonify(message=[class_session.to_dict() for class_session in class_sessions]), 201