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
    course_name = Column(String)

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

    # Relationships
    student = db.relationship("Student", backref="parents")
    parent = db.relationship("User", backref="students")


class Teaching(db.Model):
    __tablename__ = "teachings"

    session_id = Column(Integer, ForeignKey("classSessions.id"), primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), primary_key=True)
    deleted = Column(Boolean, default=False)

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
    english = Course(course_name='English')
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

@app.route('/api/v1.0/students', methods=['POST'])
def add_student():
    """
    This api adds one student to the DB.
    """
    name = request.json['name']
    deleted = request.json['deleted']

    already_existed = User.query.filter_by(name=name).first()
    if already_existed:
        return jsonify(message='The student already exists'), 409
    else:
        student = Student(name=name, deleted=deleted)
        db.session.add(student)
        db.session.commit()
        return jsonify(message="Student created successfully"), 201


@app.route('/api/v1.0/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """
    This api get one student from the DB by the student's id.
    """
    id = student_id

    student = Student.query.filter_by(id=id, deleted=False).first()
    if student:
        print(student)
        return jsonify(message="Stu")
        # return jsonify(message='The student already exists'), 409
    else:
        return jsonify(message="Student not found"), 404


"""
Todos:
    1. jsonify returned objects from the DB
    2. Add pagination support to returned lists
    3. Add CRUDs to all classes
    4. Add security to all APIs
    5. Add login page
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
