#!/usr/bin/env python3

# Generate dummy ETI/EOBI PCAP files
#
# Examples:
#
# ETI:
#
#     ./pcapgen.py | text2pcap -T 1337,19043 -4 192.168.0.23,192.168.0.60 - foo.pcap
#
# EOBI:
#
#     ./pcapgen.py | text2pcap -u 1337,59001 -4 192.168.0.23,192.168.0.60 - bar.pcap
#
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

import eti.v9_1 as eti
import xti.v9_1 as xti
import eobi.v9_1 as eobi
import sys

def mk_reject(text, seq, bs):
    m = eti.Reject()
    m.NRResponseHeaderME.MsgSeqNum = seq
    m.SessionRejectReason = eti.SessionRejectReason.OTHER
    m.VarText = text.encode()
    m.VarTextLen = len(m.VarText)
    m.update_length()
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_unaligned(text, seq, bs):
    m = eti.Reject()
    m.NRResponseHeaderME.MsgSeqNum = seq
    m.SessionRejectReason = eti.SessionRejectReason.PRICE_NOT_REASONABLE
    m.VarText = text.encode()
    m.VarTextLen = len(m.VarText)
    m.MessageHeaderOut.BodyLen += m.VarTextLen
    n = m.pack_into(bs)
    return memoryview(bs)[:m.MessageHeaderOut.BodyLen]

def mk_exec_report(bs):
    m = eti.OrderExecReportBroadcast()
    m.RBCHeaderME.PartitionID = 23
    m.OrderID = 815
    m.ClOrdID = 1337
    # m.SecurityID unset although required
    m.ExecID = 1633861270328920429
    m.LeavesQty = 7
    m.CumQty = 8
    m.CxlQty = 9
    m.OrderQty = 10
    m.MarketSegmentID = 36
    m.NoLegExecs = 3
    m.NoFills = 1
    m.NoLegs = 2
    c = eti.LegOrdGrpComp()
    c.LegPositionEffect = eti.LegPositionEffect.OPEN
    m.LegOrdGrp.append(c)
    c = eti.LegOrdGrpComp()
    c.LegPositionEffect = eti.LegPositionEffect.CLOSE
    m.LegOrdGrp.append(c)
    c = eti.FillsGrpComp()
    c.FillExecID = 666
    m.FillsGrp.append(c)
    m.InstrmntLegExecGrp.append(eti.InstrmntLegExecGrpComp())
    c = eti.InstrmntLegExecGrpComp()
    c.LegSide = eti.LegSide.BUY
    c.LegLastQty = 1234
    m.InstrmntLegExecGrp.append(c)
    m.InstrmntLegExecGrp.append(eti.InstrmntLegExecGrpComp())
    m.update_length()
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_xti_mod_order(bs):
    # i.e. malformed when parsing as Derivatives-ETI
    m = xti.ModifyOrderSingleRequest()
    m.FreeText1 = b'cash rules'
    m.FreeText2 = b'everything'
    m.FreeText4 = b'around'
    m.FIXClOrdID = b'me'
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_mod_order(bs, freetext1):
    m = eti.ModifyOrderSingleRequest()
    m.RequestHeader.MsgSeqNum = 5
    m.RequestHeader.SenderSubID = 2323
    m.OrderQty = 99000
    m.MarketSegmentID = 8989
    m.SimpleSecurityID = 232
    m.FreeText1 = freetext1.encode()
    m.FreeText3 = b'\0lol'
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_logon(bs):
    m = eti.LogonRequest()
    m.RequestHeader.MsgSeqNum = 1
    m.PartyIDSessionID = 2323
    m.Password = b'geheim23'
    m.ApplicationSystemName = b'skynet'
    m.ApplicationSystemVersion = b'1.2.3'
    m.ApplicationSystemVendor = b'ACME'
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_login(bs):
    m = eti.UserLoginRequest()
    m.RequestHeader.MsgSeqNum = 2
    m.Username = 1337
    m.Password = b'besttrader'
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_invalid_template(bs, tid):
    m = eti.UserLoginRequest()
    m.MessageHeaderIn.TemplateID = tid
    m.RequestHeader.MsgSeqNum = 2
    m.Username = 1234
    m.Password = b'geheim'
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_invalid_enum(bs):
    m = eti.DeleteAllOrderRequest()
    m.RequestHeader.SenderSubID = 88888
    m.SecurityID = 815
    m.Side = 23 # NB: Invalid enumeration value!
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

# i.e. check the message whose usage information in the usages
# array comes last in eti2wireshark generated code
def mk_user_logout_response(bs):
    m = eti.UserLogoutResponse()
    m.ResponseHeader.RequestTime = 1637015805000000000
    m.ResponseHeader.SendingTime = 1637015806000000000
    m.ResponseHeader.MsgSeqNum = 711
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_heartbeat(bs):
    ph = eobi.PacketHeader()
    ph.ApplSeqNum = 4712
    ph.MarketSegmentID = 1337
    ph.PartitionID = 7
    ph.CompletionIndicator = eobi.CompletionIndicator.COMPLETE
    ph.DSCP = 0
    ph.TransactTime = 1633864284123456789
    n = ph.pack_into(bs)
    m = eobi.Heartbeat()
    m.LastMsgSeqNumProcessed = 4711
    n = m.pack_into(bs, n)
    return memoryview(bs[:n])

