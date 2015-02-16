#!/usr/bin/env python
# coding: utf-8
#
# The base class for tests
#
# Author: Alex Simonides

import unittest

from flask.ext.testing import TestCase as FlaskTestCase

from server import app


class PALTestCase(object):
    """ TestCase wrapper that abstracts unittest.TestCase from our tests."""

    # unittest.TestCase aliases ----------------------------------------------

    @staticmethod
    def assert_is_instance(obj, cls, msg=None):
        unittest.TestCase.assertIsInstance(obj, cls, msg)

    @staticmethod
    def assert_in(member, container, msg=None):
        unittest.TestCase.assertIn(member, container, msg)

    @staticmethod
    def assert_not_none(obj, msg=None):
        unittest.TestCase.assertIsNotNone(obj, msg)

    @staticmethod
    def assert_equal(obj1, obj2, msg=None):
        unittest.TestCase.assertEqual(obj1, obj2, msg)

    # Custom methods ---------------------------------------------------------

    @classmethod
    def assert_keys(cls, dict_, keys, check_values=True):
        """ Assert that a dictionary `dict_` has entries mapped to each of
            the strings in `keys`.
        :param dict_: A python dictionary to be tested.
        :param keys: A list of strings to be found in `dict_`.
        :param check_values: A boolean flag whether to assert that a value
                             exists for each key.
        :raises: AssertionError if `dict_` either:
                 (a) is missing at least one of `keys`.
                 (b) is missing a value for at least one of `keys`
                     (if `check_values` is True).
        """
        cls.assert_is_instance(dict_, dict, "`dict_` must a dictionary!")
        for key in keys:
            cls.assert_in(key, dict_,
                          "\"{}\" is missing from `dict_`:"
                          "\n{}".format(key, dict_))
            if check_values:
                cls.assert_not_none(dict_[key],
                                    "`dict_` has the key \"{}\","
                                    " but it has no value:\n{}".format(key,
                                                                       dict_))

    @classmethod
    def assert_data_matches_format(cls, data, expected_format=None):
        """ Assert that `data` matches the expected format.
        :param data: The object to be tested.
        :param expected_format: A format for the data to match.
        """

        if expected_format is basestring:
            return cls.assert_is_instance(data, basestring)
        elif isinstance(expected_format, list):
            # use lists for items of the same type/format
            cls.assert_equal(len(expected_format), 1,
                             "`expected_format` for a lists should have "
                             "1 item that dictates the format of the items"
                             " in the list.")
            cls.assert_is_instance(data, list)
            for item in data:
                cls.assert_data_matches_format(item, expected_format[0])
        else:
            cls.assert_is_instance(expected_format, dict,  # programmer error
                                   "Format is expected to be basestring, list"
                                   ", or dict.")

            for key in data:
                value_format = expected_format.get(key, None)
                cls.assert_not_none(value_format,
                                    "`expected_format` must have a type or "
                                    "description for each key (If you meant "
                                    "for the value to be None, use NoneType "
                                    "as the format value).")
                if isinstance(value_format, type):
                    cls.assert_is_instance(data[key], value_format,
                                           "The value for \"{}\" should be "
                                           "{}.".format(key, value_format))

                elif isinstance(value_format, (list, dict)):
                    # nested description, recurse
                    cls.assert_data_matches_format(data[key], value_format)


class ServerTestCase(FlaskTestCase, PALTestCase):
    """ TestCase class for live server tests"""
    def create_app(self):
        app.config['TESTING'] = True
        return app
