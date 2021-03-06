#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.
#
# A service for the Carleton directory
import re

from api.directory.models import Building
from api.directory.directory_api import Directory

from pal.services.base_service import Service
from pal.services.base_service import wrap_response


class NotEnoughInformationException(Exception):
    pass


def format_phone_num(num):
    if not isinstance(num, str):
        num = str(num)
    num = re.sub(r'\D', '', num)
    if len(num) == 11:
        base = '+{} '.format(num[0])
        num = num[1:]
    elif len(num) == 10:
        base = ''
    else: return num
    base += '({}) {}-{}'
    return base.format(num[:3], num[3:6], num[6:])


class DirectoryService(Service):

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        return super(self.__class__, self).get_confidence(params)

    @wrap_response
    def go(self, params):
        features = params['features']
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
            if (lenstudents + lenfacstaff) == 0:
                raise NotEnoughInformationException(
                    "Couldn't find anyone named {0} {1} at Carleton.".format(
                        first_name, last_name))
            noun_words = [x[0].lower() for x in nouns if x[1] != 'PERSON']

            # answer where a student lives
            room_keywords = {'room', 'dorm', 'house', 'hall'}
            if (len(room_keywords.intersection(set(noun_words))) or
                    len(room_keywords.intersection(set(keywords))) > 0 or
                    question_type == 'LOC'):
                if lenstudents == 0:
                    raise NotEnoughInformationException(
                        "Couldn't find any student named {0} {1}.".format(
                            first_name, last_name))
                matching_students = matching_people['students']
                student = matching_students[0]
                building_name = directory.get_name_for_id(
                    Building, student.building_id)
                return "{0} {1} lives in {2} {3}.".format(
                    first_name, last_name,
                    building_name, student.room)

            # answer where a faculty/staff office is
            office_keywords = {'office'}
            if (len(office_keywords.intersection(set(noun_words))) or
                    len(room_keywords.intersection(set(keywords))) > 0):
                matching_facstaff = matching_people['facstaff']
                if lenfacstaff == 0:
                    raise NotEnoughInformationException(
                        "Could not find {0} {1}".format(first_name, last_name))
                facstaff = matching_facstaff[0]
                building_name = directory.get_name_for_id(
                    Building, facstaff.office_building_id)
                return "{0} {1}'s office is {2} {3}.".format(
                    first_name, last_name,
                    building_name, facstaff.office)

            # answer phone numbers
            phone_keywords = {'phone', 'number', 'call'}
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
                    return ("{0} {1} doesn't seem to have any phone numbers "
                            "listed.".format(first_name, last_name))
                elif len(phones) == 1:
                    num, pretty = phones[0], format_phone_num(phones[0])
                    return ("{0} {1}'s phone number is "
                        "<a href=\"tel:{2}\">{3}</a>.").format(
                        first_name, last_name, num, pretty)
                else:
                    pnums = ', '.join(["<a href=tel:{}>{}</a>".format(
                        p, format_phone_num(p)) for p in phones])
                    return "{0} {1}'s phone numbers are {2}.".format(
                        first_name, last_name, pnums)

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
                    return ("{0} {1} doesn't seem to have an email address "
                            "listed.".format(first_name, last_name))
                else:
                    return ("{0} {1}'s email address is <a href=\"mailto:{2}\">"
                            "{2}</a>.").format(
                        first_name, last_name, email)
        elif len(full_names) > 1:
            # these types of questions pertain to 2 or more people
            # i.e. "Does Matt live with Ken?"
            return ('ERROR',
                    "Sorry, I don't support multi-person queries yet.")
        directory.cleanup()
        return ('ERROR',
                "Sorry, I'm not that good at stalking.")
