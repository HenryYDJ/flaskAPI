from sqlalchemy import Column, INTEGER, String, BOOLEAN, ForeignKey, DATETIME, BLOB
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, ma


# All relationships are configured on the "many" side of a one-to-many relationship.
class Student(db.Model):
    __tablename__ = 'students'

    id = Column(INTEGER, primary_key=True)
    deleted = Column(BOOLEAN, default=False)
    realName = Column(String)
    dob = Column(DATETIME)  # Date of birth
    gender = Column(BOOLEAN)  # 0 for girl and 1 for boy
    creator_id = Column(INTEGER, ForeignKey('users.id'))
    create_time = Column(DATETIME)  # The date and time when the student is created
    qr_code = Column(BLOB)

    # Relationship for user who created this student
    creator = db.relationship("User", backref="created_students")

    def __repr__(self):
        return "<Student(name='%s')>" % self.realName

    def to_dict(self):
        return {
            "id": self.id,
            "real_name": self.realName,
            "gender": self.gender
        }

class User(db.Model):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True)
    deleted = Column(BOOLEAN, default=False)  # Field to mark whether the account is deleted.
    realName = Column(String)  # Real name of the account owner
    phone = Column(String)  # Phone number of the account owner
    email = Column(String)  # Email of the account owner
    pwhash = Column(String)  # Hashed password field.
    register_time = Column(DATETIME)  # Server date and time when registration was submitted. (All datetime are in
    # UTC time)
    roles = Column(INTEGER, default=0)
    avatar = Column(String)  # The avatar url of the user, updates everytime the user signs in.
    openID = Column(String)  # wechat openID of the user
    sessionKey = Column(String)  # wechat session Key of the user
    gender = Column(BOOLEAN)
    language = Column(String)
    city = Column(String)
    province = Column(String)
    validated = Column(BOOLEAN, default=False)  # Field to mark whether the user's account is validated by the admin.
    approve_time = Column(DATETIME)  # Server date and time when the use is approved.
    approver = Column(INTEGER, ForeignKey('users.id'), default=None)  # Approved by whom

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
    
    def validate_info(self):
        """
        This function returns the user's phone, realName, Role in a dict.
        This function is to help admins to approve an unapproved user.
        """
        return {
            'phone': self.phone,
            'real_name': self.realName,
            'role': self.roles
        }

    def get_role_value(self):
        """
        This function returns the role value of the user.
        The role value is used in the auth_utils to verify the user's role requirement.
        """
        return self.roles

    def get_roles(self):
        """
        This function returns the user's role and validation status in a dict.
        This function is for the frontend client to get the user's role and display contents accordingly.
        """
        return {
            'role': self.roles,
            'validated': self.validated
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = Column(INTEGER, primary_key=True)
    deleted = Column(BOOLEAN, default=False)
    name = Column(String)

    def __repr__(self):
        return "<Course(course name='%s')>" % self.name


class CourseCredit(db.Model):
    __tablename__ = "courseCredits"

    student_id = Column(INTEGER, ForeignKey('students.id'), primary_key=True)
    course_id = Column(INTEGER, ForeignKey('courses.id'), primary_key=True)
    deleted = Column(BOOLEAN, default=False)
    credit = Column(INTEGER)

    # Relationships
    student = db.relationship("Student", backref="student_credits")
    course = db.relationship("Course", backref="course_credits")


class ClassSession(db.Model):
    __tablename__ = "classSessions"

    id = Column(INTEGER, primary_key=True)
    series_id = Column(String, default=None)  # If the class session is in a series, then here is the UUID for the series
    course_id = Column(INTEGER, ForeignKey("courses.id"))
    deleted = Column(BOOLEAN, default=False)
    startTime = Column(DATETIME)  # UTC time of the session start time
    duration = Column(INTEGER)  # Duration of the event, in minutes
    info = Column(String)
    attendance_call = Column(BOOLEAN, default=False)  # Whether the teacher has taken the attendance
    attendance_teacher = Column(INTEGER, ForeignKey("users.id"))  # The teacher who took the attendance call
    attendance_time = Column(DATETIME)  # UTC time of the attendance call

    # Relationships
    course = db.relationship("Course", backref="course_sessions")


class ParentHood(db.Model):
    __tablename__ = "parenthoods"

    student_id = Column(INTEGER, ForeignKey("students.id"), primary_key=True)
    parent_id = Column(INTEGER, ForeignKey("users.id"), primary_key=True)
    deleted = Column(BOOLEAN, default=False)
    relation = Column(INTEGER)

    # Relationships
    student = db.relationship("Student", backref="parents")
    parent = db.relationship("User", backref="students")


class Teaching(db.Model):
    __tablename__ = "teachings"

    session_id = Column(INTEGER, ForeignKey("classSessions.id"), primary_key=True)
    teacher_id = Column(INTEGER, ForeignKey("users.id"), primary_key=True)
    deleted = Column(BOOLEAN, default=False)
    comments = Column(String)
    attended = Column(BOOLEAN, default=False)  # Whether the teacher attended the session

    # Relationships
    class_session = db.relationship("ClassSession", backref="session_teachings")
    teacher = db.relationship("User", backref="teacher_teachings")


class TakingClass(db.Model):
    __tablename__ = "takingClasses"

    session_id = Column(INTEGER, ForeignKey("classSessions.id"), primary_key=True)
    student_id = Column(INTEGER, ForeignKey("students.id"), primary_key=True)
    attended = Column(BOOLEAN, default=False)  # Whether the student attended the session
    deleted = Column(BOOLEAN, default=False)
    comments = Column(String)

    # Relationships
    class_session = db.relationship("ClassSession", backref="session_takings")
    student = db.relationship("Student", backref="student_takings")


class TokenBlacklist(db.Model):
    """
    Model for black listed JWT tokens.
    """
    id = Column(INTEGER, primary_key=True)
    jti = Column(String(36), nullable=False)
    token_type = Column(String(10), nullable=False)
    user_id = Column(String(50), nullable=False)
    revoked = Column(BOOLEAN, nullable=False)
    expires = Column(DATETIME, nullable=False)

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

    id = Column(INTEGER, primary_key=True)
    operator = Column(INTEGER, ForeignKey("users.id"))
    modification_time = Column(DATETIME)
    table = Column(String)
    entry = Column(INTEGER)
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
# class StudentSchema(ma.Schema):
#     class Meta:
#         fields = ["name"]


# class TeacherSchema(ma.Schema):
#     class Meta:
#         fields = ["name"]


# class UserSchema(ma.Schema):
#     class Meta:
#         fields = ["name"]


# class CourseSchema(ma.Schema):
#     class Meta:
#         fields = ["name"]


# class CourseCreditSchema(ma.Schema):
#     class Meta:
#         fields = ["student_id", "course_id", "credit"]


# class TeachingSchema(ma.Schema):
#     class Meta:
#         fields = ["comments"]


# class TakingClassSchema(ma.Schema):
#     class Meta:
#         fields = ["comments"]


# class ClassSessionSchema(ma.Schema):
#     class Meta:
#         fields = ["info"]


# class ParentHoodSchema(ma.Schema):
#     class Meta:
#         fields = ["comments"]


# student_schema = StudentSchema()
# students_schema = StudentSchema(many=True)

# teacher_schema = TeacherSchema()
# teachers_schema = TeacherSchema(many=True)

# course_schema = CourseSchema()
# courses_schema = CourseSchema(many=True)

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# course_credit_schema = CourseCreditSchema()
# course_credits_schema = CourseCreditSchema(many=True)

# parent_hood_schema = ParentHoodSchema()
# parent_hoods_schema = ParentHoodSchema(many=True)

# class_session_schema = ClassSessionSchema()
# class_sessions_schema = ClassSessionSchema(many=True)

# teaching_schema = TeachingSchema()
# teachings_schema = TeachingSchema(many=True)

# taking_class_schema = TakingClassSchema()
# taking_classes_schema = TakingClassSchema(many=True)
