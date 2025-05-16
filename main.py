# 13 May, 2025
# Student Management App
# Created by me (Alex Mai)

from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
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
    dob: Mapped[str] = mapped_column(String(100), nullable=False)
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
    start_date: Mapped[str] = mapped_column(String(100), nullable=False)


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
class StudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    dob = StringField('Date of Birth', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    faculty_id = IntegerField('Faculty')
    gpa = FloatField('Gpa')
    submit = SubmitField('Submit Post')


@app.route('/', methods=['GET', 'POST'])
def get_student():
    students = db.session.execute(db.select(Student)).scalars().all()
    return render_template('index.html', students=students)


@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    # faculty = Faculty(
    #     name='Engineering',
    # )
    # db.session.add(faculty)
    # db.session.commit()
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
        return redirect(url_for('get_student', students=students))
    return render_template('student-form.html', form=form, faculties=faculties)


@app.route('/delete-student/', methods=['GET', 'POST'])
def delete_student():
    form = StudentForm()

    if form.validate_on_submit():
        student = db.get_or_404(Student, form.id)
        db.session.delete(student)
        db.session.commit()
        students = db.session.execute(db.select(Student)).scalars().all()
        return redirect(url_for('get_student', students=students))
    print('yesss')
    return render_template('delete.html', form=form)


@app.route('/edit-student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = db.get_or_404(Student, id)
    form = StudentForm(
        name=student.name,
        email=student.email,
        dob=student.dob,
        gender=student.gender,
    )

    if form.validate_on_submit():
        student.name = form.name.data
        student.email = form.email.data
        student.dob = form.dob.data
        student.gender = form.gender.data
        db.session.commit()
        students = db.session.execute(db.select(Student)).scalars().all()
        return redirect(url_for('get_student', students=students))

    return render_template('student-form.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
