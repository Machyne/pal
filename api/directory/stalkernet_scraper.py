from models import Building, Major, Student, Department, FacStaff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import argparse
import requests
from bs4 import BeautifulSoup
import re
import string

Base = declarative_base()


def getSession():
    engine = create_engine(
        'postgresql://postgres:bestdatabase@cmc307-01.mathcs.carleton.edu/stalkernet')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# ----------------------------------
#       Setup the database
# ----------------------------------


def addBuildings(args):
    """ Insert buildings into buildings table from a text file """

    filename = args
    session = getSession()
    with open(filename) as f:
        for line in f:
            building_name = line.replace('\n', '')
            building = Building(name=building_name)
            session.add(building)
            try:
                session.commit()
            except Exception, e:
                print e
                session.rollback()


def addMajors(args):
    """ Insert majors into majors table from a text file """

    filename = args
    session = getSession()
    with open(filename) as f:
        for line in f:
            major_name = line.replace('\n', '')
            major = Major(name=major_name)
            session.add(major)
            try:
                session.commit()
            except Exception, e:
                print e
                session.rollback()
    session.close()


def addDepartments(args):
    """ Insert fac/staff departments into the departments table from a text file """

    filename = args
    session = getSession()
    with open(filename) as f:
        for line in f:
            department_name = line.replace('\n', '')
            department = Department(name=department_name)
            session.add(department)
            try:
                session.commit()
            except Exception, e:
                print e
                session.rollback()
    session.close()


# ----------------------------------
#       Scraping Stuff
# ----------------------------------

def getIds(ORMClass):
    """ get a dictionary whose key is the ORM class name and value is the ORM id in the database """
    session = getSession()
    names = {}
    for entry in session.query(ORMClass.id, ORMClass.name):
        id = entry[0]
        name = entry[1]
        names[name] = id
    session.close()
    return names

# def getIdsForMajors():
# 	""" get a dictionary whose key is the major name and value is the id in the database """
# 	session = getSession()
# 	majors = {}
# 	for entry in session.query(Major.id, Major.name):
# 		id = entry[0]
# 		name = entry[1]
# 		majors[name] = id
# 	session.close()
# 	return majors

# def getIdsForBuildings():
# 	""" get a dictionary whose key is the building name and value is the id in the database """
# 	session = getSession()
# 	buildings = {}
# 	for entry in session.query(Building.id, Building.name):
# 		id = entry[0]
# 		name = entry[1]
# 		buildings[name] = id
# 	session.close()
# 	return buildings

# def getIdsForDepartments():
# 	""" get a dictionary whose key is the department name and value is the id in the database """
# 	session = getSession


def scrape():
    baseUrl = 'http://apps.test.carleton.edu/campus/directory'
    allBuildings = getIds(Building)

    # for key in allBuildings:
    for fi in string.lowercase:
        for li in string.lowercase:
            # print 'searching for %s in %s' % (letter, key)
            print 'creeping on first initial: %s, last initial: %s' % (fi, li)
            payload = {'first_name': fi, 'last_name': li}
            r = requests.get(baseUrl, params=payload)
            # print r.status_code
            parseResultsPage(r.text)
        # parseResultsPage(r.text, 57)


def textWithNewlines(element):
    """ For some reason BeautifulSoup's .text strips <br/> tags, so replace all instances of <br/> in the text with \n.
    From http://stackoverflow.com/questions/5925385/remove-br-tags-from-a-parsed-beautiful-soup-list
    """
    text = ''
    for e in element.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text


