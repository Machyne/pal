#!/usr/bin/env python
# coding: utf-8
#
# Module for all the tests
#
# Author: Alex Simonides

from os import path


def parse_examples():
    """ Reads in the example query file and returns a dictionary with service
        names as keys and a list of queries as values.
    """
    file_path = path.realpath(path.join(path.dirname(__file__),
                                        "examples.txt"))
    examples = {}

    with open(file_path) as ex_file:
        service = ex_file.next().strip()
        queries = []
        for line in ex_file:
            if line == "\n":
                examples[service] = queries
                queries = []
                try:
                    service = ex_file.next().strip()
                    continue
                except StopIteration:
                    break

            queries.append(line.strip())

    return examples
