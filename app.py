from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from flask_marshmallow import Marshmallow
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# from flask_mail import Mail, Message
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sms.db')
app.config['JWT_SECRET_KEY'] = 'super-secret' # CHANGE THIS LATER
app.config

db = SQLAlchemy(app)
ma = Marshmallow(app)
# jwt = JWTManager(app)

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

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():

    student = Student(name="abc")
    english = Course(name='English')
    courseNo = CourseCredit(credit=100)
    # courseNo.student = student
    english.course_credits.append(courseNo)
    student.student_credits.append(courseNo)

    session1 = ClassSession(info="what's up")
    english.course_sessions.append(session1)

    teaching = Teaching()
    teacher = Teacher(name="teacher1")
    teacher.teacher_teachings.append(teaching)
    session1.session_teachings.append(teaching)

    taking_class = TakingClass()
    session1.session_takings.append(taking_class)
    student.student_takings.append(taking_class)

    parent_hood = ParentHood()
    user = User(name="user")
    student.parents.append(parent_hood)
    user.students.append(parent_hood)

    # SQLAlchemy has cascading property, so I just need to add one of the objects to the session.
    # https://docs.sqlalchemy.org/en/13/orm/cascades.html#unitofwork-cascades
    # db.session.add(student)
    # db.session.add(courseNo)
    db.session.add(english)
    db.session.add(user)

    db.session.commit()
    print('Database seeded!')

#---------------API Section--------------------------------------------------------------------------

# All APIs communicate using JSON format
# API routes are /api/v1.0/name_of_api/optional_parameters
#---------------------------Student Section----------------------------------------------------------
@app.route('/api/v1.0/student', methods=['POST'])
def add_student():
    """
    This api adds one student to the DB.
    """
    name = request.json['name']

    already_existed = User.query.filter_by(name=name).first()
    if already_existed:
        return jsonify(message='The student already exists'), 409
    else:
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
        return jsonify(message="Student created successfully"), 201


@app.route('/api/v1.0/student', methods=['GET'])
def get_student():
    """
    This api gets one student from the DB by the student's id.
    """
    id = request.args.get('student_id', None)

    student = Student.query.filter_by(id=id, deleted=False).first()
    if student:
        return jsonify(student_schema.dump(student))
    else:
        return jsonify(message="Student not found"), 404


@app.route('/api/v1.0/students', methods=['GET'])
def get_students():
    """
    This api gets all students from the DB.
    """

    students = Student.query.filter_by(deleted=False).all()
    if students:
        return jsonify(students_schema.dump(students))
    else:
        return jsonify(message="No students found"), 404


@app.route('/api/v1.0/student', methods=['PUT'])
def update_student():
    """
    This api updates a student's information based on the student's id.
    """
    id = request.args.get('student_id', None)

    student = Student.query.filter_by(id=id, deleted=False).first()
    if student:
        student.name = request.json["name"]
        db.session.add(student)
        db.session.commit()
        return jsonify(student_schema.dump(student))
    else:
        return jsonify(message="Student not found"), 404


@app.route('/api/v1.0/student', methods=['DELETE'])
def delete_student():
    """
    This api deletes a student by student's id from the DB.
    """
    id = request.args.get('student_id', None)

    student = Student.query.filter_by(id=id, deleted=False).first()
    if student:
        student.deleted = True
        db.session.add(student)
        db.session.commit()
        return jsonify(student_schema.dump(student))
    else:
        return jsonify(message="Student not found"), 404

#-------------------Teachers Section--------------------------------------------------------
@app.route('/api/v1.0/teacher', methods=['POST'])
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


@app.route('/api/v1.0/teacher', methods=['GET'])
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


@app.route('/api/v1.0/teachers', methods=['GET'])
def get_teachers():
    """
    This api gets all teachers from the DB.
    """
    teachers = Teacher.query.filter_by(deleted=False).all()
    if teachers:
        return jsonify(teachers_schema.dump(teachers))
    else:
        return jsonify(message="No teachers found"), 404


@app.route('/api/v1.0/teacher', methods=['PUT'])
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


@app.route('/api/v1.0/teacher', methods=['DELETE'])
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

