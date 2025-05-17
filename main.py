# 13 May, 2025
# Student Management App
# Created by me (Alex Mai)
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Float, DATETIME, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField, FloatField
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
    __tablename__ = 'students'
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)
    faculty_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('faculties.id'))


class Student(Person):
    __tablename__ = 'students'
    faculty = relationship('Faculty', back_populates='students')
    gpa: Mapped[float] = mapped_column(Float, nullable=False)


class Instructor(Person):
    __tablename__ = 'instructors'
    faculty = relationship('Faculty', back_populates='instructors')
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Faculty(db.Model):
    __tablename__ = 'faculties'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[int] = mapped_column(String(250), nullable=False, unique=True)
    students = relationship('Student', back_populates='faculty')
    instructors = relationship('Instructor', back_populates='faculty')


class Course(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)
    date_of_week: Mapped[int] = mapped_column(Integer, nullable=False)


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
    submit = SubmitField('Submit Post')


class FacultyForm(FlaskForm):
    name = StringField('Faculty name', validators=[DataRequired()])


@app.route('/', methods=['GET', 'POST'])
def get_all():
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()
    faculties = db.session.execute(db.select(Faculty)).scalars().all()
    return render_template('index.html', students=students, instructors=instructors, faculties=faculties)


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
    return render_template('faculty-form.html', form=form)


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
    faculties = db.session.execute(db.select(faculty)).scalars().all()
    return redirect(url_for('get_all', facultys=faculties))


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

    return render_template('student-form.html', form=form, faculties=faculties)


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
    faculties = db.session.execute(db.select(Faculty)).scalars().all()

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

    return render_template('instructor-form.html', form=form, faculties=faculties)


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

        faculties = db.session.execute(db.select(Student)).scalars().all()
        return redirect(url_for('get_all', students=faculties))

    return render_template('faculty-form.html', form=form, faculties=faculties)


if __name__ == '__main__':
    app.run(debug=True)
