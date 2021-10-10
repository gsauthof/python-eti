#!/usr/bin/env python3

# Dummy EOBI demo client
#
#
# Requires at least Python 3.7.
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from enum import IntEnum
import logging
import socket
import struct
import sys

import eobi.v9_1 as eobi

from dressup import pformat


log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description='EOBI example client')
    p.add_argument('address', help='IPv4 address of interface to bind')
    p.add_argument('port', type=int, help='port binding')
    p.add_argument('--group', '-g', help='address of multicast group to join')
    p.add_argument('--love', '-l', action='store_true', help='also dump EOBI heartbeat packets')
    args = p.parse_args()
    return args


def get_ip_recvtos():
    try:
        return socket.IP_RECVTOS
    except AttributeError:
        # at least on Linux it's 13
        return 13


class TLDR(IntEnum):
    EXEC_SUMMARY          = 0x1c
    IMPROVED_SPREAD       = 0x2c
    EXEC_SUMMARY_IMPROVED = 0x3c
    WIDENED_SPREAD        = 0x4c
    EXEC_SUMMARY_WIDENED  = 0x5c

tldr2str_map = {
        TLDR.EXEC_SUMMARY          : 'EXEC_SUMMARY',
        TLDR.IMPROVED_SPREAD       : 'IMPROVED_SPREAD',
        TLDR.EXEC_SUMMARY_IMPROVED : 'EXEC_SUMMARY_IMPROVED',
        TLDR.WIDENED_SPREAD        : 'WIDENED_SPREAD',
        TLDR.EXEC_SUMMARY_WIDENED  : 'EXEC_SUMMARY_WIDENED',
}


def main():
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname).1s   %(message)s')
    args = parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((args.group, args.port))

    s.setsockopt(socket.IPPROTO_IP, get_ip_recvtos(), 1)

    mreq = struct.pack('4s4s', socket.inet_aton(args.group),
            socket.inet_aton(args.address))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    bufs = ( bytearray(1500), )

    while True:
        #bs = s.recv(1500)
        n, msgs, msg_flags, addr = s.recvmsg_into(bufs, 32)
        bs = memoryview(bufs[0])[:n]

        ph = eobi.unpack_from(bs)
        ph.rstrip()
        assert ph.MessageHeader.TemplateID == eobi.TemplateID.PacketHeader

        i    = ph.MessageHeader.BodyLen
        tail = bs
        k    = 0

        while i < n:
            m = eobi.unpack_from(tail[i:])
            m.rstrip()

            if (m.MessageHeader.TemplateID != eobi.TemplateID.Heartbeat
                    or args.love):
                if k == 0:
                    if msgs and msgs[0][2] != b'\0':
                        tos = ord(msgs[0][2])
                        log.info('tl;dr DSCP flag: ' + tldr2str_map[tos])
                    log.info(f'Received ({n} bytes) - PacketHeader: {pformat(ph, width=45)}')
                log.info(f'Message: {pformat(m, width=45)}')

            k += 1
            i += m.MessageHeader.BodyLen


if __name__ == '__main__':
    sys.exit(main())
