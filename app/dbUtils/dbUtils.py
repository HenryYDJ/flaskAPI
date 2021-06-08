from app.models import Teaching, User, Course, CourseCredit, ParentHood, Student, TakingClass, ClassSession
from app.utils.utils import Roles, VALIDATIONS
from app import db


def query_existing_user(user_id):
    """
    This function returns an existing user based on the user_id.
    """
    user = User.query.filter(User.deleted == False).filter((User.id == user_id)).first()
    return user


def query_validated_user(user_id):
    """
    This function retrieves one user if it is already validated. Otherwise, a None object is returned.
    """
    exist_user = query_existing_user(user_id)
    if exist_user.validated == VALIDATIONS.APPROVED:
        return exist_user
    else:
        return None


def query_unvalidated_users():
    """
    This function retrieves all existing but unvalidated users.
    """
    users = User.query.filter(User.deleted == False).filter(User.validated == False).all()
    return users


def query_existing_student(student_id):
    """
    This function returns an existing student based on the student_id
    """
    student = Student.query.filter(Student.deleted == False).filter(Student.id == student_id).first()
    return student


def query_all_existing_students():
    """
    This function returns all undeleted students in the DB
    """
    students = Student.query.filter(Student.deleted == False).all()
    return students


def query_existing_phone_user(phone_number):
    """
    This function retrieves one existing user based on the user's phone number.
    """
    user = User.query.filter(User.deleted == False).filter((User.phone == phone_number)).first()
    return user


def query_existing_openid_user(openid):
    """
    This function retrieves one existing user based on the user's wechat openid.
    """
    user = User.query.filter(User.deleted == False).filter(User.openid == openid).first()
    return user


def query_existing_course(course_id):
    course = Course.query.filter(Course.deleted == False).filter(Course.id == course_id).first()
    return course


def query_existing_courses_all():
    """
    This function returns all the existing courses in the DB.
    """
    courses = Course.query.filter(Course.deleted == False).all()
    return courses


def query_existing_teacher(teacher_id):
    """
    This function retrieves one teacher based on the teacher_id.
    This returned teacher is not deleted, can can be either validated or not.
    """
    teacher = User.query.filter(User.deleted == False).filter(User.id == teacher_id, User.roles == Roles.TEACHER).first()
    return teacher


def query_existing_teachers():
    """
    This function retrieves all existing teachers.
    """
    teachers = User.query.filter(User.deleted == False).filter(User.roles == Roles.TEACHER).all()
    return teachers


def query_course_credit(course_id, student_id):
    """
    This functions retrieves the course_credit record based on the course_id and student_id
    """
    course_credit = CourseCredit.query.filter(CourseCredit.deleted == False)\
        .filter(CourseCredit.course_id == course_id, CourseCredit.student_id == student_id).first()
    return course_credit


def query_parent_hood(parent_id, student_id):
    """
    This function retrieves the parent_hood record based on the parent_id and student_id
    """
    parent_hood = ParentHood.query.filter(ParentHood.deleted == False)\
        .filter(ParentHood.parent_id == parent_id, ParentHood.student_id == student_id).first()
    return parent_hood


def query_existing_taking_class(class_session_id, student_id):
    """
    This functions retrieves the taking class record based on the class_session_id and student_id
    """
    taking_class = TakingClass.query.filter(TakingClass.deleted == False)\
        .filter(TakingClass.session_id == class_session_id, TakingClass.student_id == student_id).first()
    return taking_class


def query_teacher_class_sessions(start_time, end_time, teacher_id):
    """
    This function selects all the class session that a teacher is teaching, and within a certain time frame.
    """
    sessions = ClassSession.query.join(Teaching)\
        .filter(ClassSession.deleted == False)\
        .filter(Teaching.deleted == False)\
        .filter(ClassSession.id == Teaching.session_id)\
        .filter(ClassSession.start_time >= start_time, ClassSession.start_time <= end_time)\
        .filter(Teaching.teacher_id == teacher_id).all()
    return sessions


def query_class_session(session_id):
    """
    This function selects one class session using the session id
    """
    class_session = ClassSession.query.filter(ClassSession.deleted == False).filter(ClassSession.id == session_id).first()
    return class_session


def query_session_students(session_id):
    """
    This functions retrieves all the students taking a class session
    """
    students = db.session.query(TakingClass, Student).filter(TakingClass.deleted == False)\
        .filter(Student.deleted == False)\
        .filter(TakingClass.student_id == Student.id)\
        .filter(TakingClass.session_id == session_id).all()
    return students


