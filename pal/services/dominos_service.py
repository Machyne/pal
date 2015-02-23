from api.dominos.pizza_options import order_pizza
from pal.grammars import get_grammar_for_service
from pal.grammars.parser import extract
from pal.grammars.parser import parent
from pal.grammars.parser import parse
from pal.grammars.parser import search
from pal.services.service import Service
from pal.services.service import wrap_response

class DominosService(Service):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.grammar = get_grammar_for_service(self.__class__.short_name())
        self.cached_parse = None

    def applies_to_me(self, client, feature_request_type):
        return True

    def get_confidence(self, params):
        query = params['query']

        # TODO: shouldn't have to do this
        if query[-1] in '.!?':
            query = query[:-1]

        parse_ = parse(query, self.grammar)
        self.cached_parse = (query, parse_)
        if parse_:
            return 60 + super(self.__class__, self).get_confidence(params)
        return 0

    @wrap_response
    def go(self, params):
        query = params['query']

        # TODO: shouldn't have to do this
        if query[-1] in '.!?':
            query = query[:-1]

        if self.cached_parse and self.cached_parse[0] == query:
            parse_tree = self.cached_parse[1]
        else:
            parse_tree = parse(query, self.grammar)

        non_tops = set(search(parse_tree, 'negation_phrase topping_item'))
        all_tops = set(search(parse_tree, 'topping_item'))
        yes_tops = all_tops.difference(non_tops)

        crust_size = extract('crust_size', parse_tree) or 'medium'
        crust_type = extract('crust_type', parse_tree) or 'regular'
        crust = '{} {}'.format(crust_size, crust_type)

        toppings = []
        for t in yes_tops:
            item = extract('topping_item', t)
            amount = 'normal'
            parent_ = parent(parse_tree, t)
            if parent and parent_[0] == 'ingredient':
                amount = extract('topping_amount', t) || amount
            toppings.append((item, amount))

        if extract('price_query', parse_tree):
            return "It costs nine hundred dollars."

        ud = params.get('user-data', {})
        required = [
            ('name', {
                'type': 'str',
                'name': 'name',
            }),
            ('phone', {
                'type': 'str',
                'name': 'phone number',
            }),
            ('address', {
                'type': 'str',
                'name': 'address',
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
        needs = []
        for req in required:
            if req[0] not in ud:
                needs.append(req)
        if len(needs):
            return ('NEEDS DATA - USER', needs)

        return 'pizza coming soon'
