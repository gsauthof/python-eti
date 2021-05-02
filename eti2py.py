#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later


import itertools
import re
import sys
import xml.etree.ElementTree as ET


def gen_version(d, o=sys.stdout):
    r = d.getroot()
    version = r.get('version')
    sub_version = r.get('subVersion')
    build = r.get('buildNumber')
    print(f"version = '{version}'", file=o)
    print(f"sub_version = '{sub_version}'", file=o)
    print(f"build = '{build}'\n", file=o)

def get_data_types(d):
    r = d.getroot()
    x = r.find('DataTypes')
    h = {}
    for e in x:
        h[e.get('name')] = e
    return h

def get_structs(d):
    r = d.getroot()
    x = r.find('Structures')
    h = {}
    for e in x:
        h[e.get('name')] = e
    return h

def get_templates(st):
    ts = []
    for k, v in st.items():
        if v.get('type') == 'Message':
            ts.append((int(v.get('numericID')), k))
    ts.sort()
    return ts

def get_usages(d):
    def scan(m, h, p=''):
        for f in m:
            u = f.get('usage')
            if u is not None:
                h[p + m.get('name'), f.get('name')] = u
            elif f.tag == 'Group':
                scan(f, h, m.get('name') + '.')
    h = {}
    r = d.getroot()
    ms = r.find('ApplicationMessages')
    for m in ms:
        scan(m, h)
    return h

def get_message_flows(d):
    def parse_mf(cs, field=None):
        xs = []
        for c in cs:
            cond = None
            if field is not None:
                cond = f'{field} is {c.get("condition")}'
            if c.tag == 'Node':
                xs.append( (None, cond, parse_mf(c, field=c.get('name'))) )
            else:
                xs.append( (c.get('name'), cond, parse_mf(c)) )
        return xs
    r = d.getroot()
    mfs = r.find('MessageFlows')
    h = {}
    for mf in mfs:
        m = mf.find('Message')
        h[m.get('name')] = parse_mf(m)
    return h

def get_sizes(st, dt):
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
            if x == 0 or m.get('minCardinality') is not None:
                s = 0
                break
            s += x
        h[name] = s
    return h

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

def gen_header(o=sys.stdout):
    print('''# auto-generated by Georg Sauthoff's eti2py.py
import struct
from dataclasses import dataclass, field, is_dataclass
from enum import IntEnum

def rstrip_dc(x):
    for k, v in x.__dict__.items():
        if type(v) is bytes:
            x.__setattr__(k, x.__getattribute__(k).rstrip(b'\\0'))
        elif is_dataclass(v):
            rstrip_dc(v)

def enumerize(i, klasse):
    try:
        return klasse(i)
    except ValueError:
        return i
''', file=o)

def gen_enums(dt, ts, o=sys.stdout):
    def pp_nv(e, vs):
        nv = e.get('noValue')
        if nv in vs:
            return
        if nv.startswith('0x0'):
            nv = '0'
        if nv:
            print(f'    NO_VALUE = {nv}', file=o)


    print('class TemplateID(IntEnum):', file=o)
    for tid, name in ts:
        print(f'    {name} = {tid}', file=o)
    print('', file=o)
    for name, e in dt.items():
        if e.get('type') == 'int':
            vs = e.findall('ValidValue')
            if vs:
                vs.sort(key = lambda x : int(x.get('value')))
                ws = [ v.get('value') for v in vs ]
                print(f'class {name}(IntEnum):', file=o)
                for v in vs:
                    print(f'    {v.get("name").upper()} = {v.get("value")}', file=o)
                pp_nv(e, ws)
                print(file=o)
        elif e.get('rootType') == 'String' and e.get('size') == '1':
            vs = e.findall('ValidValue')
            if vs:
                vs.sort(key = lambda x : x.get('value'))
                ws = [ v.get('value') for v in vs ]
                print(f'class {name}(IntEnum):', file=o)
                for v in vs:
                    print(f'''    {v.get("name").upper()} = ord('{v.get("value")}')''', file=o)
                pp_nv(e, ws)
                print(file=o)

def is_int(t):
    if t is not None:
        r = t.get('rootType')
        return r in ('int', 'floatDecimal') or (r == 'String' and t.get('size') == '1')
    return False

def is_enum(t):
    if t is not None:
        r = t.get('rootType')
        if r == 'int' or (r == 'String' and t.get('size') == '1'):
            return t.find('ValidValue') is not None
    return False

pad_re = re.compile('Pad[1-9]')

def is_padding(t):
    if t is not None:
        return t.get('rootType') == 'String' and pad_re.match(t.get('name'))
    return False

def is_fixed_string(t):
    if t is not None:
        return t.get('rootType') in ('String', 'data') and not t.get('variableSize')
    return False

