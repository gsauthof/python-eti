

# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

from eti.v9_0 import *


def modify_ioc(x, bs):
    x.RequestHeader.MsgSeqNum += 1
    x.OrderQty = (x.OrderQty + 1) % (2**64 - 1)
    x.Price = (x.Price + 1) % (2**63 - 1)
    x.ClOrdID = (x.ClOrdID + 1) % (2**64 - 1)
    return x.pack_into(bs)

def test_pack_ioc(benchmark):
    x = NewOrderSingleShortRequest()
    x.ExecutingTrader = 1337
    x.EnrichmentRuleID = 1
    x.ApplSeqIndicator = ApplSeqIndicator.NO_RECOVERY_REQUIRED
    x.PriceValidityCheckType = PriceValidityCheckType.NONE
    x.ValueCheckTypeValue = ValueCheckTypeValue.DO_NOT_CHECK
    x.OrderAttributeLiquidityProvision = OrderAttributeLiquidityProvision.N
    x.TimeInForce = TimeInForce.IOC
    x.ExecInst = ExecInst.Q # non-persistant order
    x.TradingCapacity = TradingCapacity.MARKET_MAKER
    x.PartyIdInvestmentDecisionMakerQualifier = PartyIdInvestmentDecisionMakerQualifier.ALGO
    x.ExecutingTraderQualifier = ExecutingTraderQualifier.ALGO

    x.Side = Side.BUY
    x.SimpleSecurityID = 23

    x.RequestHeader.MsgSeqNum = 3
    x.OrderQty = 42 * 10**4
    x.Price = 404 * 10**8
    x.ClOrdID = 666

    bs = bytearray(96)

    n = benchmark(modify_ioc, x, bs)
    assert n == 96

def unpack_ioc(bs, x):
    x.unpack_from(bs)
    return x


def test_unpack_ioc(benchmark):
    x = NewOrderSingleShortRequest()
    x.ExecutingTrader = 1337
    x.EnrichmentRuleID = 1
    x.ApplSeqIndicator = ApplSeqIndicator.NO_RECOVERY_REQUIRED
    x.PriceValidityCheckType = PriceValidityCheckType.NONE
    x.ValueCheckTypeValue = ValueCheckTypeValue.DO_NOT_CHECK
    x.OrderAttributeLiquidityProvision = OrderAttributeLiquidityProvision.N
    x.TimeInForce = TimeInForce.IOC
    x.ExecInst = ExecInst.Q # non-persistant order
    x.TradingCapacity = TradingCapacity.MARKET_MAKER
    x.PartyIdInvestmentDecisionMakerQualifier = PartyIdInvestmentDecisionMakerQualifier.ALGO
    x.ExecutingTraderQualifier = ExecutingTraderQualifier.ALGO

    x.Side = Side.BUY
    x.SimpleSecurityID = 23

    x.RequestHeader.MsgSeqNum = 3
    x.OrderQty = 42 * 10**4
    x.Price = 404 * 10**8
    x.ClOrdID = 666

    bs = bytearray(96)
    x.pack_into(bs)

    y = NewOrderSingleShortRequest()
    y = benchmark(unpack_ioc, bs, y)
    y.rstrip()
    assert y == x
