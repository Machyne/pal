#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2015, PAL Team.
# All rights reserved. See LICENSE for details.

from api.dominos.pizza_options import order_pizzas
from api.dominos.pizza_options import price_pizzas
from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parent
from pal.grammars.parser import parse
from pal.grammars.parser import search
from pal.grammars.text_to_int import text_to_int
from pal.services.base_service import Service
from pal.services.base_service import wrap_response


PIZZA_ORDER_REQUIRED_FIELDS = [
    ('name', {
        'type': 'str',
        'name': 'name',
    }),
    ('phone', {
        'type': 'str',
        'name': 'phone number',
    }),
    ('line1', {
        'type': 'str',
        'name': 'address line 1',
    }),
    ('line2', {
        'type': 'str',
        'name': 'address line 2',
    }),
    ('instructions', {
        'type': 'str',
        'name': 'delivery instructions',
    }),
    ('cc-number', {
        'type': 'hidden',
        'name': 'credit card number',
    }),
    ('cc-type', {
        'type': 'hidden',
        'name': 'credit card type',
    }),
    ('cc-expiration', {
        'type': 'hidden',
        'name': 'credit card expiration date',
    }),
    ('cvv', {
        'type': 'hidden',
        'name': 'cvv',
    }),
    ('cc-zip', {
        'type': 'hidden',
        'name': 'credit card zip code',
    }),
]


def extract_pizza_features(parse_tree):
    non_tops = set(search(parse_tree, 'negation_phrase topping_item'))
    all_tops = set(search(parse_tree, 'topping_item'))
    yes_tops = all_tops.difference(non_tops)

    crust_size = extract(parse_tree, 'crust_size') or 'medium'
    crust_type = extract(parse_tree, 'crust_type') or 'regular'
    crust = '{} {}'.format(crust_size, crust_type)

    num_pizzas = text_to_int(extract(parse_tree, 'number') or 'one')

    toppings = []
    for t in yes_tops:
        item = extract(t, 'topping_item')
        amount = 'normal'
        parent_ = parent(parse_tree, t)
        if parent and parent_[0] == 'ingredient':
            amount = extract(parent_, 'topping_amount') or amount
        toppings.append((item, amount))

    for t in non_tops:
        item = extract(t, 'topping_item')
        amount = 'none'
        toppings.append((item, amount))

    return {
        'crust': crust,
        'quantity': num_pizzas,
        'options': toppings,
    }


class DominosService(Service):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.grammar = get_grammar_for_service(self.__class__.short_name())
        self.cached_parse = None

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        query = params['query']
        parsed = parse(query, self.grammar)
        self.cached_parse = (query, parsed)
        return 100 if parsed else 0

    @wrap_response
    def go(self, params):
        query = params['query']
        if self.cached_parse and self.cached_parse[0] == query:
            parse_tree = self.cached_parse[1]
        else:
            parse_tree = parse(query, self.grammar)

        pizza = extract_pizza_features(parse_tree)

        # Case 1: Pizza pricing query
        if extract(parse_tree, 'price_query'):
            price = price_pizzas([pizza])
            if price:
                return "It costs $" + "{:20,.2f}.".format(price).strip()
            else:
                return ('ERROR', "I think it's more than zero dollars...")

        # Case 2: Pizza order query
        ud = params.get('user-data', {})
        needs = [req for req in PIZZA_ORDER_REQUIRED_FIELDS
                 if req[0] not in ud]
        if needs:
            return ('NEEDS DATA - USER', needs)

        card = {
            'num': ud['cc-number'].strip(),
            'type': ud['cc-type'].strip(),
            'expire': ud['cc-expiration'].strip(),
            'cvv': ud['cvv'].strip(),
            'zip': ud['cc-zip'].strip(),
        }
        address = [ud['line1'], ud['line2']]
        res = order_pizzas(ud['phone'], ud['name'], address,
                           card, [pizza])
        if res.get('msg', '') == 'Pizza complete.':
            return "I just finished ordering! Your pizza is on its way!"
        else:
            msg, dts = res.get('msg', ''), res.get('details', '')
            return ('ERROR', "Sorry, I couldn't finish the order.<br><br>{}"
                             "<br>{}<br><br>But you could try calling "
                             "Dominos.".format(msg, dts))
