#!/usr/bin/env python
# coding: utf-8
#
# Module for all the tests
#
# Author: Alex Simonides and Ken Schiller

from collections import defaultdict
from os import path


EXAMPLES_FILE = path.realpath(path.join(path.dirname(__file__),
                              "examples.txt"))


def parse_examples():
    """ Reads in the example query file and returns a dictionary with service
        names as keys and a list of queries as values.
    """
    with open(EXAMPLES_FILE) as f:
        examples = defaultdict(list)
        service_name = None
        for line in f:
            line = line.strip()
            if service_name is None:
                if line:
                    service_name = line
            else:
                if line:
                    examples[service_name].append(line)
                else:
                    service_name = None
    return examples