def query_student_parents(student_id):
    """
    This function selects all the parents' names and relations that is accociated with a student.
    # """
    parents = db.session.query(User.real_name, ParentHood.relation).filter(User.deleted == False)\
        .filter(ParentHood.deleted == False)\
        .filter(User.id == ParentHood.parent_id)\
        .filter(ParentHood.student_id == student_id).all()
    return parents


def query_student_credit(student_id, course_id):
    """
    This function selects the student credit using student_id and course_id
    """
    student_credit = CourseCredit.query.filter(CourseCredit.deleted == False)\
        .filter(CourseCredit.student_id == student_id, CourseCredit.course_id == course_id).first()
    return student_credit


def query_student_credits(student_id):
    """
    This function selects the students remaining credits
    """
    course_credits = db.session.query(Course.name, CourseCredit.credit).filter(Course.deleted == False)\
        .filter(CourseCredit.deleted == False)\
        .filter(CourseCredit.course_id == Course.id)\
        .filter(CourseCredit.student_id == student_id).all()
    return course_credits


def query_student_credits_of_parent(student_id, parent_id):
    """
    This function selects the students of a parent remaining credits
    """
    course_credits = db.session.query(Course.name, CourseCredit.credit).filter(Course.deleted == False)\
        .filter(CourseCredit.deleted == False)\
        .filter(ParentHood.deleted == False)\
        .filter(CourseCredit.course_id == Course.id)\
        .filter(CourseCredit.student_id == student_id).all()
    return course_credits


def query_teacher_sessions(teacher_id, start_time_utc, end_time_utc):
    """
    This function retrieves all the sessions that a teacher teaches within a time frame.
    """
    sessions = db.session.query(ClassSession, Teaching).filter(ClassSession.deleted == False).\
        filter(Teaching.deleted == False).\
        filter(Teaching.session_id == ClassSession.id).\
        filter(Teaching.teacher_id == teacher_id).\
        filter(ClassSession.start_time >= start_time_utc, ClassSession.start_time <= end_time_utc).all()
    return sessions


def query_student_sessions(student_id, start_time_utc, end_time_utc):
    """
    This function retrieves all the sessions that a student registered within a time frame.
    """
    sessions = db.session.query(ClassSession, TakingClass).filter(ClassSession.deleted == False).\
        filter(TakingClass.deleted == False).\
        filter(TakingClass.session_id == ClassSession.id).\
        filter(TakingClass.student_id == student_id).\
        filter(ClassSession.start_time >= start_time_utc, ClassSession.start_time <= end_time_utc).all()
    return sessions


def query_taking_class(student_id, session_id):
    """
    This function retrieves one taking class record using student_id and session_id
    """
    taking_class = TakingClass.query.filter(TakingClass.deleted == False).filter(TakingClass.session_id == session_id)\
        .filter(TakingClass.student_id == student_id).first()
    return taking_class


def query_unvalidated_parents():
    """
    This function retrieves all existing but unvalidated parents.
    """
    parents = User.query.filter(User.deleted == False).filter(User.validated == False).filter(User.roles == Roles.PARENT).all()
    return parents


def query_parent_hood(parent_id, student_id):
    """
    This function retrieves the parenthood record based on parent_id and student_id
    """
    parent_hood = ParentHood.query.filter(ParentHood.deleted == False).filter(ParentHood.parent_id == parent_id).\
        filter(ParentHood.student_id == student_id).first()
    return parent_hood


def query_unrevoked_admins():
    """
    This function retrieves all the unrevoked admins
    """
    admins = User.query.filter(User.deleted == False).filter(User.roles == Roles.ADMIN).filter(User.validated != VALIDATIONS.REVOKED).all()
    return admins


def query_parent_students(parent_id):
    """
    This function get all the students of a parent
    """
    students = db.session.query(Student, ParentHood).filter(ParentHood.deleted == False).\
        filter(Student.deleted == False).\
        filter(ParentHood.student_id == Student.id).\
        filter(ParentHood.parent_id == parent_id).all()
    return students

# def query_existing_class_session(session_id, teacher_id):
#     """
#     This function selects one session based on the session_id and teacher_id.
#     """
#     sessions = ClassSession.query.join(Teaching)\
#         .filter(ClassSession.deleted == False)\
#         .filter(Teaching.deleted == False)\
#         .filter(ClassSession.id == Teaching.session_id)\
#         .filter(ClassSession.id == session_id)\
#         .filter(Teaching.teacher_id == teacher_id).first()
# -----------------------------TEST-------------------------------

# def query_existing_class_sessions():
#     sessions = db.session.query(ClassSession).all()
#     return sessions