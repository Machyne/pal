import json

import requests

TOPPINGS = {
    # Cheese
    'C': 'cheese',
    # Sauce
    'X': ('robust inspired tomato sauce', 'tomato sauce', 'sauce'),
    'Xm': 'marinara sauce',
    'Xw': 'white sauce',
    'Bq': ('barbecue sauce', 'bbq sauce'),
    # Meats
    'P': 'pepperoni',
    'S': ('italian sausage', 'sausage'),
    'Sb': ('sliced italian sausage', 'sliced sausage'),
    'B': 'beef',
    'Pm': ('philly steak', 'steak'),
    'H': 'ham',
    'K': 'bacon',
    'Sa': 'salami',
    'Du': ('premium chicken', 'chicken'),
    # Cheese Toppings
    'E': ('cheddar cheese', 'cheddar'),
    'Fe': ('feta cheese', 'feta'),
    'Cs': ('shredded parmesan asiago', 'parmesan', 'asiago'),
    'Cp': ('shredded provolone cheese', 'provolone'),
    # Veggies / Fruit / Other
    'Z': 'banana peppers',
    'R': 'black olives',
    'V': ('green olives', 'olives'),
    'G': ('green pepper', 'pepper'),
    'J': ('jalapeno peppers', 'jalapenos', 'jalapeno'),
    'M': 'mushrooms',
    'N': 'pineapple',
    'O': ('onions', 'onion'),
    'Rr': ('roasted red pepper', 'red pepper'),
    'Si': 'spinach',
    'Td': ('diced tomatoes', 'tomatoes', 'tomato'),
    'Ht': 'hot sauce',
}

# (names): (format, (size_options))
CRUSTS = {
    ('hand tossed', 'regular'): ("{}SCREEN", (10, 12, 14, 16)),
    ('pan', 'handmade pan'): ("P{}IPAZA", (10,)),
    ('thin', 'crunchy thin'): ("{}THIN", (10, 12, 14)),
    ('brooklyn', 'brooklyn style'): ("PBKERIZA", (14,)),
    ('gfree', 'gluten free'): ("P{}IGFZA", (10,)),
}

SIZES = {
    'small': 10,
    'medium': 12,
    'large': 14,
    'xlarge': 16,
    10: 10,
    12: 12,
    14: 14,
    16: 16,
}

AMOUNTS = {
    'no': 0.0,
    'none': 0.0,
    'light': 0.5,
    'normal': 1.0,
    'extra': 1.5,
    'double': 2.0,
    'triple': 3.0,
    0.0: 0.0,
    0.5: 0.5,
    1.0: 1.0,
    1.5: 1.5,
    2.0: 2.0,
    3.0: 3.0,
}

_DUMMY_CARD = {
    'num': "4444888888888888",
    'type': "VISA",
    'expire': "1017",
    'cvv': "189",
    'zip': "55057",
}


def _topping_amount(full=None, left=None, right=None):
    if sum(AMOUNTS[x or 0] for x in (full, left, right)) == 0:
        return 0
    if full is not None:
        return {'1/1': AMOUNTS[full]}
    left, right = left or 0, right or 0
    return {'1/2': AMOUNTS[left], '2/2': AMOUNTS[right]}


def _get_crust(size, crust):
    crust = crust.lower()
    if isinstance(size, str):
        size = size.lower()
    for names in CRUSTS:
        if crust in names:
            format_str, sizes = CRUSTS[names]
            size = SIZES[size]
            if size in sizes:
                return format_str.format(size)
            else:
                return format_str.format(sizes[0])
    return '12SCREEN'


def _get_topping_code(topping):
    for code, names in TOPPINGS.iteritems():
        if topping in names:
            return code
    return topping


def _pizzas_to_products(pizzas):
    products = []
    for pizza in pizzas:
        pie = {'options': {}}
        size, _, crust_type = pizza['crust'].partition(' ')
        pie['crust'] = _get_crust(size, crust_type)
        pie['quantity'] = pizza['quantity']
        for topping, amount in pizza['options']:
            if not isinstance(amount, dict):
                amount = {'full': amount}
            code = _get_topping_code(topping)
            pie['options'][code] = _topping_amount(**amount)
        products.append(pie)
    return products


def order_pizzas(phone, name, address, card, pizzas, instructions=''):
    name_parts = name.rpartition(' ')
    data = {
        'phone': phone,
        'firstName': name_parts[0] or name_parts[-1],
        'lastName': name_parts[-1],
        'address': address,
        'card': card,
        'instr': instructions,
        'pizzas': _pizzas_to_products(pizzas),
    }

    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post("http://localhost:8000", data=data, headers=headers)
        return r.json()
    except Exception:
        return {'msg': "Couldn't communicate with Dominos."}


def price_pizzas(pizzas, address='1 N College St, Northfield, MN 55057',
                 instructions=''):
    data = {
        'phone': '2024561111',
        'firstName': 'Pizza',
        'lastName': 'Price',
        'address': address,
        'card': _DUMMY_CARD,
        'instr': instructions,
        'pizzas': _pizzas_to_products(pizzas),
        'onlyPrice': True,
    }
    data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    r = requests.post("http://localhost:8000", data=data, headers=headers)
    try:
        resp = r.json()
        return resp.get('price', False)
    except Exception:
        return False


if __name__ == '__main__':
    card = _DUMMY_CARD
    phone = '2024561111'
    name = 'Test Tester'
    address = ['1 N College St', 'Northfield, MN 55057']
    instructions = 'Please come to the Weitz Center, room 236.'
    pizza = {
        'crust': 'medium thin',
        'quantity': 1,
        'options': [
            ('cheese', 'no'),
            ('sauce', 'extra'),
            ('mushrooms', 'normal'),
            ('jalapeno', 'normal'),
        ],
    }
    print price_pizzas([pizza], address, instructions)
    print order_pizzas(phone, name, address, card, [pizza], instructions)
