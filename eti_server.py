#!/usr/bin/env python3

# Dummy ETI demo server
#
#
# Requires at least Python 3.7.
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import asyncio
import logging
import random
import struct
import sys

import eti.v9_1 as eti

from dressup import pformat


log = logging.getLogger(__name__)

len_st = struct.Struct('<I')


def set_seq_num(m, seq):
    i = iter(m.__annotations__.items())
    next(i)
    zs = next(i)

    header = m.__getattribute__(zs[0])
    try:
        header.__setattr__('MsgSeqNum', seq)
        return seq + 1
    except AttributeError:
        # broadcast messages are out of sequence ...
        return seq

def send_response(wstream, xs, seq, bs):
    if not xs:
        return seq
    T, cond, zs = random.choice(xs)
    if T is not None:
        m = T()
        seq = set_seq_num(m, seq)

        n = m.pack_into(bs)
        log.info(f'Sending Response: {T}')
        wstream.write(memoryview(bs)[:n])

    return send_response(wstream, zs, seq, bs)

def send_reject(wstream, text, seq, bs):
    m = eti.Reject()
    m.NRResponseHeaderME.MsgSeqNum = seq
    m.SessionRejectReason = eti.SessionRejectReason.OTHER
    m.VarText = text.encode()
    m.VarTextLen = len(m.VarText)
    m.update_length()
    n = m.pack_into(bs)
    log.info('Sending Reject')
    wstream.write(memoryview(bs)[:n])
    return seq + 1

async def serve_session(rstream, wstream):
    seq = 1
    buf = bytearray(1024)
    global logon_count
    lc = logon_count
    logon_count += 1
    try:
        while True:
            bs = await rstream.readexactly(4)
            n = len_st.unpack(bs)[0]
            rest = await rstream.readexactly(n - 4)
            bs += rest
            m = eti.unpack_from(bs)
            m.rstrip()
            log.info(f'Received: {pformat(m, width=45)}')

            if lc == reject_nth_logon:
                send_reject(wstream, 'You cannot logon until you have payed your bills!',
                    seq, buf)
                await wstream.drain()
                wstream.close()
                await wstream.wait_closed()
                log.info('rejected session, connection closed')
                return

            xs = eti.request2response[m.MessageHeaderIn.TemplateID]

            seq = send_response(wstream, xs, seq, buf)
            await wstream.drain()

    except asyncio.IncompleteReadError:
        log.info('Got EOF on read end')


async def server(host, port):
    s = await asyncio.start_server(serve_session, host, port)

    async with s:
        await s.serve_forever()

def parse_args():
    p = argparse.ArgumentParser(description='ETI example server')
    p.add_argument('host', help='address to bind to')
    p.add_argument('port', type=int, help='port to listen on')
    p.add_argument('--reject-nth-logon', type=int, help='reject the nth logon (count start at 0)')
    args = p.parse_args()
    return args

def main():
    args = parse_args()
    global reject_nth_logon
    reject_nth_logon = args.reject_nth_logon
    global logon_count
    logon_count = 0
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname).1s   %(message)s')
    asyncio.run(server(args.host, args.port))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log.info('quitting due to SIGINT')
