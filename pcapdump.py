#!/usr/bin/env python3


# Dump ETI/EOBI packets from a pcap file
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later


import argparse
import dpkt
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
            i += m.MessageHeader.BodyLen
            k += 1
            if (m.MessageHeader.TemplateID != eobi.TemplateID.Heartbeat
                    or dump_heartbeat):
                print(f'EOBI-Begin: {pformat(ph, width=45)}')
                print(f'EOBI-Message: {pformat(m, width=45)}')
            else:
                return
        else:
            raise RuntimeError('EOBI PacketHeader without messages')

        while i < n:
            m = eobi.unpack_from(tail[i:])
            m.rstrip()
            i += m.MessageHeader.BodyLen
            k += 1
            print(f'EOBI-Message: {pformat(m, width=45)}')
        print(f'EOBI-End: {k} messages in {n} bytes')


def dump_eti(bs):
    m = eti.unpack_from(bs)
    m.rstrip()
    print(f'ETI-Message: {pformat(m, width=45)}')
    if len(bs) != m.MessageHeader.BodyLen:
        print(f'WARNING: trailing bytes after ETI message: size(payload)={len(bs)} vs. size(msg)={m.MessageHeader.BodyLen}')


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
                payload = udp.data
                dump_eobi(payload, args.love)
            elif isinstance(tp, dpkt.tcp.TCP):
                tcp     = tp
                payload = tcp.data
                dump_eti(payload)


if __name__ == '__main__':
    sys.exit(main())


