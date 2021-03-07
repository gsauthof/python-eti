

# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

from eti.v9_0 import *

import dataclasses
import pytest


def test_logon():
    x = LogonRequest()
    assert x.MessageHeaderIn.TemplateID == 10000
    assert x.MessageHeaderIn.BodyLen == 280

    x.HeartBtInt = 2300000 # ms
    assert x.DefaultCstmApplVerID == b'9.0'
    x.ApplUsageOrders = ApplUsageOrders.AUTOMATED
    x.ApplUsageQuotes = ApplUsageQuotes.AUTOMATED
    x.OrderRoutingIndicator = OrderRoutingIndicator.NO
    x.ApplicationSystemName = b'myRoboTrader'
    x.ApplicationSystemVersion = b'1.666'
    x.ApplicationSystemVendor = b'ACME Inc.'

    x.PartyIDSessionID = 471142
    x.Password = b'einsfueralles'
    x.RequestHeader.MsgSeqNum = 1
    x.RequestHeader.SenderSubID = 8150815 # not used for logon

    bs = x.pack()

    y = LogonRequest.create_from(bs)
    cs = y.pack()
    y.rstrip()
    assert x == y

    x.RequestHeader.MsgSeqNum = 2
    assert x != y

    x.RequestHeader.MsgSeqNum = 1
    x.MessageHeaderIn.BodyLen = 100
    assert x != y

    assert bs == cs


def test_login():
    x = UserLoginRequest()
    assert x.MessageHeaderIn.TemplateID == 10018
    assert x.MessageHeaderIn.BodyLen == 64
    assert x.RequestHeader.SenderSubID == 0xffffffff # -> no-value, not used for login
    x.RequestHeader.MsgSeqNum = 2
    x.Username = 23
    x.Password = b'P4s7w0rd'

    bs = x.pack()

    y = UserLoginRequest.create_from(bs)
    cs = y.pack()
    y.rstrip()

    assert x == y

    x.Username = 24

    assert x != y

    assert bs == cs


def test_order():
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

    x.RequestHeader.MsgSeqNum = 3
    x.Side = Side.BUY
    x.OrderQty = 42 * 10**4
    x.SimpleSecurityID = 23
    x.Price = 404 * 10**8
    x.ClOrdID = 666


    bs = x.pack()

    y = NewOrderSingleShortRequest.create_from(bs)
    cs = y.pack()
    y.rstrip()

    assert x == y

    assert bs == cs


def test_unk_att_fails():
    x = NewOrderSingleShortRequest()
    with pytest.raises(AttributeError):
        x.ExecutingTrada = 1337

def test_unpack_factory():
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

    x.RequestHeader.MsgSeqNum = 3
    x.Side = Side.BUY
    x.OrderQty = 42 * 10**4
    x.SimpleSecurityID = 23
    x.Price = 404 * 10**8
    x.ClOrdID = 666


    bs = x.pack()


    y = unpack_from(bs)
    y.rstrip()

    assert x == y