def is_var_string(t):
    if t is not None:
        return t.get('rootType') in ('String', 'data') and t.get('variableSize') is not None
    return False

def is_unsigned(t):
    v = t.get('minValue')
    return v is not None and not v.startswith('-')

def is_counter(t):
    return t.get('type') == 'Counter'

def type_to_fmt(t):
    if is_padding(t):
        return f'{t.get("size")}x'
    elif is_int(t):
        n = int(t.get('size'))
        if n == 1:
            return 'B'
        else:
            if n == 2:
                c = 'h'
            elif n == 4:
                c = 'i'
            elif n == 8:
                c = 'q'
            else:
                raise ValueError(f'unknown int size {n}')
            if is_unsigned(t):
                c = c.upper()
            return c
    elif is_fixed_string(t):
        return f'{t.get("size")}s'
    else:
        return '?'

def pp_int_type(t):
    if not is_int(t):
        return None
    s = 'i'
    if is_unsigned(t):
        s = 'u'
    n = int(t.get('size'))
    s += str(n)
    return s

def is_elementary(t):
    return t is not None and t.get('counter') is None

def group_members(e, dt):
    xs = []
    ms = []
    for m in e:
        t = dt.get(m.get('type'))
        if is_elementary(t):
            ms.append(m)
        else:
            if ms:
                xs.append(ms)
                ms = []
            xs.append([m])
    if ms:
        xs.append(ms)
    return xs

def gen_fields(e, st, dt, us, sizes, min_sizes, version, o=sys.stdout, comment=False, off=0, fname=None):
    for m in e:
        if comment:
            print('    #', end='')
        atts = []
        t = dt.get(m.get('type'))
        if is_padding(t):
            print(f'    # PADDING={t.get("size")}', end='', file=o)
        elif is_int(t):
            atts.append(pp_int_type(t))
            def_str = '0'
            nv = t.get('noValue')
            if nv:
                def_str = nv
            if def_str == '0x00' or is_counter(t):
                def_str = '0'
            elif def_str.startswith('0x80'):
                def_str = str(2**(8*int(t.get('size')) - 1) * -1)
            if is_enum(t):
                atts.append(f'enum:{t.get("name")}')
                def_str = f"{t.get('name')}({def_str})"
            print(f'    {m.get("name")}: int = {def_str}', end='', file=o)
            scale = t.get('precision')
            if scale:
                atts.append(f'scale:{scale}')
        elif is_fixed_string(t) or is_var_string(t):
            if is_var_string(t):
                atts.append(f'length:{m.get("counter")}')
            # when packing, struct.pack right-pads missing bytes with zero bytes
            def_str = "b''"
            if m.get('type') == 'DefaultCstmApplVerID':
                def_str = f"b'{version[0]}'"
            if m.get('type') == 'DefaultCstmApplVerSubID':
                def_str = f"b'{version[1]}'"
            print(f"""    {m.get("name")}: bytes = {def_str}""", end='', file=o)
        else:
            if m.get('type') in ('MessageHeaderInComp', 'MessageHeaderOutComp', 'MessageHeaderComp'):
                l = sizes[e.get('name')]
                if l == 0:
                    l = min_sizes[e.get('name')]
                def_str = f'field(default_factory=lambda : {m.get("type")}({l}, {e.get("numericID")}))'
            else:
                def_str = f'field(default_factory={m.get("type")})'
            if m.get('minCardinality') is None:
                print(f'    {m.get("name")}: {m.get("type")} = {def_str}', end='', file=o)
            else:
                print(f'    {m.get("name")}: [{m.get("type")}] = field(default_factory=list)', end='', file=o)

        atts.append(f'fmt:{type_to_fmt(t)}')
        atts.append(f'size:{sizes[m.get("type")]}')
        if off is not None:
            atts.append(f'off:{off}')
        u = us.get((fname if fname else e.get('name'), m.get('name')), None)
        if not is_padding(t) and u and u != 'mandatory':
            atts.append(u.upper())
        print(f' # {", ".join(atts)}', file=o)

        s = st.get(m.get('type'))
        if s:
            gen_fields(s, st, dt, us, sizes, min_sizes, version, o, comment=True, off=off, fname=f"{e.get('name')}.{m.get('name')}")

        if off is not None:
            l = sizes[m.get('type')]
            if l == 0:
                off = None
            else:
                off += l


