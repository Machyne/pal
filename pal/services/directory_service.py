import sys
from api.directory.models import Building, Major, Student, Department, FacStaff
from api.directory.directory_api import Directory

from .abstract_service import AbstractService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# but that's not working for some reason...


class DirectoryService(AbstractService):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return 1

    def go(self, features):

        directory = Directory()

        # pull the person's record out of the database
    	nouns = features['nouns']
        full_names = [x for x in nouns[x] if x[1] == 'PERSON']

        if len(full_names) == 1:
            # these types of questions only pertain to 1 person
            full_name = full_names[0]
            first_name = full_name[0]
            last_name = full_name[-1]

            # answer where someone lives
            # if "building" in nouns or 

            matching_people = directory.find_people(first_name=first_name, last_name=last_name)

        else:
            # these types of questions pertain to 2 or more people
            # i.e. "Does Matt live with Ken?"
            pass

        directory.cleanup()

        # return {'response': "Tom Hanks was in 1 movies."}
