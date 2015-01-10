import sys
from api.directory.models import Building, Major, Student, Department, FacStaff
from api.directory.directory_api import Directory

from .abstract_service import AbstractService


class NotEnoughInformationException(Exception):
    pass


class DirectoryService(AbstractService):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return 1

    def go(self, features):

        directory = Directory()

        # pull the person's record out of the database
        nouns = features['nouns']
        full_names = [x for x in nouns if x[1] == 'PERSON']

        if len(full_names) == 1:
            # these types of questions only pertain to 1 person
            full_name = full_names[0][0].split()
            first_name = full_name[0]
            last_name = full_name[-1]

            matching_people = directory.find_people(
                first_name=first_name, last_name=last_name)

            noun_words = [x[0] for x in nouns if x[1] != 'PERSON']

            # answer where a student lives
            room_keywords = set(['room', 'dorm', 'house', 'hall'])
            if len(room_keywords.intersection(set(noun_words))) > 0:
                matching_students = matching_people['students']
                if len(matching_students) > 1:
                    raise NotEnoughInformationException(
                        "Too many matches found for name: {0} {1}".format(first_name, last_name))
                student = matching_students[0]
                building_name = directory.get_name_for_id(
                    Building, student.building_id)
                return {'response': "{0} {1} lives in {2} {3}".format(first_name, last_name, building_name, student.room)}

            # answer where a faculty/staff office is
            office_keywords = set(['office'])
            if len(office_keywords.intersection(set(noun_words))) > 0:
                matching_facstaff = matching_people['facstaff']
                if len(matching_facstaff) > 1:
                    raise NotEnoughInformationException(
                        "Too many matches found for name: {0} {1}".format(first_name, last_name))
                elif len(matching_facstaff) == 0:
                    raise NotEnoughInformationException(
                        "Could not find {0} {1}".format(first_name, last_name))
                facstaff = matching_facstaff[0]
                building_name = directory.get_name_for_id(
                    Building, facstaff.office_building_id)
                return {'response': "{0} {1} works in {2} {3}".format(first_name, last_name, building_name, facstaff.office)}

        else:
            # these types of questions pertain to 2 or more people
            # i.e. "Does Matt live with Ken?"
            pass

        directory.cleanup()
        return

        # return {'response': "Tom Hanks was in 1 movies."}
