#!/usr/bin/env python3

# Dummy ETI demo server
#
#
# Requires at least Python 3.7.
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import logging
import random
import struct
import sys

import eti.v9_0 as eti

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


async def serve_session(rstream, wstream):
    seq = 1
    buf = bytearray(1024)
    try:
        while True:
            bs = await rstream.readexactly(4)
            n = len_st.unpack(bs)[0]
            rest = await rstream.readexactly(n - 4)
            bs += rest
            m = eti.unpack_from(bs)
            m.rstrip()
            log.info(f'Received: {pformat(m, width=45)}')

            xs = eti.request2response[m.MessageHeaderIn.TemplateID]

            seq = send_response(wstream, xs, seq, buf)
            await wstream.drain()

    except asyncio.IncompleteReadError:
        log.info('Got EOF on read end')


async def server(host, port):
    s = await asyncio.start_server(serve_session, host, port)

    async with s:
        await s.serve_forever()


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname).1s   %(message)s')
    asyncio.run(server(host, port))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log.info('quitting due to SIGINT')