#-------------------Courses Section--------------------------------------------------------
@app.route('/api/v1.0/course', methods=['POST'])
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


@app.route('/api/v1.0/course', methods=['GET'])
def get_course():
    """
    This api gets one course from the DB by the course's id.
    """
    id = request.args.get('course_id', None)

    course = Course.query.filter_by(id=id, deleted=False).first()
    if course:
        return jsonify(course_schema.dump(course))
    else:
        return jsonify(message="Course not found"), 404


@app.route('/api/v1.0/courses', methods=['GET'])
def get_courses():
    """
    This api gets all courses from the DB.
    """
    courses = Course.query.filter_by(deleted=False).all()
    if courses:
        return jsonify(courses_schema.dump(courses))
    else:
        return jsonify(message="No courses found"), 404


@app.route('/api/v1.0/course', methods=['PUT'])
def update_course():
    """
    This api updates a course's information based on the course's id
    """
    id = request.args.get('course_id', None)

    course = Course.query.filter_by(id=id, deleted=False).first()
    if course:
        course.name = request.json["name"]
        db.session.add(course)
        db.session.commit()
        return jsonify(course_schema.dump(course))
    else:
        return jsonify(message="Course not found"), 404


@app.route('/api/v1.0/course', methods=['DELETE'])
def delete_course():
    """
    This api deletes a course by course's id from the DB.
    """
    id = request.args.get('course_id', None)

    course = Course.query.filter_by(id=id, deleted=False).first()
    if course:
        course.deleted = True
        db.session.add(course)
        db.session.commit()
        return jsonify(course_schema.dump(course))
    else:
        return jsonify(message="Course not found"), 404

#-----------------------Users Section-----------------------------------------
@app.route('/api/v1.0/user', methods=['POST'])
def add_user():
    """
    This api adds one user to the DB.
    """
    name = request.json['name']

    already_existed = User.query.filter_by(name=name, deleted=False).first()
    if already_existed:
        return jsonify(message='The user already exists'), 409
    else:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@app.route('/api/v1.0/user', methods=['GET'])
def get_user():
    """
    This api gets one user from the DB by the user's id.
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404


@app.route('/api/v1.0/users', methods=['GET'])
def get_users():
    """
    This api gets all users from the DB.
    """
    users = User.query.filter_by(deleted=False).all()
    if users:
        return jsonify(users_schema.dump(users))
    else:
        return jsonify(message="No users found"), 404


@app.route('/api/v1.0/user', methods=['PUT'])
def update_user():
    """
    This api updates a user's information based on the user's id
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        user.name = request.json["name"]
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404


