from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from flask_marshmallow import Marshmallow
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# from flask_mail import Mail, Message
import os
from app import db, ma

# All relationships are configured on the "many" side of a one-to-many relationship.
class Student(db.Model):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)

    def __repr__(self):
        return "<Student(name='%s')>" % (self.name)


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(String)


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