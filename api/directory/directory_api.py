from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from models import Building, Major, Student, FacStaff, Department


class IDNotFoundException(Exception):
    pass


class Directory(object):

    def init_db_connection(self):
        """ Set up a connection to the database """
        Base = declarative_base()
        engine = create_engine(
            'postgresql://postgres:bestdatabase@cmc307-01.mathcs.carleton.edu/stalkernet')
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def cleanup(self):
        """ Tear down the connection to the database """
        self.session.commit()
        self.session.close()

    def get_id(self, ORMClass, name):
        """ get the id associated with an ORM class (specifically Building, Major, and Department) """
        query = self.session.query(ORMClass).filter(
            ORMClass.name.contains(name))
        if query.count() > 0:
            result = query[0]
            id = result.id
            return id
        else:
            raise IDNotFoundException(
                "ID not found for {0} named {1}".format(ORMClass.__name__, name))

    def find_people(self, first_name=None, last_name=None, email=None, phones=None, building=None, room=None, major=None, department=None):
        """
        Query the database to find people with specific attributes.
        If the building, major, or department arguments are used, this function should be
        wrapped in a try/except block as an IDNotFoundException may be thrown if an ID number
        cannot be matched to the name of the parameter given. 

        Arguments:
            first_name: First name of person to find
            last_name: Last name of person to find
            email: email address (complete with @carleton.edu)
            phones: phone numbers. must be an array of integers
            building: name of either the office building or dorm
            room: string of either the room number or office number to search for
            major: name of student's major
            department: name of department for faculty/staff

        Return: 
            The return of this fucntion is a dictionary with two keys: 'studnets' and 'facstaff'.
            Each key corresponds to a list of either Student or FacStaff objects.
        """

        # query students table first
        filters = []

        # get ids of departments, buildings if available
        building_id = None
        if building != None:
            building_id = self.get_id(Building, building)
            filters.append(Student.building_id.__eq__(building_id))
        if major != None:
            major_id = self.get_id(Major, major)
            filters.append(Student.majors.contains([major_id]))

        # build out filters for the rest of the parameters
        if first_name != None:
            filters.append(Student.first_name.like(first_name))
        if last_name != None:
            filters.append(Student.last_name.like(last_name))
        if email != None:
            filters.append(Student.email.__eq__(email))
        if phones != None:
            filters.append(Student.phones.contains([long(p) for p in phones]))
        if room != None:
            filters.append(Student.room.contains(room))

        # run the query
        query = self.session.query(Student).filter(and_(*filters))
        results = {}
        results["students"] = [q for q in query]

        # query fac-staff table
        filters = []

        if building_id != None:
            filters.append(FacStaff.office_building_id.__eq__(building_id))
        if department != None:
            department_id = self.get_id(Department, department)
            filters.append(FacStaff.department_id.__eq__(department_id))

        if first_name != None:
            filters.append(FacStaff.first_name.like(first_name))
        if last_name != None:
            filters.append(FacStaff.last_name.like(last_name))
        if email != None:
            filters.append(FacStaff.email.__eq__(email))
        if phones != None:
            filters.append(FacStaff.phones.contains([long(p) for p in phones]))
        if room != None:
            filters.append(FacStaff.office.like(room))

        query = self.session.query(FacStaff).filter(and_(*filters))
        results["facstaff"] = [q for q in query]

        return results

    def __init__(self):
        self.session = self.init_db_connection()
