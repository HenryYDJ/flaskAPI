from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# from flask_mail import Mail, Message
import os
from app import db, ma, login

# All relationships are configured on the "many" side of a one-to-many relationship.
class Student(db.Model):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)

    def __repr__(self):
        return "<Student(name='%s')>" % (self.name)


class Teacher(UserMixin, db.Model):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False) # Field to mark whether the account is deleted.
    validated = Column(Boolean, default=False) # Field to mark whether the teacher's account is validated by the admin.
    name = Column(String) # Real name of the account owner
    phone = Column(String) # Phone number of the account owner
    email = Column(String) # Email of the account owner
    pwhash = Column(String) # Hashed password field.
    register_time = Column(DateTime) # Server date and time when registration was submitted. (All datetime are in UTC time)
    approve_time = Column(DateTime) # Server date and time when the use is approved.
    approver = Column(Integer, ForeignKey('teachers.id'), default=None) # Approved by whom
    roles = Column(Integer, default=0)
    # roles are represented similar to the Linux file permission scheme: rwx
    # However, in here, the three bits represent: admin, principal, teacher
    # So, --t (1) means the role is a teacher
    # -pt (3) means the roles are principal and teacher
    # apt (7) means the roles are admin, principal and teacher


    def set_pwhash(self, password):
        """
        This function sets the password hash from the password inputed by the user.
        """
        self.pwhash = generate_password_hash(password)

    def check_password(self, password):
        """
        This function checks the password by using the check_password_hash function.
        """
        return check_password_hash(self.pwhash, password)

    def to_dict(self):
        return {
            'id': self.id
        }

@login.user_loader
def load_teacher(id):
    return Teacher.query.get(int(id))

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)


class Course(db.Model):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)

    def __repr__(self):
        return "<Course(course name='%s')>" % (self.course_name)


class CourseCredit(db.Model):
    __tablename__ = "courseCredits"

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    deleted = Column(Boolean, default=False)
    credit = Column(Integer)

    # Relationships
    student = db.relationship("Student", backref="student_credits")
    course = db.relationship("Course", backref="course_credits")


class ClassSession(db.Model):
    __tablename__ = "classSessions"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    deleted = Column(Boolean, default=False)
    info = Column(String)

    # Relationships
    course = db.relationship("Course", backref="course_sessions")


class ParentHood(db.Model):
    __tablename__ = "parenthoods"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    parent_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    deleted = Column(Boolean, default=False)
    comments = Column(String)

    # Relationships
    student = db.relationship("Student", backref="parents")
    parent = db.relationship("User", backref="students")


class Teaching(db.Model):
    __tablename__ = "teachings"

    session_id = Column(Integer, ForeignKey("classSessions.id"), primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), primary_key=True)
    deleted = Column(Boolean, default=False)
    comments = Column(String)

    # Relationships
    class_session = db.relationship("ClassSession", backref="session_teachings")
    teacher = db.relationship("Teacher", backref="teacher_teachings")


class TakingClass(db.Model):
    __tablename__ = "takingClasses"

    session_id = Column(Integer, ForeignKey("classSessions.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    deleted = Column(Boolean, default=False)
    comments = Column(String)

    # Relationships
    class_session = db.relationship("ClassSession", backref="session_takings")
    student = db.relationship("Student", backref="student_takings")

class TokenBlacklist(db.Model):
    """
    Model for black listed JWT tokens.
    """
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    token_type = Column(String(10), nullable=False)
    user_id = Column(String(50), nullable=False)
    revoked = Column(Boolean, nullable=False)
    expires = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }

#--------------------------Marshmallow Schema----------------------------------------
class StudentSchema(ma.Schema):
    class Meta:
        fields = ["name"]


class TeacherSchema(ma.Schema):
    class Meta:
        fields = ["name"]


class UserSchema(ma.Schema):
    class Meta:
        fields = ["name"]


class CourseSchema(ma.Schema):
    class Meta:
        fields = ["name"]


class CourseCreditSchema(ma.Schema):
    class Meta:
        fields = ["student_id", "course_id", "credit"]


class TeachingSchema(ma.Schema):
    class Meta:
        fields = ["comments"]


class TakingClassSchema(ma.Schema):
    class Meta:
        fields = ["comments"]


class ClassSessionSchema(ma.Schema):
    class Meta:
        fields = ["info"]


class ParentHoodSchema(ma.Schema):
    class Meta:
        fields = ["comments"]

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

teacher_schema = TeacherSchema()
teachers_schema = TeacherSchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

course_credit_schema = CourseCreditSchema()
course_credits_schema = CourseCreditSchema(many=True)

parent_hood_schema = ParentHoodSchema()
parent_hoods_schema = ParentHoodSchema(many=True)

class_session_schema = ClassSessionSchema()
class_sessions_schema = ClassSessionSchema(many=True)

teaching_schema = TeachingSchema()
teachings_schema = TeachingSchema(many=True)

taking_class_schema = TakingClassSchema()
taking_classes_schema = TakingClassSchema(many=True)