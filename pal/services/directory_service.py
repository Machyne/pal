# A service for the Carleton directory

from api.directory.models import Building
from api.directory.directory_api import Directory

from pal.services.service import Service


class NotEnoughInformationException(Exception):
    pass


class DirectoryService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, features):
        return super(self.__class__, self).get_confidence(features)

    def go(self, features):
        # print features
        directory = Directory()

        nouns = features['nouns']
        keywords = features['keywords']
        full_names = [x for x in nouns if x[1] == 'PERSON']
        question_type = features['questionType']

        if len(full_names) == 1:
            # these types of questions only pertain to 1 person
            full_name = full_names[0][0].split()
            first_name = full_name[0]
            last_name = full_name[-1]

            matching_people = directory.find_people(
                first_name=first_name, last_name=last_name)

            lenstudents = len(matching_people['students'])
            lenfacstaff = len(matching_people['facstaff'])
            if ((lenstudents > 0 and lenfacstaff > 0) or
                    (lenstudents > 1 or lenfacstaff > 1)):
                raise NotEnoughInformationException(
                    "Too many matches found for name: {0} {1}".format(
                        first_name, last_name))

            noun_words = [x[0].lower() for x in nouns if x[1] != 'PERSON']

            # answer where a student lives
            room_keywords = set(['room', 'dorm', 'house', 'hall'])
            if (len(room_keywords.intersection(set(noun_words))) or
                    len(room_keywords.intersection(set(keywords))) > 0 or
                    question_type == 'LOC'):
                matching_students = matching_people['students']
                student = matching_students[0]
                building_name = directory.get_name_for_id(
                    Building, student.building_id)
                return {'response': 1,
                        'summary': "{0} {1} lives in {2} {3}".format(
                            first_name, last_name,
                            building_name, student.room)}

            # answer where a faculty/staff office is
            office_keywords = set(['office'])
            if (len(office_keywords.intersection(set(noun_words))) or
                    len(room_keywords.intersection(set(keywords))) > 0):
                matching_facstaff = matching_people['facstaff']
                if len(matching_facstaff) == 0:
                    raise NotEnoughInformationException(
                        "Could not find {0} {1}".format(first_name, last_name))
                facstaff = matching_facstaff[0]
                building_name = directory.get_name_for_id(
                    Building, facstaff.office_building_id)
                return {'response': 1,
                        'summary': "{0} {1}'s office is {2} {3}".format(
                            first_name, last_name,
                            building_name, facstaff.office)}

            # answer phone numbers
            phone_keywords = set(['phone', 'number', 'call'])
            if (len(phone_keywords.intersection(noun_words)) > 0 or
                    len(phone_keywords.intersection(set(keywords)))):
                phones = []
                if lenstudents > 0:
                    phones = matching_people['students'][0].phones
                elif lenfacstaff > 0:
                    phones = matching_people['facstaff'][0].phones
                else:
                    raise NotEnoughInformationException(
                        "Could not find {0} {1}".format(first_name, last_name))

                if len(phones) == 0:
                    return {'response': 1,
                            'summary': "{0} {1} doesn't seem to have any "
                                       "phone numbers listed".format(
                                           first_name, last_name)}
                elif len(phones) == 1:
                    return {'response': 1,
                            'summary': "{0} {1}'s phone number is "
                                       "{2}".format(
                                           first_name, last_name, phones[0])}
                else:
                    pnums = ', '.join([str(p) for p in phones])
                    return {'response': 1,
                            'summary': "{0} {1}'s phone numbers are "
                                       "{2}".format(first_name,
                                                    last_name,
                                                    pnums)}

            # answer email questions
            email_keywords = set(['email', 'e-mail', 'mail'])
            if (len(email_keywords.intersection(noun_words)) > 0 or
                    len(email_keywords.intersection(set(keywords)))):
                email = ''
                if lenstudents > 0:
                    email = matching_people['students'][0].email
                elif lenfacstaff > 0:
                    email = matching_people['facstaff'][0].email
                else:
                    raise NotEnoughInformationException(
                        "Could not find {0} {1}".format(first_name, last_name))

                if email == '':
                    return {'response': 1,
                            'summary': "{0} {1} doesn't seem to have an "
                                       "email address listed"
                                       "".format(first_name, last_name)}
                else:
                    return {'response': 1,
                            'summary': "{0} {1}'s email address is "
                                       "{2}".format(first_name,
                                                    last_name, email)}
        else:
            # these types of questions pertain to 2 or more people
            # i.e. "Does Matt live with Ken?"
            directory.cleanup()
            return {'response': 0,
                    'summary': 'Sorry, multi person queries not supported.'}
