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

import eti.v9_1 as eti
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

def mk_exec_report(bs):
    m = eti.OrderExecReportBroadcast()
    m.RBCHeaderME.PartitionID = 23
    m.ClOrdID = 1337
    m.ExecID = 1633861270328920429
    m.NoLegExecs = 3
    m.NoFills = 1
    m.NoLegs = 2
    c = eti.LegOrdGrpComp()
    c.LegPositionEffect = eti.LegPositionEffect.OPEN
    m.LegOrdGrp.append(c)
    c = eti.LegOrdGrpComp()
    c.LegPositionEffect = eti.LegPositionEffect.CLOSE
    m.LegOrdGrp.append(c)
    m.FillsGrp.append(eti.FillsGrpComp())
    m.InstrmntLegExecGrp.append(eti.InstrmntLegExecGrpComp())
    c = eti.InstrmntLegExecGrpComp()
    c.LegSide = eti.LegSide.BUY
    m.InstrmntLegExecGrp.append(c)
    m.InstrmntLegExecGrp.append(eti.InstrmntLegExecGrpComp())
    m.update_length()
    n = m.pack_into(bs)
    return memoryview(bs)[:n]

def mk_heartbeat(bs):
    ph = eobi.PacketHeader()
    ph.ApplSeqNum = 4712
    ph.MarketSegmentID = 1337
    ph.PartitionID = 7
    ph.CompletionIndicator = eobi.CompletionIndicator.COMPLETE
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
    ph.DSCP = 0x3c >> 2 # exclude ECN field
    ph.TransactTime = 1633864284123456789
    n = ph.pack_into(bs)
    m = eobi.ExecutionSummary()
    m.SecurityID = 23 # instrument id
    m.ExecID = 1633864284123000789
    m.LastQty = 400123
    m.AggressorSide = eobi.AggressorSide.BUY
    m.LastPx = 9902422
    n = m.pack_into(bs, n)
    return memoryview(bs[:n])
    
def dump(u):
    print(f'000000 {u.hex(sep=" ", bytes_per_sep=1)}\n')

def gen_eti():
    buf = bytearray(1024)
    u = mk_reject('Invalid login credentials!', 23, buf)
    dump(u)
    u = mk_summary(buf)
    dump(u)

def gen_eobi():
    buf = bytearray(1024)
    u = mk_heartbeat(buf)
    dump(u)
    u = mk_summary(buf)
    dump(u)

def main():
    gen_eti()
    gen_eobi()

if __name__ == '__main__':
    sys.exit(main())