def parseResultsPage(htmlContent):
    soup = BeautifulSoup(htmlContent)
    session = getSession()

    majorIds = getIds(Major)
    buildingIds = getIds(Building)
    departmentIds = getIds(Department)

    for person in soup.find_all(class_='person'):

        # get the name
        full_name = person.find('h2').text
        name_components = full_name.split()
        first_name = name_components[0]
        # assume 1 first name, 1 <= last names
        last_name = ' '.join(name_components[1:])

        status = None
        # get email
        # some people (like dining staff) don't have emails
        try:
            email = person.find(class_='email').text
        except Exception, e:
            email = None

        # get room and room number
        location = room = person.find(class_='location')
        building_id = None
        if location:
            # person definietly on campus
            room = location.find('a')
            if room:
                # building & room listed & on campus
                room = room.text
                building = ' '.join(
                    re.findall(r'(^[0-9]{3}|\b[A-z\-]+\b|\&)+', room))
                building_id = buildingIds[building]
                try:
                    room = re.findall(r'(\b[0-9]+[A-z]*\b)', room)
                    if room:
                        room = room[0]
                    else:
                        room = None
                except Exception, e:
                    # some fac/staff have no room number
                    print "error parsing room number for %s %s" % (first_name, last_name)
                    raise e
                    room = None
            else:
                # room not listed or nofo option
                building_id = None
                room = textWithNewlines(person.find(class_='location'))
        else:
            # person might be on leave or off campus
            try:
                status = person.find(class_='status')
                if status:
                    status = status.text
                    building_id = None
                    room = None
            except Exception, e:
                print "error parsing location for %s %s" % (first_name, last_name)
                raise e
                room = None

        # get phone numbers, accounting for possibility of 2 phone numbers per
        # row separated by /
        p = person.find_all(class_='telephone')
        phones = []
        for phone in p:
            psplit = phone.text.split('/')
            for phonenum in psplit:
                phones.append(int(phonenum.replace(' ', '').replace('-', '')))

        # determine if it is a student or fac/staff by checking for title
        if person.find(class_='title'):
            # it's fac/staff

            # get their titles
            titles = [title.text for title in person.find_all(class_='title')]

            # get the department
            dept_class = person.find(class_='dept')
            if dept_class:
                dept_link = dept_class.find('a')
                # some departments don't have a link (ex Maitenence)
                if dept_link:
                    dept_name = dept_link.text
                else:
                    dept_name = dept_class.text
                dept_id = departmentIds[dept_name]
            else:
                dept_id = None

            fs = FacStaff(
                first_name=first_name,
                last_name=last_name,
                email=email,
                titles=titles,
                department_id=dept_id,
                office_building_id=building_id,
                office=room,
                phones=phones
            )

            session.add(fs)
            try:
                session.commit()
            except Exception, e:
                print e
                session.rollback()

        else:
            # it's a student
            # get class year
            year_text = person.find(class_='affiliation').text
            year = None
            if year_text:
                # check that they're not an ole first
                if year_text == 'St Olaf Student':
                    building_id = buildingIds["St. Olaf"]
                    room = None
                else:
                    try:
                        year = int(year_text)
                    except Exception, e:
                        year = None

            # find majors
            majors = [major.text for major in person.find_all(class_='major')]
            major_ids = []
            for major in majors:
                try:
                    major_id = majorIds[major]
                    major_ids.append(major_id)
                except Exception, e:
                    print "Error parsing major for student %s" % (full_name)
                    print e
                    break

            # phones = [int(phone.text.replace(' ', '').replace('-', '')) for phone in person.find_all(class_ = 'telephone')]

            s = Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                class_year=year,
                building_id=building_id,
                room=room,
                phones=phones,
                majors=major_ids,
                status=status
            )

            session.add(s)
            try:
                session.commit()
            except Exception, e:
                print e
                session.rollback()

    session.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--add-buildings', type=addBuildings)
    parser.add_argument('-m', '--add-majors', type=addMajors)
    parser.add_argument('-d', '--add-departments', type=addDepartments)
    parser.add_argument('-s', '--scrape', action='store_true')
    args = parser.parse_args()
    if args.scrape:
        scrape()
        print "Creeping finished"

if __name__ == '__main__':
    main()
