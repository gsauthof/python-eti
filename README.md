This repository contains a code-generator that turns a Deutsche
Börse ETI (Enhanced Trading Interface) protocol description into
Python bindings.
It supports EOBI (market data) protocol descriptions, as
well.

There is also a code generator for creating Wireshark protocol
dissector from these protocol descriptions.

This is a private research project for investigating how binary
serialisation/deserialization code can profit from modern Python
features and other experiments.


2021, Georg Sauthoff <mail@gms.tf>


## Use Cases

The generated Python code can be used for several
purposes, such as:

- creating binary message templates for traffic generators or
  high performance ETI clients
- analysing captured ETI messages for - say - debugging
- a concise reference to look up message details such as the
  name, offset, width, type, etc. of fields
- writing a ETI traffic generator or test-server in Python


## Examples

As an example for how the generated code looks you can check out
the [output][ex] for the T7 ETI version 9 specification.

This repository also contains a simple ETI-Client
(`eti_client.py`) and a small ETI-Server (`eti_server.py`) that
can be used to ping pong some ETI messages over the network. The
server runs forever and replies to each request with some context
dependent response message or messages (as specified in the
protocol specification). If alternative response types are
possible, a choice is made by random. Since the server dumps each
received ETI message to stdout it can also be used as ad-hoc
protocol dissector when developing/testing an ETI client.

There is also a simple EOBI-Client (`eobi_client.py`) that dumps
multicast market data packets, including the [DSCP][dscp] field in
which the EOBI protocol encodes market data related information, as well.

Another example is `pcapdump.py`, a simple PCAP to ETI/EOBI
dumper. It pretty-prints EOBI/ETI packets from a PCAP file to
stdout in a human-readable format. Note that for simplicity it
assumes that ETI-TCP-packets just contain complete ETI messages
and start with an ETI message header which is usually the case, in
practice. Of course, since it's ETI over TCP and TCP is a stream
oriented protocol it's perfectly fine for a client to span
ETI-messages over TCP segment boundaries. Adding TCP reassembly
to the example can be seen as an exercise.

The `pcapgen.py` script shows how to quickly generate/fake some
ETI/EOBI PCAP files from scratch for testing purposes.

## Protocol Descriptions

Deutsche Börse publishes the ETI protocol descriptions on their
web sites. Since they are sometimes kind of hard to find I include
some links:

- [ETI 10](https://www.eurex.com/resource/blob/2827374/da41cfed961c5635fd438d848af30a43/data/T7_R.10.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip)
  via [Xetra system documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release10-0/Release-10.0-2692700?frag=2692722) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-10-0)
