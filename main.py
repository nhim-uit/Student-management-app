# 13 May, 2025
# Student Management App
# Created by me (Alex Mai)
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xgvdf3423*&%'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Person(db.Model):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    faculty_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('faculties.id'))


class Student(Person):
    __tablename__ = 'students'
    faculties = relationship('Faculty', back_populates='students')
    gpa: Mapped[float] = mapped_column(Float, nullable=False)


class Instructor(Person):
    __tablename__ = 'instructors'
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    faculties = relationship('Faculty', back_populates='instructors')
    faculty_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('faculties.id'))
    courses = relationship('Course', back_populates='instructors')


class Faculty(db.Model):
    __tablename__ = 'faculties'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    students = relationship('Student', back_populates='faculties')
    instructors = relationship('Instructor', back_populates='faculties')
    courses = relationship('Course', back_populates='faculties')


class Course(db.Model):
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    credit: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    instructors = relationship('Instructor', back_populates='courses')
    faculty_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('faculties.id'))
    instructor_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('instructors.id'))
    faculties = relationship('Faculty', back_populates='courses')


with app.app_context():
    db.create_all()


# FORMS
class PersonForm(FlaskForm):
    __abstract__ = True
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('F', 'Female'), ('M', 'Male')], validators=[DataRequired()])
    faculty_id = SelectField('Faculty',
                             choices=[(1, 'Computer Science'), (2, 'Engineering'), (3, 'Arts')],
                             validators=[DataRequired()])


class StudentForm(PersonForm):
    gpa = FloatField('Gpa') # will add gpa table later
    submit = SubmitField('Submit Post')


class InstructorForm(PersonForm):
    salary = FloatField('Salary', validators=[DataRequired()])
    start_date = DateField('Start date', validators=[DataRequired()])
    faculty_id = SelectField('Faculty',
                             choices=[(1, 'Computer Science'), (2, 'Engineering'), (3, 'Arts')],
                             validators=[DataRequired()])
    submit = SubmitField('Submit Post')


class FacultyForm(FlaskForm):
    name = StringField('Faculty name', validators=[DataRequired()])
    submit = SubmitField('Submit Post')


class CourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    start_time = DateField('Start time', validators=[DataRequired()])
    end_time = DateField('End time', validators=[DataRequired()])
    credit = IntegerField('Credit', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])

    instructors = relationship('Instructor', back_populates='course')
    faculty_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('faculties.id'))
    instructor_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('instructors.id'))
    submit = SubmitField('Submit Post')


@app.route('/add-my-faculty', methods=['GET', 'POST'])
def add_my_faculty():
    faculty1 = Faculty(
        name='Computer Science'
    )
    faculty2 = Faculty(
        name='Engineering'
    )
    db.session.add(faculty1)
    db.session.add(faculty2)
    db.session.commit()
    return redirect(url_for('get_all'))


@app.route('/', methods=['GET', 'POST'])
def get_all():
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()
    faculties = db.session.execute(db.select(Faculty)).scalars().all()
    courses = db.session.execute(db.select(Course)).scalars().all()

    student_count = db.session.execute(db.func.count(Student.id)).scalar()
    instructor_count = db.session.execute(db.func.count(Instructor.id)).scalar()
    faculty_count = db.session.execute(db.func.count(Faculty.id)).scalar()
    course_count = db.session.execute(db.func.count(Course.id)).scalar()

    return render_template('index.html',
                           students=students,
                           instructors=instructors,
                           faculties=faculties,
                           courses=courses,
                           student_count=student_count,
                           instructor_count=instructor_count,
                           faculty_count=faculty_count,
                           course_count=course_count)


@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    faculties = db.session.execute(db.select(Faculty)).scalars().all()

    if request.method == 'POST':
        student = Student(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            gender=form.gender.data,
            faculty_id=form.faculty_id.data,
            gpa=form.gpa.data
        )
        db.session.add(student)
        db.session.commit()

        students = db.session.execute(db.select(Student)).scalars().all()
        instructors = db.session.execute(db.select(Instructor)).scalars().all()
        return redirect(url_for('get_all', students=students, instructors=instructors))
    return render_template('student-form.html', form=form, faculties=faculties)


@app.route('/add-instructor', methods=['GET', 'POST'])
def add_instructor():
    form = InstructorForm()

    if form.validate_on_submit():
        instructor = Instructor(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            gender=form.gender.data,
            salary=form.salary.data,
            start_date=form.start_date.data,
            faculty_id=form.faculty_id.data,
        )
        db.session.add(instructor)
        db.session.commit()

        instructors = db.session.execute(db.select(Instructor)).scalars().all()
        students = db.session.execute(db.select(Student)).scalars().all()
        return redirect(url_for('get_all', instructors=instructors, students=students))
    return render_template('instructor-form.html', form=form)