@app.route('/api/v1.0/user', methods=['DELETE'])
def delete_user(user_id):
    """
    This api deletes a user by user's id from the DB.
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        user.deleted = True
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404

#---------------------CourseCredit Section---------------------------------
@app.route('/api/v1.0/course_credit', methods=['POST'])
def add_course_credit():
    """
    This api adds one course_credit record to the DB.
    """
    course_id = request.json['course_id']
    student_id = request.json['student_id']

    course = Course.query.filter_by(id=course_id, deleted=False).first()
    student = Student.query.filter_by(id=student_id, deleted=False).first()

    if course and student:
        # Course and Student must both exist
        already_existed = CourseCredit.query.filter_by(course_id=course_id, student_id=student_id, deleted=False).first()
        if already_existed:
            return jsonify(message="The course credit entry already exists"), 409
        else:
            course_credit = CourseCredit()
            course_credit.student = student
            course_credit.course = course
            course_credit.credit = request.json['credit']
            db.session.add(course_credit)
            db.session.commit()
            return jsonify(message="Course credit added successfully"), 201
    else:
        return jsonify(message="Student or Course do not exist."), 404


@app.route('/api/v1.0/course_credit', methods=['PUT'])
def update_course_credit():
    """
    This api updates one course_credit record in the DB.
    """
    course_id = request.json['course_id']
    student_id = request.json['student_id']

    course_credit = CourseCredit.query.filter_by(course_id=course_id, student_id=student_id, deleted=False).first()
    if course_credit:
        course_credit.credit = request.json['credit']
        db.session.add(course_credit)
        db.session.commit()
        return jsonify(message="Course credit updated successfully."), 201
    else:
        return jsonify(message="Course credit do not exist."), 404

@app.route('/api/v1.0/student_course_credits', methods=['GET'])
def get_student_course_credits():
    """
    This api gets a list of course_credit record by its student_id.
    """
    student_id = request.args.get('student_id', None)

    course_credits = CourseCredit.query.filter_by(student_id=student_id, deleted=False).all()
    if course_credits:
        return jsonify(course_credits_schema.dump(course_credits)), 201
    else:
        return jsonify(message="Course credits do not exist."), 404


@app.route('/api/v1.0/course_course_credits', methods=['GET'])
def get_course_course_credits():
    """
    This api gets a list of course_credit record by its course_id.
    """
    course_id = request.args.get('course_id', None)

    course_credits = CourseCredit.query.filter_by(course_id=course_id, deleted=False).all()
    if course_credits:
        return jsonify(course_credits_schema.dump(course_credits)), 201
    else:
        return jsonify(message="Course credits do not exist."), 404


@app.route('/api/v1.0/course_credit', methods=['DELETE'])
def delete_course_credit():
    """
    This api deletes a course_credit record by its course_id and student_id.
    """
    course_id = request.args.get('course_id', None)
    student_id = request.args.get('student_id', None)

    course_credit = CourseCredit.query.filter_by(course_id=course_id, student_id=student_id, deleted=False).first()
    if course_credit:
        course_credit.deleted = True
        db.session.add(course_credit)
        db.session.commit()
        return jsonify(message="Course credit deleted successfully."), 201
    else:
        return jsonify(message="Course credit do not exist."), 404


#------------------------------Parent Hood Section-------------------------------------------------------------------------
@app.route('/api/v1.0/parent_hood', methods=['POST'])
def add_parent_hood():
    """
    This api adds one parent_hood record to the DB.
    """
    parent_id = request.json['parent_id']
    student_id = request.json['student_id']

    parent = User.query.filter_by(id=parent_id, deleted=False).first()
    student = Student.query.filter_by(id=student_id, deleted=False).first()

    if parent and student:
        # Parent and Student must both exist
        already_existed = ParentHood.query.filter_by(parent_id=parent_id, student_id=student_id, deleted=False).first()
        if already_existed:
            return jsonify(message="The parent hood entry already exists"), 409
        else:
            parent_hood = ParentHood()
            parent_hood.student = student
            parent_hood.parent = parent
            parent_hood.comments = request.json['comments']
            db.session.add(parent_hood)
            db.session.commit()
            return jsonify(message="Parent hood added successfully"), 201
    else:
        return jsonify(message="Student or Parent do not exist."), 404


@app.route('/api/v1.0/parent_hood', methods=['PUT'])
def update_parent_hood():
    """
    This api updates one parent_hood record in the DB.
    """
    parent_id = request.json['parent_id']
    student_id = request.json['student_id']

    parent_hood = ParentHood.query.filter_by(parent_id=parent_id, student_id=student_id, deleted=False).first()
    if parent_hood:
        parent_hood.comments = request.json['comments']
        db.session.add(parent_hood)
        db.session.commit()
        return jsonify(message="Parent hood updated successfully."), 201
    else:
        return jsonify(message="Parent hood do not exist."), 404


@app.route('/api/v1.0/student_parent_hoods', methods=['GET'])
def get_student_parent_hoods():
    """
    This api gets a list of parent_hood record by its student_id.
    """
    student_id = request.args.get('student_id', None)

    parent_hoods = ParentHood.query.filter_by(student_id=student_id, deleted=False).all()
    if parent_hoods:
        return jsonify(parent_hoods_schema.dump(parent_hoods)), 201
    else:
        return jsonify(message="Parent hoods do not exist."), 404


@app.route('/api/v1.0/parent_parent_hoods', methods=['GET'])
def get_parent_parent_hoods():
    """
    This api gets a list of parent_hood record by its parent_id.
    """
    parent_id = request.args.get('parent_id', None)

    parent_hoods = ParentHood.query.filter_by(parent_id=parent_id, deleted=False).all()
    if parent_hoods:
        return jsonify(parent_hoods_schema.dump(parent_hoods)), 201
    else:
        return jsonify(message="Parent hoods do not exist."), 404


@app.route('/api/v1.0/parent_hood', methods=['DELETE'])
def delete_parent_hood():
    """
    This api deletes a parent_hood record by its parent_id and student_id.
    """
    parent_id = request.args.get('parent_id', None)
    student_id = request.args.get('student_id', None)

    parent_hood = ParentHood.query.filter_by(parent_id=parent_id, student_id=student_id, deleted=False).first()
    if parent_hood:
        parent_hood.deleted = True
        db.session.add(parent_hood)
        db.session.commit()
        return jsonify(message="Parent hood deleted successfully."), 201
    else:
        return jsonify(message="Parent hood do not exist."), 404


#------------------------------------Class Session Section---------------------------------------------------
@app.route('/api/v1.0/class_session', methods=['POST'])
def add_class_session():
    """
    This api adds one class_session record to the DB.
    """
    course_id = request.json['course_id']

    course = Course.query.filter_by(id=course_id, deleted=False).first()

    if course:
        # Course must exist
        class_session = ClassSession()
        class_session.course = course
        class_session.info = request.json['info']
        db.session.add(class_session)
        db.session.commit()
        return jsonify(message="Class Session added successfully"), 201
    else:
        return jsonify(message="Course does not exist."), 404


@app.route('/api/v1.0/class_session', methods=['PUT'])
def update_class_session():
    """
    This api updates one class_session record in the DB.
    """
    id = request.json['id']

    class_session = ClassSession.query.filter_by(id=id, deleted=False).first()
    if class_session:
        class_session.info = request.json['info']
        db.session.add(class_session)
        db.session.commit()
        return jsonify(message="Class Session updated successfully."), 201
    else:
        return jsonify(message="Class Session does not exist."), 404


@app.route('/api/v1.0/class_session', methods=['GET'])
def get_class_session():
    """
    This api gets a class_session record by its id.
    """
    id = request.args.get('id', None)

    class_session = ClassSession.query.filter_by(id=id, deleted=False).first()
    if class_session:
        return jsonify(class_session_schema.dump(class_session)), 201
    else:
        return jsonify(message="Class session does not exist."), 404


@app.route('/api/v1.0/class_sessions', methods=['GET'])
def get_class_sessions():
    """
    This api gets a list of class_session record by course_id.
    """
    course_id = request.args.get('course_id', None)

    class_sessions = ClassSession.query.filter_by(course_id=course_id, deleted=False).all()
    if class_sessions:
        return jsonify(class_sessions_schema.dump(class_sessions)), 201
    else:
        return jsonify(message="Class session does not exist."), 404


@app.route('/api/v1.0/class_session', methods=['DELETE'])
def delete_class_session():
    """
    This api deletes a class_session record by its id.
    """
    id = request.args.get('id', None)

    class_session = ClassSession.query.filter_by(id=id, deleted=False).first()
    if class_session:
        class_session.deleted = True
        db.session.add(class_session)
        db.session.commit()
        return jsonify(message="Class session deleted successfully."), 201
    else:
        return jsonify(message="Class session does not exist."), 404


#------------------------------Teachings Section---------------------------------------------------------------------------------
@app.route('/api/v1.0/teaching', methods=['POST'])
def add_teaching():
    """
    This api adds one teaching record to the DB.
    """
    session_id = request.json['session_id']
    teacher_id = request.json['teacher_id']

    class_session = ClassSession.query.filter_by(id=session_id, deleted=False).first()
    teacher = Teacher.query.filter_by(id=teacher_id, deleted=False).first()

    if class_session and teacher:
        # Class Session and Teacher must both exist
        already_existed = Teaching.query.filter_by(session_id=session_id, teacher_id=teacher_id, deleted=False).first()
        if already_existed:
            return jsonify(message="The class_session entry already exists"), 409
        else:
            teaching = Teaching()
            teaching.teacher = teacher
            teaching.class_session = class_session
            teaching.comments = request.json['comments']
            db.session.add(teaching)
            db.session.commit()
            return jsonify(message="Teaching added successfully"), 201
    else:
        return jsonify(message="Teacher or Class Session do not exist."), 404


@app.route('/api/v1.0/teaching', methods=['PUT'])
def update_teaching():
    """
    This api updates one teaching record in the DB.
    """
    session_id = request.json['session_id']
    teacher_id = request.json['teacher_id']

    teaching = Teaching.query.filter_by(session_id=session_id, teacher_id=teacher_id, deleted=False).first()
    if teaching:
        teaching.comments = request.json['comments']
        db.session.add(teaching)
        db.session.commit()
        return jsonify(message="Teaching updated successfully."), 201
    else:
        return jsonify(message="Teaching do not exist."), 404


@app.route('/api/v1.0/teacher_teachings', methods=['GET'])
def get_teacher_teachings():
    """
    This api gets a list of teaching record by its teacher_id.
    """
    teacher_id = request.args.get('teacher_id', None)

    teachings = Teaching.query.filter_by(teacher_id=teacher_id, deleted=False).all()
    if teachings:
        return jsonify(teachings_schema.dump(teachings)), 201
    else:
        return jsonify(message="Teachings do not exist."), 404


@app.route('/api/v1.0/class_session_teachings', methods=['GET'])
def get_class_session_teaching():
    """
    This api gets a list of teaching record by its session_id.
    """
    session_id = request.args.get('session_id', None)

    teachings = Teaching.query.filter_by(session_id=session_id, deleted=False).all()
    if teachings:
        return jsonify(teachings_schema.dump(teachings)), 201
    else:
        return jsonify(message="Teachings do not exist."), 404


@app.route('/api/v1.0/teaching', methods=['DELETE'])
def delete_teaching():
    """
    This api deletes a teaching record by its session_id and teacher_id.
    """
    session_id = request.args.get('session_id', None)
    teacher_id = request.args.get('teacher_id', None)

    teaching = Teaching.query.filter_by(session_id=session_id, teacher_id=teacher_id, deleted=False).first()
    if teaching:
        teaching.deleted = True
        db.session.add(teaching)
        db.session.commit()
        return jsonify(message="Teaching deleted successfully."), 201
    else:
        return jsonify(message="Teaching do not exist."), 404


#--------------------------------Taking Class Section--------------------------------------------------------------------------
@app.route('/api/v1.0/taking_class', methods=['POST'])
def add_taking_class():
    """
    This api adds one taking_class record to the DB.
    """
    session_id = request.json['session_id']
    student_id = request.json['student_id']

    class_session = ClassSession.query.filter_by(id=session_id, deleted=False).first()
    student = Student.query.filter_by(id=student_id, deleted=False).first()

    if class_session and student:
        # Class Session and Student must both exist
        already_existed = TakingClass.query.filter_by(session_id=session_id, student_id=student_id, deleted=False).first()
        if already_existed:
            return jsonify(message="The class_session entry already exists"), 409
        else:
            taking_class = TakingClass()
            taking_class.student = student
            taking_class.class_session = class_session
            taking_class.comments = request.json['comments']
            db.session.add(taking_class)
            db.session.commit()
            return jsonify(message="TakingClass added successfully"), 201
    else:
        return jsonify(message="Student or Class Session do not exist."), 404


@app.route('/api/v1.0/taking_class', methods=['PUT'])
def update_taking_class():
    """
    This api updates one taking_class record in the DB.
    """
    session_id = request.json['session_id']
    student_id = request.json['student_id']

    taking_class = TakingClass.query.filter_by(session_id=session_id, student_id=student_id, deleted=False).first()
    if taking_class:
        taking_class.comments = request.json['comments']
        db.session.add(taking_class)
        db.session.commit()
        return jsonify(message="TakingClass updated successfully."), 201
    else:
        return jsonify(message="TakingClass do not exist."), 404


@app.route('/api/v1.0/student_taking_classes', methods=['GET'])
def get_student_taking_classes():
    """
    This api gets a list of taking_class record by its student_id.
    """
    student_id = request.args.get('student_id', None)

    taking_classes = TakingClass.query.filter_by(student_id=student_id, deleted=False).all()
    if taking_classes:
        return jsonify(taking_classes_schema.dump(taking_classes)), 201
    else:
        return jsonify(message="TakingClasss do not exist."), 404


@app.route('/api/v1.0/class_session_taking_classes', methods=['GET'])
def get_class_session_taking_classes():
    """
    This api gets a list of taking_class record by its session_id.
    """
    session_id = request.args.get('session_id', None)

    taking_classes = TakingClass.query.filter_by(session_id=session_id, deleted=False).all()
    if taking_classes:
        return jsonify(taking_classes_schema.dump(taking_classes)), 201
    else:
        return jsonify(message="TakingClasss do not exist."), 404


@app.route('/api/v1.0/taking_class', methods=['DELETE'])
def delete_taking_class():
    """
    This api deletes a taking_class record by its session_id and student_id.
    """
    session_id = request.args.get('session_id', None)
    student_id = request.args.get('student_id', None)

    taking_class = TakingClass.query.filter_by(session_id=session_id, student_id=student_id, deleted=False).first()
    if taking_class:
        taking_class.deleted = True
        db.session.add(taking_class)
        db.session.commit()
        return jsonify(message="TakingClass deleted successfully."), 201
    else:
        return jsonify(message="TakingClass do not exist."), 404


# @app.route('/api/v1.0/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     """
#     This api deletes a user by user's id from the DB.
#     """
#     id = user_id

