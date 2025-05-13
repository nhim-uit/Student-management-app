# 13 May, 2025
# Student Management App
# Created by me (Alex Mai)
from datetime import datetime

from django.db.models import ForeignKey
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from nbclient.client import timestamp
from sqlalchemy import Integer, String, DATETIME, Float
from sqlalchemy.dialects.mssql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xgvdf3423*&%'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
db = SQLAlchemy(model_class=Base)
db.init_app()


class Person(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[datetime] = mapped_column(DATETIME, nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)


class Student(Person):
    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey('faculty'))
    faculty = relationship('Faculty', back_populates='instructor')


class Instructor(Person):
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DATETIME, nullable=False)

    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey('faculty'))
    faculty = relationship('Faculty', back_populates='instructor')


class Faculty(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[int] = mapped_column(String(250), nullable=False)

    instructor = relationship('Instructor', back_populates='faculty')
    student = relationship('Student', back_populates='faculty')


class Course(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DATETIME, nullable=False)
    date_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    

with app.app_context():
    db.create_all()


@app.route('/')
def get_student():
    students = db.session.execute(db.select(Student)).scalars.all()
    return render_template('index.html', students=students)