@app.route('/add-faculty', methods=['GET', 'POST'])
def add_faculty():
    form = FacultyForm()

    if form.validate_on_submit():
        faculty = FacultyForm(
            name=form.name.data,
        )
        db.session.add(faculty)
        db.session.commit()
        return redirect(url_for('get_all'))
    return render_template('faculty-form.html', form=form)


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()

    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            credit=form.credit.data,
            duration=form.duration.data,
            description=form.description.data,
            faculty_id=1,
            instructor_id=1,
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('get_all'))
    return render_template('course-form.html', form=form)


@app.route('/delete-student/', methods=['GET', 'POST'])
def delete_student():
    student_id = request.args.get('id')
    student = db.get_or_404(Student, student_id)

    db.session.delete(student)
    db.session.commit()
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()
    return redirect(url_for('get_all', students=students, instructors=instructors))


@app.route('/delete-instructor/', methods=['GET', 'POST'])
def delete_instructor():
    instructor_id = request.args.get('id')
    instructor = db.get_or_404(Instructor, instructor_id)

    db.session.delete(instructor)
    db.session.commit()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()
    students = db.session.execute(db.select(Student)).scalars().all()
    return redirect(url_for('get_all', instructors=instructors, students=students))


@app.route('/delete-faculty/', methods=['GET', 'POST'])
def delete_faculty():
    faculty_id = request.args.get('id')
    faculty = db.get_or_404(Faculty, faculty_id)

    db.session.delete(faculty)
    db.session.commit()
    faculties = db.session.execute(db.select(Faculty)).scalars().all()
    return redirect(url_for('get_all', faculties=faculties))


@app.route('/delete-course/', methods=['GET', 'POST'])
def delete_course():
    course_id = request.args.get('id')
    course = db.get_or_404(Course, course_id)

    db.session.delete(course)
    db.session.commit()

    return redirect(url_for('get_all'))


@app.route('/edit-student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = db.get_or_404(Student, id)
    form = StudentForm(
        name=student.name,
        email=student.email,
        dob=student.dob,
        gender=student.gender,
        gpa=student.gpa,
    )
    faculties = db.session.execute(db.select(Faculty)).scalars().all()

    if form.validate_on_submit():
        student.name = form.name.data
        student.email = form.email.data
        student.dob = form.dob.data
        student.gender = form.gender.data
        student.gpa = form.gpa.data

        db.session.commit()

        students = db.session.execute(db.select(Student)).scalars().all()
        return redirect(url_for('get_all', students=students))

    return render_template('student-form.html', form=form)


@app.route('/edit-course/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    course = db.get_or_404(Course, id)
    form = CourseForm(
        name=course.name,
        start_time=course.start_time,
        end_time=course.end_time,
        credit=course.credit,
        duration=course.duration,
        description=course.description,
    )
    faculties = db.session.execute(db.select(Faculty)).scalars().all()

    if form.validate_on_submit():
        course.name = form.name.data
        course.start_time = form.start_time.data
        course.end_time = form.end_time.data
        course.credit = form.credit.data
        course.duration = form.duration.data
        course.description = form.description.data

        db.session.commit()

        courses = db.session.execute(db.select(Course)).scalars().all()
        return redirect(url_for('get_all', courses=courses))

    return render_template('course-form.html', form=form, faculties=faculties)


@app.route('/edit-instructor/<int:id>', methods=['GET', 'POST'])
def edit_instructor(id):
    instructor = db.get_or_404(Instructor, id)
    form = InstructorForm(
        name=instructor.name,
        email=instructor.email,
        dob=instructor.dob,
        gender=instructor.gender,
        salary=instructor.salary,
        start_date=instructor.start_date,
    )

    if form.validate_on_submit():
        instructor.name = form.name.data
        instructor.email = form.email.data
        instructor.dob = form.dob.data
        instructor.gender = form.gender.data
        instructor.start_date = form.start_date.data
        instructor.salary = form.salary.data

        db.session.commit()

        instructors = db.session.execute(db.select(Instructor)).scalars().all()
        return redirect(url_for('get_all', instructors=instructors))

    return render_template('instructor-form.html', form=form)


@app.route('/edit-faculty/<int:id>', methods=['GET', 'POST'])
def edit_faculty(id):
    faculty = db.get_or_404(Faculty, id)
    form = FacultyForm(
        name=faculty.name,
    )
    faculties = db.session.execute(db.select(Faculty)).scalars().all()

    if form.validate_on_submit():
        faculty.name = form.name.data

        db.session.commit()

        faculties = db.session.execute(db.select(Faculty)).scalars().all()
        return redirect(url_for('get_all', students=faculties))

    return render_template('faculty-form.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