def gen_block(name, e, st, dt, us, sizes, min_sizes, max_sizes, version, o=sys.stdout):
    print(f'@dataclass\nclass {name}:')
    print(f'    sizes = ({min_sizes[name]}, {max_sizes[name]})\n', file=o)
    gen_fields(e, st, dt, us, sizes, min_sizes, version, o)

    ms = group_members(e, dt)

    print(f'\n    def update_length(self):', file=o)
    if sizes[name] == 0 and e.get('type') == 'Message':
        header = 'MessageHeaderOut' if e.find('Member[@name="MessageHeaderIn"]') is None else 'MessageHeaderIn'
        ls = []
        for xs in ms:
            t = dt.get(xs[0].get('type'))
            l = sum(sizes[m.get("type")] for m in xs)
            if is_var_string(t):
                ls.append(f'self.{xs[0].get("counter")}')
            elif xs[0].get('minCardinality') is not None:
                ls.append(f'self.{xs[0].get("counter")} * {l}')
            else:
                ls.append(str(l))
        print(f'        self.{header}.BodyLen = {" + ".join(ls)}', file=o)
    else:
        print(f'        pass', file=o)
    print(file=o)

    fs = [ ("'<" + ''.join(type_to_fmt(dt.get(a.get('type'))) for a in xs) + "'") for xs in ms ]
    print(f'    fmt = ( {", ".join(fs)}, )', file=o)

    print(f'    _struct = [ {", ".join("None" for _ in ms)} ]', file=o)
    print('''
    @classmethod
    def st(cls, i):
        if cls._struct[i] is None:
            cls._struct[i] = struct.Struct(cls.fmt[i])
        return cls._struct[i]''', file=o)

    gen_pack(name, e, st, dt, sizes, min_sizes, max_sizes, ms, o)
    gen_unpack(name, e, st, dt, sizes, min_sizes, max_sizes, ms, o)

    gen_setter(o)

    print('    def rstrip(self):\n        rstrip_dc(self)', file=o)

    print('', file=o)


def gen_setter(o=sys.stdout):
    print('''    def __setattr__(self, k, v): 
        if k not in self.__annotations__: 
            raise AttributeError(f'{self.__class__.__name__} dataclass has no field {k}')
        super().__setattr__(k, v)''', file=o)


def gen_pack(name, e, st, dt, sizes, min_sizes, max_sizes, ms, o=sys.stdout):
    print('    def pack_into(self, buf, off=0):', file=o)
    off = 0
    dyn = False
    for i, xs in enumerate(ms):
        t = dt.get(xs[0].get('type'))
        args = ', '.join('self.' + m.get('name') for m in xs if not is_padding(dt.get(m.get('type'))))
        if not dyn:
            if off == 0:
                off_str = 'off'
            else:
                off_str = f'off + {off}'
        l = sum(sizes[m.get("type")] for m in xs)
        if is_elementary(t):
            print(f'        self.st({i}).pack_into(buf, {off_str}, {args})', file=o)
            if dyn:
                print('f    o += l', file=o)
        else:
            if is_var_string(t):
                if not dyn:
                    print(f'        o = off + {off}', file=o)
                    dyn = True
                    off_str = 'o'
                print(f'        struct.pack_into(f"<{{self.{xs[0].get("counter")}}}s", buf, {off_str}, self.{xs[0].get("name")})', file=o)
                print(f'        o += self.{xs[0].get("counter")}', file=o)
            elif xs[0].get('minCardinality') is not None:
                if not dyn:
                    print(f'        o = off + {off}', file=o)
                    dyn = True
                    off_str = 'o'
                print(f'        for v in self.{xs[0].get("name")}:', file=o)
                print(f'            v.pack_into(buf, {off_str})', file=o)
                print(f'            o += {l}')
            else:
                print(f'        self.{xs[0].get("name")}.pack_into(buf, {off_str})', file=o)
                if dyn:
                    print('f    o += l', file=o)
        off += l

    if dyn:
        print('        return o', file=o)
    else:
        print(f'        return off + {off}', file=o)
    if max_sizes[name] ==  sizes[name]:
        print(f'''    def pack(self):
        bs = bytearray({sizes[name]})
        self.pack_into(bs)
        return bytes(bs)''', file=o)
    else:
        print(f'''    def pack(self):
        bs = bytearray({max_sizes[name]})
        n = self.pack_into(bs)
        mv = memoryview(bs)
        return bytes(mv[:n])''', file=o)
    print(file=o)

