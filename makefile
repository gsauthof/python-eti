


eti_9_0 = work/T7_ETI_9.0.zip
eti_8_1 = work/T7_ETI_8_1.zip
eti_8_0 = work/T7_ETI_8_0.zip

all: all-eti

work:
	mkdir work


$(eti_9_0): work
	curl -o $@ https://www.xetra.com/resource/blob/2339516/fb5884fb098c442a4bf7cc8c57912ca7/data/T7_R.9.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip
	touch work

$(eti_8_1): work
	curl -o $@ https://www.eurex.com/resource/blob/1896940/e00bfe40dc3ceed5e99e3bfd9a47af54/data/T7_R.8.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip
	touch work

$(eti_8_0): work
	curl -o $@ https://www.eurex.com/resource/blob/1614576/6734877da8532f0e3859c8681c42f5e9/data/T7_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts.zip
	touch work


.PHONY: download
download: $(eti_9_0) $(eti_8_1) $(eti_8_0)


.PHONY: all-eti
all-eti: eti/v9_0.py eti/v8_1.py eti/v8_0.py

temp/$(eti_9_0)/eti_Derivatives.xml: $(eti_9_0)
	mkdir -p temp/$(eti_9_0)
	unzip -u $(eti_9_0) -d temp/$(eti_9_0)
	touch $@

eti/v9_0.py: temp/$(eti_9_0)/eti_Derivatives.xml eti2py.py
	./eti2py.py $^ > $@


temp/$(eti_8_1)/eti_Derivatives.xml: $(eti_8_1)
	mkdir -p temp/$(eti_8_1)
	unzip -u $(eti_8_1) -d temp/$(eti_8_1)
	touch $@

eti/v8_1.py: temp/$(eti_8_1)/eti_Derivatives.xml eti2py.py
	./eti2py.py $^ > $@


temp/$(eti_8_0)/eti_Derivatives.xml: $(eti_8_0)
	mkdir -p temp/$(eti_8_0)
	unzip -u $(eti_8_0) -d temp/$(eti_8_0)
	touch $@

eti/v8_0.py: temp/$(eti_8_0)/eti_Derivatives.xml eti2py.py
	./eti2py.py $^ > $@

.PHONY: check
check:
	python3 -m pytest test_eti.py -v

.PHONY: bench
bench:
	python3 -m pytest bench_eti.py


