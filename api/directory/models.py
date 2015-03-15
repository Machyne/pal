#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Building(Base):
	__tablename__ = 'buildings'

	id = Column(Integer, primary_key = True)
	name = Column(String, unique = True)

	def __repr__(self):
		return "<Building(%s)>" % self.name


class Major(Base):
	__tablename__ = 'majors'

	id = Column(Integer, primary_key = True)
	name = Column(String, unique = True)

	def __repr__(self):
		return "<Major(%s)>" % self.name

class Department(Base):
	__tablename__ = 'departments'

	id = Column(Integer, primary_key = True)
	name = Column(String, unique = True)

	def __repr__(self):
		return "<Department(%s)>" % self.name


class Student(Base):
	__tablename__ = 'students'

	id = Column(Integer, primary_key = True)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String, unique = True)
	class_year = Column(Integer)
	building_id = Column(Integer, ForeignKey('buildings.id'))
	room = Column(String)
	phones = Column(ARRAY(BigInteger))
	majors = Column(ARRAY(Integer))
	status = Column(String)

	dorm = relationship("Building")

	def __repr__(self):
		return "<Student(%s %s, %s)>" % (self.first_name, self.last_name, self.class_year)


class FacStaff(Base):
	__tablename__ = 'facstaff'

	id = Column(Integer, primary_key = True)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String, unique = True)
	titles = Column(ARRAY(String))
	department_id = Column(Integer, ForeignKey('departments.id'))
	office_building_id = Column(Integer, ForeignKey('buildings.id'))
	office = Column(String)
	phones = Column(ARRAY(BigInteger))

	department = relationship("Department")
	office_building = relationship("Building")

	def __repr__(self):
		return "<FacStaff(%s %s)>" % (self.first_name, self.last_name)



if __name__ == '__main__':
	engine = create_engine('postgresql+psycopg2://postgres:bestdatabase@cmc307-01.mathcs.carleton.edu/stalkernet', echo = True)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(engine)