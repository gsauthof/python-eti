#!/usr/bin/env python3


# Dump ETI/EOBI packets from a pcap file
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later


import argparse
import dpkt
import struct
import sys

import eobi.v9_0 as eobi
import eti.v9_0 as eti

from dressup import pformat


def dump_eobi(bs, dump_heartbeat):
        n = len(bs)

        ph = eobi.unpack_from(bs)
        ph.rstrip()
        assert ph.MessageHeader.TemplateID == eobi.TemplateID.PacketHeader

        i    = ph.MessageHeader.BodyLen
        tail = bs
        k    = 0

        if i < n:
            m = eobi.unpack_from(tail[i:])
            m.rstrip()
            if (m.MessageHeader.TemplateID != eobi.TemplateID.Heartbeat
                    or dump_heartbeat):
                print(f'EOBI-Begin: {pformat(ph, width=45)}')
                print(f'EOBI-Message: {pformat(m, width=45)}')
            else:
                return
            i += m.MessageHeader.BodyLen
            k += 1
        else:
            raise RuntimeError('EOBI PacketHeader without messages')

        while i < n:
            m = eobi.unpack_from(tail[i:])
            m.rstrip()
            i += m.MessageHeader.BodyLen
            k += 1
            print(f'EOBI-Message: {pformat(m, width=45)}')
        print(f'EOBI-End: {k} messages in {n} bytes')

eti_head_st = struct.Struct('<IH')

def dump_eti(bsP):

    bs = bsP
    i = 0
    xs = []

    while True:
        m = eti.unpack_from(bs)
        m.rstrip()
        t = ''
        if i > 0:
            t = f' ({i})'
        print(f'ETI-Message{t}: {pformat(m, width=45)}')
        bl, tid = eti_head_st.unpack_from(bs)
        if len(bs) != bl:
            print(f'WARNING: trailing bytes after ETI message: size(payload)={len(bs)} vs. size(msg)={bl}')
            bs = bs[bl:]
            i += 1
            xs.append(eti.TemplateID(tid).name)
        else:
            if i > 0:
                i += 1
                xs.append(eti.TemplateID(tid).name)
                print(f'ETI-packet of {i} messages: {",".join(xs)}')
            break


def parse_args():
    p = argparse.ArgumentParser(description='Dump ETI/EOBI messages from PCAP files')
    p.add_argument('filename', help='PCAP file')
    p.add_argument('--love', '-l', action='store_true', help='also dump EOBI heartbeat packets')
    args = p.parse_args()
    return args

def main():
    args = parse_args()

    with open(args.filename, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)

        for ts, buf in pcap:
            print(f'Captured @ {ts}')
            eth = dpkt.ethernet.Ethernet(buf)
            ip  = eth.data

            if not isinstance(ip, dpkt.ip.IP):
                continue

            tp = ip.data

            if isinstance(tp, dpkt.udp.UDP):
                udp     = tp
                payload = memoryview(udp.data)
                dump_eobi(payload, args.love)
            elif isinstance(tp, dpkt.tcp.TCP):
                tcp     = tp
                payload = memoryview(tcp.data)
                try:
                    dump_eti(payload)
                except struct.error:
                    print(f'WARNING: non-ETI @{ts}')
                except IndexError:
                    print(f'WARNING: non-ETI unknown template ID @{ts}')
                except AttributeError:
                    print(f'WARNING: non-ETI unknown template ID @{ts}')


if __name__ == '__main__':
    sys.exit(main())


