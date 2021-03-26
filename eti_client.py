#!/usr/bin/env python3


# Dummy ETI demo client
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later


import asyncio
import logging
import struct
import sys

import eti.v9_0 as eti

from dressup import pformat


log = logging.getLogger(__name__)

len_st = struct.Struct('<I')

async def read_everything(stream):
    try:
        while True:
            bs = await stream.readexactly(4)
            n = len_st.unpack(bs)[0]
            log.info(f'next message size: {n}')
            rest = await stream.readexactly(n - 4)
            bs += rest
            m = eti.unpack_from(bs)
            m.rstrip()
            log.info(f'Received: {pformat(m, width=45)}')
    except asyncio.IncompleteReadError:
        log.info('Got EOF on read end')


async def client(host, port):
    rstream, wstream = await asyncio.open_connection(host, port)

    reader = asyncio.create_task(read_everything(rstream))
    # ^ Python 3.7, prior:
    # reader = asyncio.ensure_future(read_everything(rstream))

    bs = bytearray(1024)

    x = eti.LogonRequest()
    x.HeartBtInt = 2300000 # ms
    x.ApplUsageOrders = eti.ApplUsageOrders.AUTOMATED
    x.ApplUsageQuotes = eti.ApplUsageQuotes.AUTOMATED
    x.OrderRoutingIndicator = eti.OrderRoutingIndicator.NO
    x.ApplicationSystemName = b'myRoboTrader'
    x.ApplicationSystemVersion = b'1.666'
    x.ApplicationSystemVendor = b'ACME Inc.'

    x.PartyIDSessionID = 471142
    x.Password = b'einsfueralles'
    x.RequestHeader.MsgSeqNum = 1
    x.RequestHeader.SenderSubID = 8150815 # not used for logon

    n = x.pack_into(bs)

    wstream.write(memoryview(bs)[:n])
    log.info('Sending Logon')
    await wstream.drain()

    x = eti.UserLoginRequest()
    x.RequestHeader.MsgSeqNum = 2
    x.Username = 23
    x.Password = b'P4s7w0rd'
    n = x.pack_into(bs)

    wstream.write(memoryview(bs)[:n])
    log.info('Sending Login')
    await wstream.drain()

    x = eti.NewOrderSingleShortRequest()
    x.ExecutingTrader = 1337
    x.EnrichmentRuleID = 1
    x.ApplSeqIndicator = eti.ApplSeqIndicator.NO_RECOVERY_REQUIRED
    x.PriceValidityCheckType = eti.PriceValidityCheckType.NONE
    x.ValueCheckTypeValue = eti.ValueCheckTypeValue.DO_NOT_CHECK
    x.OrderAttributeLiquidityProvision = eti.OrderAttributeLiquidityProvision.N
    x.TimeInForce = eti.TimeInForce.IOC
    x.ExecInst = eti.ExecInst.Q # non-persistant order
    x.TradingCapacity = eti.TradingCapacity.MARKET_MAKER
    x.PartyIdInvestmentDecisionMakerQualifier = eti.PartyIdInvestmentDecisionMakerQualifier.ALGO
    x.ExecutingTraderQualifier = eti.ExecutingTraderQualifier.ALGO

    x.RequestHeader.MsgSeqNum = 3
    x.Side = eti.Side.BUY
    x.OrderQty = 42 * 10**4
    x.SimpleSecurityID = 23
    x.Price = 404 * 10**8
    x.ClOrdID = 666
    n = x.pack_into(bs)

    wstream.write(memoryview(bs)[:n])
    log.info('Sending IOC')
    await wstream.drain()

    await asyncio.sleep(3)

    wc = wstream.close()
    await wstream.wait_closed()

    await asyncio.wait_for(reader, timeout=None)

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    logging.basicConfig(level=logging.INFO)
    asyncio.run(client(host, port))

if __name__ == '__main__':
    sys.exit(main())


