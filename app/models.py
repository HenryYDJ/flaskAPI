from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# from flask_mail import Mail, Message
import os
from app import db, ma


# All relationships are configured on the "many" side of a one-to-many relationship.
class Student(db.Model):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    realName = Column(String)
    dob = Column(DateTime)  # Date of birth
    gender = Column(Boolean)  # 0 for girl and 1 for boy
    creator_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "<Student(name='%s')>" % self.realName


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)  # Field to mark whether the account is deleted.
    realName = Column(String)  # Real name of the account owner
    phone = Column(String)  # Phone number of the account owner
    email = Column(String)  # Email of the account owner
    pwhash = Column(String)  # Hashed password field.
    register_time = Column(DateTime)  # Server date and time when registration was submitted. (All datetime are in
    # UTC time)
    roles = Column(Integer, default=0)
    avatar = Column(String)  # The avatar url of the user, updates everytime the user signs in.
    openID = Column(String)  # wechat openID of the user
    sessionKey = Column(String)  # wechat session Key of the user
    gender = Column(Boolean)
    language = Column(String)
    city = Column(String)
    province = Column(String)
    validated = Column(Boolean, default=False)  # Field to mark whether the user's account is validated by the admin.
    approve_time = Column(DateTime)  # Server date and time when the use is approved.
    approver = Column(Integer, ForeignKey('users.id'), default=None)  # Approved by whom

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

    def get_roles(self):
        return self.roles


class Course(db.Model):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)

    def __repr__(self):
        return "<Course(course name='%s')>" % self.name


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
    startTime = Column(DateTime)  # UTC time of the session start time
    endTime = Column(DateTime)  # UTC time of the session end time

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
    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    deleted = Column(Boolean, default=False)
    comments = Column(String)

    # Relationships
    class_session = db.relationship("ClassSession", backref="session_teachings")
    teacher = db.relationship("User", backref="teacher_teachings")


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


class ModificationLog(db.Model):
    """
    Model for tracking who made modifications to the DB
    Only tracking modifications, creations are not tracked since the creator and creation time is included almost all the times
    """
    __tablename__ = "modificationLog"

    id = Column(Integer, primary_key=True)
    operator = Column(Integer, ForeignKey("users.id"))
    modification_time = Column(DateTime)
    table = Column(String)
    entry = Column(Integer)
    column = Column(String)
    original = Column(String)
    new = Column(String)

    # def __repr__(self):
    #     if self.operator_wechat:
    #         return "Wechat user %s changed table: %s entry: %s column: %s from %s to %s" % \
    #                (self.operator_wechat, self.table, self.entry, self.column, self.original, self.new)
    #     else:
    #         return "Web user %s changed table: %s entry: %s column: %s from %s to %s" % \
    #                (self.operator_web, self.table, self.entry, self.column, self.original, self.new)


# --------------------------Marshmallow Schema----------------------------------------
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
