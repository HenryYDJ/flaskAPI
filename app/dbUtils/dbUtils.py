from app.models import User, Course, CourseCredit, ParentHood, Student, TakingClass
from app.utils.utils import Roles


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
    if exist_user.validated:
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


def query_existing_course(course_id):
    course = Course.query.filter(Course.deleted == False).filter(Course.id == course_id).first()
    return course


def query_existing_teacher(teacher_id):
    """
    This function retrieves one teacher based on the teacher_id.
    This returned teacher is not deleted, can can be either validated or not.
    """
    teacher = User.query.filter(User.deleted == False).filter(User.id == teacher_id, User.roles == Roles.TEACHER).first()
    return teacher


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