#     user = User.query.filter_by(id=id, deleted=False).first()
#     if user:
#         user.deleted = True
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(user_schema.dump(user))
#     else:
#         return jsonify(message="User not found"), 404

"""
Todos:
    1. Add security to all APIs
    2. Add login function
    3. Add pagination support to returned lists
    4. Split single file into multiple files
"""


# @app.route('/login', methods=['POST'])
# def login():
#     if request.is_json:
#         email = request.json['email']
#         password = request.json['password']
#     else:
#         email = request.form['email']
#         password = request.form['password']

#     test = User.query.filter_by(email=email, password=password).first()
#     if test:
#         access_token = create_access_token(identity=email)
#         return jsonify(message='Login succeeded!', access_token=access_token)
#     else:
#         return jsonify(message='Bad email or password!'), 401


# @app.route('/addStudent', methods=['POST'])
# def addStudent():
#     email = request.form['email']
#     test = User.query.filter_by(email=email).first()
#     print(email)
#     if test:
#         return jsonify(message='That email already exists'), 409
#     else:
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         password = request.form['password']
#         user = User(first_name=first_name, last_name=last_name, email=email, password=password)
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(message='User created successfully.'), 201






# @app.route('/')
# def hello_world():
#     return 'Hello World!'


# @app.route('/super_simple')
# def super_simple():
#     return jsonify(message='Hello from the Planetary API.'), 200