def mk_summary(bs):
    ph = eobi.PacketHeader()
    ph.ApplSeqNum = 4713
    ph.MarketSegmentID = 1337 # product id
    ph.PartitionID = 7
    ph.CompletionIndicator = eobi.CompletionIndicator.COMPLETE
    ph.DSCP = 0x3c # exclude ECN field
    ph.TransactTime = 1633864284123456789
    n = ph.pack_into(bs)
    m = eobi.ExecutionSummary()
    m.MessageHeader.MsgSeqNum = 23
    m.SecurityID = 23 # instrument id
    m.ExecID = 1633864284123000789
    m.LastQty = 400123
    m.AggressorSide = eobi.AggressorSide.BUY
    m.LastPx = 9902422
    # NB: m.RestingCxlQty unset although it's required
    n = m.pack_into(bs, n)
    return memoryview(bs[:n])

def mk_empty_inssum(bs):
    ph = eobi.PacketHeader()
    ph.ApplSeqNum = 4713
    ph.MarketSegmentID = 1337 # product id
    ph.PartitionID = 7
    ph.CompletionIndicator = eobi.CompletionIndicator.COMPLETE
    ph.DSCP = 0x4c
    ph.TransactTime = 1633864284123480230
    n = ph.pack_into(bs)
    m = eobi.InstrumentSummary()
    m.MessageHeader.MsgSeqNum = 4711
    m.SecurityID = 42 # instrument id
    m.SoldOutIndicator = eobi.SoldOutIndicator.SOLDOUT
    assert m.NoMDEntries == 0
    # NB: in contrast to ETI, EOBI messages with variable-length arrays are
    # never shortened
    m.MessageHeader.BodyLen = m.sizes[1]
    m.pack_into(bs, n)
    n += m.sizes[1]

    m.NoMDEntries = 0xff # NO_VALUE
    m.MarketCondition = eobi.MarketCondition.STRESSED
    m.pack_into(bs, n)
    n += m.sizes[1]
    return memoryview(bs[:n])

def mk_counter_overflow(bs):
    bs.__init__(1024)
    ph = eobi.PacketHeader()
    ph.ApplSeqNum = 4714
    ph.MarketSegmentID = 1337 # product id
    ph.PartitionID = 7
    ph.CompletionIndicator = eobi.CompletionIndicator.COMPLETE
    ph.DSCP = 0x5c
    ph.TransactTime = 1633864284123480238
    n = ph.pack_into(bs)
    m = eobi.MassInstrumentStateChange()
    # NB: m.MessageHeader.MsgSeqNum unset although it's required
    m.SecurityMassTradingStatus = eobi.SecurityMassTradingStatus.INTRADAYAUCTION
    m.NoRelatedSym = 25 # NB: max: 24 => overflow
    m.MessageHeader.BodyLen = m.sizes[1]
    m.pack_into(bs, n)
    n += m.MessageHeader.BodyLen
    return memoryview(bs[:n])
    
def dump(u):
    print(f'000000 {u.hex(sep=" ", bytes_per_sep=1)}\n')

def gen_eti():
    buf = bytearray(1024)
    tail = bytearray(1024)
    u = mk_reject('Invalid login credentials!', 23, buf)
    dump(u)
    u = mk_exec_report(buf)
    dump(u)

    # test tcp packet reassembly
    v = mk_logon(buf)
    w = mk_login(tail)
    dump(v[:123])
    dump(bytearray(v[123:]) + w[:23])
    dump(w[23:])

    u = mk_xti_mod_order(buf)
    dump(u)
    u = mk_mod_order(buf, 'test stray chars')
    dump(u)

    u = mk_invalid_template(buf, 23)
    dump(u)
    u = mk_invalid_template(buf, 10105)
    dump(u)

    u = mk_invalid_enum(buf)
    dump(u)

    u = mk_user_logout_response(buf)
    dump(u)

    u = mk_unaligned('show unaligned', 666, buf)
    dump(u)

def mk_overused(bs):
    ph = eobi.PacketHeader()
    ph.MessageHeader.MsgSeqNum = 0x23
    ph.ApplSeqNum = 4733
    ph.MarketSegmentID = 90211
    ph.PartitionID = 6
    ph.DSCP = 0
    n = ph.pack_into(bs)
    m = eobi.Heartbeat()
    m.LastMsgSeqNumProcessed = 14141
    n = m.pack_into(bs, n)
    return memoryview(bs[:n])

def gen_eobi():
    buf = bytearray(1024)
    u = mk_heartbeat(buf)
    dump(u)
    u = mk_summary(buf)
    dump(u)
    u = mk_counter_overflow(buf)
    dump(u)
    u = mk_empty_inssum(buf)
    dump(u)
    u = mk_overused(buf)
    dump(u)

def parse_args():
    p = argparse.ArgumentParser(description='Generate dummy ETI/EOBI PCAP files')
    p.add_argument('--eobi', action='store_true', help='generate EOBI PCAP instead of ETI')
    args = p.parse_args()
    return args

def main():
    args = parse_args()
    if args.eobi:
        gen_eobi()
    else:
        gen_eti()

if __name__ == '__main__':
    sys.exit(main())
