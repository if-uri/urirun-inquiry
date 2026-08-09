PYTHON ?= python3

.PHONY: doctor-setup doctor-build doctor-test doctor-health

doctor-setup:
	$(PYTHON) -m pip install -e . pytest

doctor-build:
	$(PYTHON) -m compileall -q urirun_inquiry tests

doctor-test:
	$(PYTHON) -m pytest -q

doctor-health:
	$(PYTHON) -m urirun_inquiry.cli --help >/dev/null