- [ETI
  9.1](https://www.eurex.com/resource/blob/2609690/62b03a26ce2075635b329e6c688d69b9/data/T7_R.9.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release91/Release-9.1-2425830?frag=2425852) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-9-1)
- [ETI
  9.0](https://www.xetra.com/resource/blob/2339516/fb5884fb098c442a4bf7cc8c57912ca7/data/T7_R.9.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release9/Release-9.0-1698786?frag=1698808) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-9-0)
- [ETI
  8.1](https://www.eurex.com/resource/blob/1896940/e00bfe40dc3ceed5e99e3bfd9a47af54/data/T7_R.8.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release81/Release-8.1-1698746?frag=1698768)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-8-1)
- [ETI
  8.0](https://www.eurex.com/resource/blob/1614576/6734877da8532f0e3859c8681c42f5e9/data/T7_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release8/Release-8.0-1449522?frag=1601504)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release8)

EOBI descriptions:

- [EOBI 10](https://www.eurex.com/resource/blob/2827418/d9c79556c0aea9bfc9db8b7ef262fe4b/data/T7_EOBI_XML_Representation_v.10.0.1.zip)
  via [Xetra system documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release10-0/Release-10.0-2692700?frag=2692720) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-10-0)
- [EOBI
  9.1](https://www.eurex.com/resource/blob/2612882/6e784f79cac7928d39d7dbcf831cc14e/data/T7_EOBI_XML_Representation_v.9.1.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release91/Release-9.1-2425830?frag=2425850) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-9-1)
- [EOBI
  9.0](https://www.xetra.com/resource/blob/2221290/00792edace1aaa799a42c67a7638efbf/data/T7_EOBI_XML_Representation_v.9.0.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release9/Release-9.0-1698786?frag=1698808) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-9-0)
- [ETI
  8.1](https://www.eurex.com/resource/blob/2128192/2209fe1a6f0a78a27baf6411698690b0/data/T7_EOBI_XML_Representation_v.8.1.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release81/Release-8.1-1698746?frag=1698768)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/t7-release-8-1)
- [ETI
  8.0](https://www.eurex.com/resource/blob/1741872/baeb2d87c8cc518f2ff2738a74356548/data/T7_EOBI_XML_Representation_v.8.0.3.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release8/Release-8.0-1449522?frag=1601504)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release8)

## Related Documentation

The previous section contains links into the Euex/Xetra system
documentation which includes manuals and reference manuals on the
various protocols and services.

Besides the protocols there is also the N7 Network Access Guide
which lists the various ports and IP addresses in use for these
protocols:

- [Xetra Release 10 Network Access Section](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release10-0/Release-10.0-2692700?frag=2692724)
- Direct link: [N7 Network Access-Guide v2.1 Release 10 (Xetra)](https://www.xetra.com/resource/blob/2811582/bf5796497fac47ad74a285682482eb2d/data/N7-Network-Access-Guide-v2.1.pdf)
- Direct link: [N7 Network Access-Guide v2.1 Release 10 (Eurex)](https://www.eurex.com/resource/blob/2811582/bf5796497fac47ad74a285682482eb2d/data/N7-Network-Access-Guide-v2.1.pdf)

The functional reference gives some background on how the
exchange system (the order matching etc.) is supposed to work:

- [Xetra Release 10 Overview and Functionality Section](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release10-0/Release-10.0-2692700?frag=2692698)
- Direct link: [T7 Functional Reference v10.0.4 Release 10 (Xetra)](https://www.xetra.com/resource/blob/2826274/8ef045968590b5dfc76791c5db9f3ad5/data/T7_Release_10.0_-_Functional_Reference_v.10.0.4.pdf)
- Direct link: [T7 Functional Reference v10.0.4 Release 10 (Eurex)](https://www.xetra.com/resource/blob/2826274/8ef045968590b5dfc76791c5db9f3ad5/data/T7_Release_10.0_-_Functional_Reference_v.10.0.4.pdf)


## Python Notes

The main noteworthy modern Python features the generated code uses are [Python
enumerations][enum] (available since Python 3.4) and [dataclasses][dc]
(available since Python 3.7, for Python 3.6 there is a [backport][dcold]).

Dataclasses provide some syntactic sugar for dealing with mutable
named records in Python. Their use of type annotations and
default values allow for compact definitions. Two things to keep
in mind with dataclasses are that default value definitions must
be immutable and that additional (non-annotated) fields can
accidentally added my typos. Thus, the generated code uses
default factory functions for mutable defaults and overwrites
`__setattr__()` to check for unknown fields.

The generated code also makes heavy use of [Python's neat
struct][struct] package for serializing and deserializing spans
of elementary fields. This isn't a recent addition to Python,
however, [memoryviews][mv], which are often a useful tool for
avoiding buffer churning were added as late as Python 2.7.


## Performance

Of course, Python trades some runtime speed for syntactic sugar
and usability, and you wouldn't write performance critical code
in Python. Having said that, serializing/deserializing shouldn't
be too slow, either.

The file `bench_eti.py` contains a small benchmark that
repeatedly serializes an IOC (immediate-or-cancel) order after
changing a few fields, while avoiding buffer churning.

On a Skylake i7-6600U Laptop this results in:

```
$ pytest bench_eti.py 
------------------------------------------------------------------------------------- benchmark: 2 tests -------------------------------------------------------------------------------------
Name (time in us)         Min                   Max               Mean             StdDev             Median               IQR            Outliers  OPS (Kops/s)            Rounds  Iterations
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_pack_ioc          4.4320 (1.0)        158.2600 (1.0)       4.9058 (1.0)       2.1368 (1.0)       4.7510 (1.0)      0.1140 (1.0)       403;688      203.8419 (1.0)       18464           1
test_unpack_ioc       20.6270 (4.65)     1,231.7820 (7.78)     23.7020 (4.83)     10.6706 (4.99)     22.3940 (4.71)     2.5851 (22.67)   1063;1534       42.1906 (0.21)      22066           1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```

That means on that machine the code serializes ~ 200 k IOC orders
per seconds (with cpython) which is quite ok.

Using [PyPy][pypy], the numbers are much better (same machine):

```
$ pypy3 -m pytest bench_eti.py
----------------------------------------------------------------------------------------------- benchmark: 2 tests -----------------------------------------------------------------------------------------------
Name (time in ns)            Min                       Max                  Mean                 StdDev                Median                 IQR             Outliers  OPS (Kops/s)            Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_pack_ioc           258.9996 (1.0)        334,982.7357 (1.0)        317.4350 (1.0)       1,081.2319 (1.0)        284.9449 (1.0)       25.3693 (1.0)      323;20639    3,150.2509 (1.0)      191351          19
test_unpack_ioc       3,491.9940 (13.48)    3,202,659.4854 (9.56)     4,626.1754 (14.57)    14,446.8865 (13.36)    3,695.9827 (12.97)    345.4916 (13.62)   1321;18103      216.1613 (0.07)     142817           2
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```

Basically PyPy speeds up the serialization by a factor of 10 and the deserialization by a factor of 5 or so. Note the change in units in the pytest output (from µs to ns).


## Protocol Introduction

The ETI and EOBI protocols specify a message stream, where each
message is tagged and starts with a length field, although most
messages are of fixed size. Most message fields are of fixed
size, those which aren't are prefixed with an accompanying
length field. Integers a encoded in little endian byte order,
each field size is divisible by 8 bits, and the size of each
message is divisible by 8 bytes.

One important difference between the ETI and EOBI encoding is
that whole EOBI messages are of fixed size whereas ETI messages
may vary in size and only their sub-records are of fixed size.
That means that arrays in ETI messages are minimally encoded
(i.e. only the filled elements are put on the wire) while arrays
in EOBI are fully encoded (i.e. trailing empty elements act as
additional padding). Some ETI messages also include string fields
of variable size and those are zero-padded such that the
message size is divisible by 8.

ETI runs over TCPv4 while EOBI is specified on top of UDPv4.

See for example the ETI request header:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Body Length                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Template ID          |                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
|                  Network Message ID (unused)                  |
+                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |              pad              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Message Sequence Number                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Sender Sub ID                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

And the EOBI Packet-Header:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Body Length          |          Template ID          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                Message Sequence Number (unused)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Application Sequence Number                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Market Segment ID                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Partition ID | CompletionInd.|ApplSeqRestInd.|   DSCP copy   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              pad                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                         Transact Time                         +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```


## Wireshark Protocol Dissectors

The tool `./eti2wireshark.py` generates Wireshark protocol
dissectors from the ETI/EOBI protocol descriptions.

Example:

    ./eti2wireshark.py --proto eobi --desc 'Enhanced Order Book Interface' temp/T7_EOBI_9.1.zip/eobi-mod.xml -o packet-eobi.c
    ./eti2wireshark.py temp/T7_ETI_9.1.zip/eti_Derivatives.xml -o packet-eti.c

The generated code is implemented around a tight state machine to
avoid [code bloat](https://en.wikipedia.org/wiki/Code_bloat).

Protocol fields are pretty-printed in the obvious ways, e.g.
timestamps in human readable format, fixed point decimals with
the point inserted at the type specific place, enumeration
mappings provided etc.

**Related work:**

- [Open-Markets-Initiative/wireshark-lua](https://github.com/Open-Markets-Initiative/wireshark-lua) - A collection of Lua based model-generated Wireshark dissectors for various trading/market data protocols. The ETI/EOBI protocols are listed there as untested. I haven't tested these dissectors - however, the fact that they use another layer of general indirection (the Lua interpreter) surely doesn't help with dissecting speed.<br/>
The generated ETI 9.1 Lua dissector file contains over 32
thousand lines whereas the `eti2wireshark.py` generated ETI 9.1
dissector C-code just spans about 13 thousand lines - where most
of the lines are lookup tables that are placed into the read-only
data segment (i.e. more than 12 thousand lines).<br/>
FWIW, in contrast to the eti2wireshark dissectors, the Lua dissectors
pretty-print field names with spaces between the camel-cased
elements.<br/>
A real limitation is that timestamp fields such as `ExecID` are displayed as is, i.e. the
value isn't converted into a human readable date-time string.<br/>
A serious issue is how the Lua dissectors display
fixed-point decimals: the Lua code uses floating-point arithmetic to
convert them and the resulting floating-point value is
displayed. Thus, the displayed value is just an approximation
of the real value.<br/>
From the repository's description and README it isn't clear
where the Lua dissector generators are available and whether they
are avaiable under an Open Source license.
- [dharmangbhavsar/eti_dissector (removed)](https://web.archive.org/web/20201228095555/https://github.com/dharmangbhavsar/eti_dissector) - 'A Eurex ETI Wireshark Dissector for Geneva Trading' was available until mid 2021 or so but that repository was removed later that year. From the archived page its unclear whether that dissector was released under an open source license. The last commit was from December, 2018 and it looks like it supported ETI version 6.1. Since the repository listing includes Deutsche Börse's published C header file (with structs for all the ETI PDUs) and no XML protocol description it looks like that dissectors wasn't code generated.

## See also

- The benchmark test case relies on [pytest benchmark][pybench]
(Fedora package: python3-pytest-benchmark).
- The `pcapdump.py` example uses the [dpkt][dpkt] package for
parsing PCAP files and skipping over Ethernet/IP/UDP/TCP headers
(Fedora package: python3-dpkt).
- Wikipedia's [List of Electronic Trading Protocols][wptp]

[enum]: https://docs.python.org/3/library/enum.html
[dc]: https://docs.python.org/3/library/dataclasses.html
[dcold]: https://pypi.org/project/dataclasses/
[struct]: https://docs.python.org/3/library/struct.html
[mv]: https://docs.python.org/3/library/stdtypes.html#memoryview
[pybench]: https://pytest-benchmark.readthedocs.io
[ex]: https://georg.so/pub/v9_0.py
[dscp]: https://en.wikipedia.org/wiki/Differentiated_services
[pypy]: http://pypy.org/
[dpkt]: https://github.com/kbandla/dpkt
[wptp]: https://en.wikipedia.org/wiki/List_of_electronic_trading_protocols

