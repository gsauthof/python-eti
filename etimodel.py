
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-2.0-or-later


import itertools


# XXX also move other shared functions:
#
# get_data_types
# get_structs
# get_templates
# group_members
# is_counter
# is_elementary
# is_enum
# is_fixed_string
# is_int
# is_padding
# is_unsigned
# is_var_string
# pp_int_type
# type_to_fmt

def get_max_sizes(st, dt):
    h = {}
    for name, e in dt.items():
        v = e.get('size', '0')
        h[name] = int(v)
    for name, e in itertools.chain((i for i in st.items() if i[1].get('type') != 'Message'),
                                   (i for i in st.items() if i[1].get('type') == 'Message')):
        s = 0
        for m in e:
            x = h.get(m.get('type'), 0)
            s += x  * int(m.get('cardinality'))
        h[name] = s
    return h

def get_min_sizes(st, dt):
    h = {}
    for name, e in dt.items():
        v = e.get('size', '0')
        if e.get('variableSize') is None:
            h[name] = int(v)
        else:
            h[name] = 0
    for name, e in itertools.chain((i for i in st.items() if i[1].get('type') != 'Message'),
                                   (i for i in st.items() if i[1].get('type') == 'Message')):
        s = 0
        for m in e:
            x = h.get(m.get('type'), 0)
            s += x  * int(m.get('minCardinality', '1'))
        h[name] = s
    return h
