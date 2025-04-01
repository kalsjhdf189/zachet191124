from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

Base = declarative_base()

class Department(Base):
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True)
    department_name = Column(String)
    
class Duty(Base):
    __tablename__ = "duty"
    
    id = Column(Integer, primary_key=True)
    duty_name = Column(String)
    
class Skill(Base):
    __tablename__ = "skill"
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String)
    
    employee_rel = relationship("EmployeeSkill", back_populates="skill_rel")
    
class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    id_duty = Column(Integer, ForeignKey('duty.id'))
    id_department = Column(Integer, ForeignKey('department.id'))
    date_in = Column(Date)
    
    dep_rel = relationship("Department")
    duty_rel = relationship("Duty")
    skill_rel = relationship("EmployeeSkill", back_populates="employee_rel")
    
class EmployeeSkill(Base):
    __tablename__ = "employee_skill"
    
    id = Column(Integer, primary_key=True)
    id_employee = Column(Integer, ForeignKey('employee.id'))
    id_skill = Column(Integer, ForeignKey('skill.id'))
    
    employee_rel = relationship("Employee", back_populates="skill_rel")
    skill_rel = relationship("Skill", back_populates="employee_rel")

class Connect:
    @staticmethod
    def create_connection():
        engine = create_engine("postgresql://postgres:1234@localhost:5432/postgres")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session