def gen_unpack(name, e, st, dt, sizes, min_sizes, max_sizes, ms, o=sys.stdout):
    print('    def unpack_from(self, buf, off=0):', file=o)
    off = 0
    dyn = False
    for i, xs in enumerate(ms):
        t = dt.get(xs[0].get('type'))
        args = ', '.join('self.' + m.get('name') for m in xs if not is_padding(dt.get(m.get('type'))))
        if not dyn:
            if off == 0:
                off_str = 'off'
            else:
                off_str = f'off + {off}'
        l = sum(sizes[m.get("type")] for m in xs)
        if is_elementary(t):
            print(f'        {args} = self.st({i}).unpack_from(buf, {off_str})', file=o)
            es = [ m for m in xs if is_enum(dt.get(m.get('type'))) ]
            lhs = ', '.join('self.' + e.get('name') for e in es)
            rhs = ', '.join(f"enumerize(self.{e.get('name')}, {dt.get(e.get('type')).get('name')})" for e in es)
            if lhs:
                print(f'        {lhs} = {rhs}', file=o)
            if dyn:
                print('f    o += l', file=o)
        else:
            if is_var_string(t):
                if not dyn:
                    print(f'        o = off + {off}', file=o)
                    dyn = True
                    off_str = 'o'
                print(f'        self.{xs[0].get("name")} = struct.unpack_from(f"<{{self.{xs[0].get("counter")}}}s", buf, {off_str})', file=o)
                print(f'        o += self.{xs[0].get("counter")}', file=o)
            elif xs[0].get('minCardinality') is not None:
                if not dyn:
                    print(f'        o = off + {off}', file=o)
                    dyn = True
                    off_str = 'o'
                print(f'        self.{xs[0].get("name")} = []', file=o)
                print(f'        for i in range(self.{xs[0].get("counter")}):', file=o)
                print(f'            v = {xs[0].get("type")}.create_from(buf, {off_str})', file=o)
                print(f'            self.{xs[0].get("name")}.append(v)', file=o)
                print(f'            o += {l}')
            else:
                print(f'        self.{xs[0].get("name")}.unpack_from(buf, {off_str})', file=o)
                if dyn:
                    print('f    o += l', file=o)
        off += l

    if dyn:
        print('        return o', file=o)
    else:
        print(f'        return off + {off}', file=o)
    print(f'''    @staticmethod\n    def create_from(buf, off=0):
        obj = {name}()
        obj.unpack_from(buf, off)
        return obj''', file=o)
    print(file=o)


def gen_blocks(version, st, dt, us, o=sys.stdout):
    sizes = get_sizes(st, dt)
    min_sizes = get_min_sizes(st, dt)
    max_sizes = get_max_sizes(st, dt)
    for name, e in st.items():
        if e.get('type') == 'Message':
            continue
        gen_block(name, e, st, dt, us, sizes, min_sizes, max_sizes, version, o)
    for name, e in st.items():
        if e.get('type') != 'Message':
            continue
        gen_block(name, e, st, dt, us, sizes, min_sizes, max_sizes, version, o)


def gen_unpack_factory(ts, dt, o=sys.stdout):
    n = ts[-1][0] - ts[0][0] + 1
    a = ts[0][0]
    b = ts[-1][0]
    xs = [None] * n
    for tid, name in ts:
        xs[tid-a] = name
    s = ',\n        '.join('None' if x is None else x for x in xs)
    print(f'tid2class = [', file=o)
    tid = a
    for tid, x in enumerate(xs, tid):
        if x is None:
            print(f'              None, # {tid}', file=o)
        else:
            print(f'              {x}, # {tid}', file=o)
    print(f']\n', file=o)

    bl_size = dt['BodyLen'].get('size')

    print(f'''tid_st = struct.Struct('<{bl_size}xH')

class UnpackError(Exception):
    pass
''', file=o)

    print(f'''def unpack_from(bs, off=0):
    tid = tid_st.unpack_from(bs, off)[0]
    if tid < {a} or tid  > {b}:
        raise UnpackError(f'template ID out of range: {{tid}} not in [{a}..{b}]')
    c = tid2class[tid-{a}]
    if c is None:
        raise UnpackError(f'unknown template ID: {{tid}}')
    return c.create_from(bs, off)
''', file=o)


def gen_message_flows(mf, o=sys.stdout):
    def f(xs):
        print('[ ', end='', file=o)
        for name, cond, cs in xs:
            s = name
            t = 'None' if cond is None else f"'{cond}'"
            print(f'( {s}, {t}, ', end='', file=o)
            f(cs)
            print(f' ),', end='', file=o)
        print(' ]', end='', file=o)
    print('request2response = {', file=o)
    for k, v in mf.items():
        print(f'    TemplateID.{k}: ', end='', file=o)
        f(v)
        print(',', file=o)
    print('}\n', file=o)


def main():
    filename = sys.argv[1]
    d = ET.parse(filename)

    version = (d.getroot().get('version'), d.getroot().get('subVersion'))
    dt = get_data_types(d)
    st = get_structs(d)
    ts = get_templates(st)

    us = get_usages(d)

    mf = get_message_flows(d)

    gen_header()
    gen_version(d)
    gen_enums(dt, ts)
    gen_blocks(version, st, dt, us)

    gen_unpack_factory(ts, dt)

    gen_message_flows(mf)


if __name__ == '__main__':
    sys.exit(main())
