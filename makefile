
url_eti_10_0 = https://www.eurex.com/resource/blob/2762272/9bcab8822ab884633cc0bbbeeec8b69b/data/T7_R.10.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.1.zip
url_eti_9_1 = https://www.eurex.com/resource/blob/2609690/62b03a26ce2075635b329e6c688d69b9/data/T7_R.9.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.1.zip
url_eti_9_0 = https://www.xetra.com/resource/blob/2339516/fb5884fb098c442a4bf7cc8c57912ca7/data/T7_R.9.0_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip
url_eti_8_1 = https://www.eurex.com/resource/blob/1896940/e00bfe40dc3ceed5e99e3bfd9a47af54/data/T7_R.8.1_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts_v.1.2.zip
url_eti_8_0 = https://www.eurex.com/resource/blob/1614576/6734877da8532f0e3859c8681c42f5e9/data/T7_Enhanced_Trading_Interface_-_XSD_XML_representation_and_layouts.zip

url_eobi_10_0 = https://www.eurex.com/resource/blob/2762306/01c8058a2fbabd3a13891e7e53e3886b/data/T7_EOBI_XML_Representation_v.10.0.0-1-.zip
url_eobi_9_1 = https://www.eurex.com/resource/blob/2612882/6e784f79cac7928d39d7dbcf831cc14e/data/T7_EOBI_XML_Representation_v.9.1.1.zip
url_eobi_9_0 = https://www.xetra.com/resource/blob/2221290/00792edace1aaa799a42c67a7638efbf/data/T7_EOBI_XML_Representation_v.9.0.1.zip
url_eobi_8_1 = https://www.eurex.com/resource/blob/2128192/2209fe1a6f0a78a27baf6411698690b0/data/T7_EOBI_XML_Representation_v.8.1.1.zip
url_eobi_8_0 = https://www.eurex.com/resource/blob/1741872/baeb2d87c8cc518f2ff2738a74356548/data/T7_EOBI_XML_Representation_v.8.0.3.zip

eti_versions = 10_0 9_1 9_0 8_1 8_0

eobi_versions = 10_0 9_1 9_0 8_1 8_0


all: all-eti


define download_template =

work/T7_$(1)_$(3).zip:
	mkdir -p work
	curl -o $$@ $$(url_$(2)_$(3))

endef
$(foreach p,$(eti_versions),$(eval $(call download_template,ETI,eti,$(p))))
$(foreach p,$(eobi_versions),$(eval $(call download_template,EOBI,eobi,$(p))))


.PHONY: download
download: $(foreach p,$(eti_versions),work/T7_ETI_$(p).zip) $(foreach p,$(eti_versions),work/T7_EOBI_$(p).zip)

.PHONY: all-eti
all-eti: $(foreach p,$(eti_versions),eti/v$(p).py)

.PHONY: all-xti
all-xti: $(foreach p,$(eti_versions),xti/v$(p).py)

.PHONY: all-eobi
all-eobi: $(foreach p,$(eti_versions),eobi/v$(p).py)


define ETI_template =

temp/T7_ETI_$(1)/eti_Derivatives.xml temp/T7_ETI_$(1)/eti_Cash.xml: work/T7_ETI_$(1).zip
	mkdir -p temp/$$(eti_$(1))
	unzip -DD -o work/T7_ETI_$(1).zip -d temp/T7_ETI_$(1)

TEMP += temp/T7_ETI_$(1)

eti/v$(1).py: temp/T7_ETI_$(1)/eti_Derivatives.xml eti2py.py
	mkdir -p eti
	./eti2py.py $$^ > $$@

TEMP += eti/v$(1).py

xti/v$(1).py: temp/T7_ETI_$(1)/eti_Cash.xml eti2py.py
	mkdir -p xti
	./eti2py.py $$^ > $$@

TEMP += xti/v$(1).py

endef

$(foreach p,$(eti_versions),$(eval $(call ETI_template,$(p))))


define EOBI_template =

temp/T7_EOBI_$(1)/eobi.xml: work/T7_EOBI_$(1).zip
	mkdir -p temp/T7_EOBI_$(1)
	unzip -DD -o work/T7_EOBI_$(1).zip -d temp/T7_EOBI_$(1)
	if [ -f temp/T7_EOBI_$(1)/eobi/eobi.xml ]; then mv temp/T7_EOBI_$(1)/eobi/eobi.xml temp/T7_EOBI_$(1)/eobi.xml; fi

TEMP += temp/T7_EOBI_$(1)

eobi/v$(1).py: temp/T7_EOBI_$(1)/eobi.xml eti2py.py
	mkdir -p eobi
	./eti2py.py $$^ > $$@

TEMP += eobi/v$(1).py

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

