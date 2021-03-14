This repository contains a code-generator that turns a Deutsche
Börse ETI (Enhanced Trading Interface) protocol description into
Python bindings.

It's a private research project for investigating how binary
serialisation/deserialization code can profit from modern Python
features.

It also support EOBI (market data) protocol descriptions.

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


## Example

As an example for how the generated code looks you can check out
the [output][ex] for the T7 ETI version 9 specification.


## Protocol Descriptions

Deutsche Börse publishes the ETI protocol descriptions on their
web sites. Since they are sometimes kind of hard to find I include
some links:

- [ETI
  9.0](https://www.xetra.com/resource/blob/2339516/fb5884fb098c442a4bf7cc8c57912ca7/data/T7_R.9.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release9/Release-9.0-1698786?frag=1698808) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-releases/T7-Releases-2438492?frag=2438494)
- [ETI
  8.1](https://www.eurex.com/resource/blob/1896940/e00bfe40dc3ceed5e99e3bfd9a47af54/data/T7_R.8.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release81/Release-8.1-1698746?frag=1698768)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release81/Release-8.1-1698368?frag=1698376)
- [ETI
  8.0](https://www.eurex.com/resource/blob/1614576/6734877da8532f0e3859c8681c42f5e9/data/T7_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release8/Release-8.0-1449522?frag=1601504)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release8/Release-8.0-1546104?frag=1546112)

EOBI descriptions:

- [EOBI
  9.0](https://www.xetra.com/resource/blob/2221290/00792edace1aaa799a42c67a7638efbf/data/T7_EOBI_XML_Representation_v.9.0.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release9/Release-9.0-1698786?frag=1698808) or via [Eurex system documentation](https://www.eurex.com/ex-en/support/initiatives/t7-releases/T7-Releases-2438492?frag=2438494)
- [ETI
  8.1](https://www.eurex.com/resource/blob/2128192/2209fe1a6f0a78a27baf6411698690b0/data/T7_EOBI_XML_Representation_v.8.1.1.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release81/Release-8.1-1698746?frag=1698768)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release81/Release-8.1-1698368?frag=1698376)
- [ETI
  8.0](https://www.eurex.com/resource/blob/1741872/baeb2d87c8cc518f2ff2738a74356548/data/T7_EOBI_XML_Representation_v.8.0.3.zip)
  via [Xetra system
  documentation](https://www.xetra.com/xetra-en/technology/t7/system-documentation/release8/Release-8.0-1449522?frag=1601504)
  or via [Eurex system
  documentation](https://www.eurex.com/ex-en/support/initiatives/archive/release8/Release-8.0-1546104?frag=1546112)

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
----------------------------------------------- benchmark: 1 tests -----------------------------------------------
Name (time in us)        Min       Max    Mean  StdDev  Median     IQR  Outliers  OPS (Kops/s)  Rounds  Iterations
------------------------------------------------------------------------------------------------------------------
test_order            4.2220  169.4589  4.7557  2.3963  4.5809  0.0880  345;3299      210.2732   20337           1
------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```

That means on that machine the code serializes ~ 200 k IOC orders
per seconds which is quite ok.


## See also

The benchmark test case relies on [pytest benchmark][pybench]
(Fedora package: python3-pytest-benchmark).

[enum]: https://docs.python.org/3/library/enum.html
[dc]: https://docs.python.org/3/library/dataclasses.html
[dcold]: https://pypi.org/project/dataclasses/
[struct]: https://docs.python.org/3/library/struct.html
[mv]: https://docs.python.org/3/library/stdtypes.html#memoryview
[pybench]: https://pytest-benchmark.readthedocs.io
[ex]: https://georg.so/pub/v9_0.py
