


eti_9_1 = T7_ETI_9.1.zip
eti_9_0 = T7_ETI_9.0.zip
eti_8_1 = T7_ETI_8_1.zip
eti_8_0 = T7_ETI_8_0.zip

eti_versions = 9_1 9_0 8_1 8_0

eobi_9_1 = T7_EOBI_9.1.zip
eobi_9_0 = T7_EOBI_9.0.zip
eobi_8_1 = T7_EOBI_8_1.zip
eobi_8_0 = T7_EOBI_8_0.zip

eobi_versions = 9_1 9_0 8_1 8_0

all: all-eti

work/$(eti_9_1):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/2609690/62b03a26ce2075635b329e6c688d69b9/data/T7_R.9.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.1.zip

work/$(eti_9_0):
	mkdir -p work
	curl -o $@ https://www.xetra.com/resource/blob/2339516/fb5884fb098c442a4bf7cc8c57912ca7/data/T7_R.9.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip

work/$(eti_8_1):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/1896940/e00bfe40dc3ceed5e99e3bfd9a47af54/data/T7_R.8.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip

work/$(eti_8_0):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/1614576/6734877da8532f0e3859c8681c42f5e9/data/T7_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts.zip


work/$(eobi_9_1):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/2612882/6e784f79cac7928d39d7dbcf831cc14e/data/T7_EOBI_XML_Representation_v.9.1.1.zip

work/$(eobi_9_0):
	mkdir -p work
	curl -o $@ https://www.xetra.com/resource/blob/2221290/00792edace1aaa799a42c67a7638efbf/data/T7_EOBI_XML_Representation_v.9.0.1.zip

work/$(eobi_8_1):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/2128192/2209fe1a6f0a78a27baf6411698690b0/data/T7_EOBI_XML_Representation_v.8.1.1.zip

work/$(eobi_8_0):
	mkdir -p work
	curl -o $@ https://www.eurex.com/resource/blob/1741872/baeb2d87c8cc518f2ff2738a74356548/data/T7_EOBI_XML_Representation_v.8.0.3.zip


.PHONY: download
download: work/$(eti_9_0) work/$(eti_8_1) work/$(eti_8_0)


.PHONY: all-eti
all-eti: eti/v9_0.py eti/v8_1.py eti/v8_0.py

.PHONY: all-xti
all-xti: xti/v9_0.py xti/v8_1.py xti/v8_0.py

.PHONY: all-eobi
all-eobi: eobi/v9_0.py eobi/v8_1.py eobi/v8_0.py


define ETI_template =

temp/$$(eti_$(1))/eti_Derivatives.xml temp/$$(eti_$(1))/eti_Cash.xml: work/$$(eti_$(1))
	mkdir -p temp/$$(eti_$(1))
	unzip -DD -o work/$$(eti_$(1)) -d temp/$$(eti_$(1))

TEMP += temp/$$(eti_$(1))

eti/v$(1).py: temp/$$(eti_$(1))/eti_Derivatives.xml eti2py.py
	mkdir -p eti
	./eti2py.py $$^ > $$@

TEMP += eti/v$(1).py

xti/v$(1).py: temp/$$(eti_$(1))/eti_Cash.xml eti2py.py
	mkdir -p xti
	./eti2py.py $$^ > $$@

TEMP += xti/v$(1).py

endef

$(foreach p,$(eti_versions),$(eval $(call ETI_template,$(p))))


define EOBI_template =

temp/$$(eobi_$(1))/eobi.xml: work/$$(eobi_$(1))
	mkdir -p temp/$$(eobi_$(1))
	unzip -DD -o work/$$(eobi_$(1)) -d temp/$$(eobi_$(1))
	if [ -f temp/$$(eobi_$(1))/eobi/eobi.xml ]; then mv temp/$$(eobi_$(1))/eobi/eobi.xml  temp/$$(eobi_$(1))/eobi.xml; fi

TEMP += temp/$$(eobi_$(1))

eobi/v$(1).py: temp/$$(eobi_$(1))/eobi.xml eti2py.py
	mkdir -p eobi
	./eti2py.py $$^ > $$@

endef

$(foreach p,$(eobi_versions),$(eval $(call EOBI_template,$(p))))


.PHONY: check
check: eti/v9_0.py
	python3 -m pytest test_eti.py -v

.PHONY: bench
bench: eti/v9_0.py
	python3 -m pytest bench_eti.py

.PHONY: clean
clean:
	rm -rf $(TEMP)