# @app.route('/not_found')
# def not_found():
#     return jsonify(message='That resource was not found'), 404


# @app.route('/parameters')
# def parameters():
#     name = request.args.get('name')
#     age = int(request.args.get('age'))
#     if age < 18:
#         return jsonify(message='Sorry ' + name + ', you are not old enough.'), 401
#     else:
#         return jsonify(message='Welcome ' + name + ', you are old enough!')


# @app.route('/url_variables/<string:name>/<int:age>')
# def url_variables(name: str, age: int):
#     if age < 18:
#         return jsonify(message='Sorry ' + name + ', you are not old enough.'), 401
#     else:
#         return jsonify(message='Welcome ' + name + ', you are old enough!')


# @app.route('/planets', methods=['GET'])
# def planets():
#     planets_list = Planet.query.all()
#     result = planets_schema.dump(planets_list)
#     return jsonify(result)


# # database models
# class User(db.Model):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     email = Column(String, unique=True)
#     password = Column(String)


# class Planet(db.Model):
#     __tablename__ = 'planets'
#     planet_id = Column(Integer, primary_key=True)
#     planet_name = Column(String)
#     planet_type = Column(String)
#     home_star = Column(String)
#     mass = Column(Float)
#     radius = Column(Float)
#     distance = Column(Float)


# class UserSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'first_name', 'last_name', 'email', 'password')


# class PlanetSchema(ma.Schema):
#     class Meta:
#         fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# planet_schema = PlanetSchema()
# planets_schema = PlanetSchema(many=True)


if __name__ == '__main__':
    app.run(debug=True)
