SHELL      = /bin/bash
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)
RDIR      := reports
HTML       = --self-contained-html

.PHONY: help \
        demo demo-dummyjson demo-jsonplaceholder demo-retry switch \
        test test-dummyjson test-jsonplaceholder smoke unit integration \
        probe-all lint install report-clean

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Demo  (AI tooling summary → schemas refresh → full suite → timestamped report)"
	@echo "  demo                 full suite against reqres.in"
	@echo "  demo-dummyjson       refresh dummyjson schemas then run full suite"
	@echo "  demo-jsonplaceholder refresh jsonplaceholder schemas then run full suite"
	@echo "  demo-retry           simulate 429 / 5xx → retry log + xfail source suggestion"
	@echo "  switch               interactive recovery — probe chosen source then run suite"
	@echo ""
	@echo "Source schemas  (refresh before switching sources)"
	@echo "  probe-all            regenerate schemas for all three sources"
	@echo ""
	@echo "Run tests  (each writes a timestamped report to reports/)"
	@echo "  test                 full suite → reqres.in"
	@echo "  test-dummyjson       full suite → dummyjson"
	@echo "  test-jsonplaceholder full suite → jsonplaceholder"
	@echo "  smoke                smoke tests only"
	@echo "  unit                 unit tests only  (no network, no report)"
	@echo "  integration          integration tests only  (no report)"
	@echo ""
	@echo "CI / lint"
	@echo "  lint                 validate .github/workflows/qa.yml with actionlint"
	@echo ""
	@echo "Setup & cleanup"
	@echo "  install              pip install -r requirements.txt"
	@echo "  report-clean         remove all reports in reports/"
	@echo ""

# ── Demo ──────────────────────────────────────────────────────────────────────
demo:
	@mkdir -p $(RDIR)
	@python3 scripts/demo_header.py
	@source ~/.zshrc 2>/dev/null; \
	  pytest --html=$(RDIR)/report_reqres_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_reqres_$(TIMESTAMP).html

demo-dummyjson:
	@mkdir -p $(RDIR)
	@echo "--- refreshing schemas for dummyjson ---"
	@TEST_SOURCE=dummyjson python3 scripts/probe.py
	@python3 scripts/demo_header.py
	@TEST_SOURCE=dummyjson pytest \
	  --html=$(RDIR)/report_dummyjson_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_dummyjson_$(TIMESTAMP).html

demo-jsonplaceholder:
	@mkdir -p $(RDIR)
	@echo "--- refreshing schemas for jsonplaceholder ---"
	@TEST_SOURCE=jsonplaceholder python3 scripts/probe.py
	@python3 scripts/demo_header.py
	@TEST_SOURCE=jsonplaceholder pytest \
	  --html=$(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html

demo-retry:
	@echo ""
	@echo "Simulating transient HTTP errors — watch for live WARNING log and xfail suggestion ..."
	@echo ""
	@pytest tests/resilience -v; \
	echo ""; \
	echo "Source unavailable? Run: make switch  — probes the chosen source then runs the full suite."

# ── Source switch (interactive recovery) ─────────────────────────────────────
switch:
	@mkdir -p $(RDIR)
	@echo ""
	@echo "Source unavailable. Choose a replacement:"
	@echo "  1  reqres.in        (requires REQRES_API_KEY)"
	@echo "  2  dummyjson        (no key needed)"
	@echo "  3  jsonplaceholder  (no key needed)"
	@echo ""
	@read -rp "Switch to [1/2/3]: " choice; \
	case "$$choice" in \
	  1) echo ""; \
	     echo "--- refreshing schemas for reqres ---"; \
	     source ~/.zshrc 2>/dev/null; python3 scripts/probe.py; \
	     echo ""; python3 scripts/demo_header.py; \
	     source ~/.zshrc 2>/dev/null; \
	     pytest --html=$(RDIR)/report_reqres_$(TIMESTAMP).html $(HTML); \
	     python3 scripts/print_report_link.py $(RDIR)/report_reqres_$(TIMESTAMP).html ;; \
	  2) echo ""; \
	     echo "--- refreshing schemas for dummyjson ---"; \
	     TEST_SOURCE=dummyjson python3 scripts/probe.py; \
	     echo ""; python3 scripts/demo_header.py; \
	     TEST_SOURCE=dummyjson pytest \
	       --html=$(RDIR)/report_dummyjson_$(TIMESTAMP).html $(HTML); \
	     python3 scripts/print_report_link.py $(RDIR)/report_dummyjson_$(TIMESTAMP).html ;; \
	  3) echo ""; \
	     echo "--- refreshing schemas for jsonplaceholder ---"; \
	     TEST_SOURCE=jsonplaceholder python3 scripts/probe.py; \
	     echo ""; python3 scripts/demo_header.py; \
	     TEST_SOURCE=jsonplaceholder pytest \
	       --html=$(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html $(HTML); \
	     python3 scripts/print_report_link.py $(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html ;; \
	  *) echo "Invalid choice — run 'make switch' again." ;; \
	esac

# ── Source schemas ────────────────────────────────────────────────────────────
probe-all:
	@source ~/.zshrc 2>/dev/null; python3 scripts/probe.py
	TEST_SOURCE=dummyjson python3 scripts/probe.py
	TEST_SOURCE=jsonplaceholder python3 scripts/probe.py

# ── Run tests ─────────────────────────────────────────────────────────────────
test:
	@mkdir -p $(RDIR)
	@pytest --html=$(RDIR)/report_reqres_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_reqres_$(TIMESTAMP).html

test-dummyjson:
	@mkdir -p $(RDIR)
	@TEST_SOURCE=dummyjson pytest \
	  --html=$(RDIR)/report_dummyjson_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_dummyjson_$(TIMESTAMP).html

test-jsonplaceholder:
	@mkdir -p $(RDIR)
	@TEST_SOURCE=jsonplaceholder pytest \
	  --html=$(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_jsonplaceholder_$(TIMESTAMP).html

smoke:
	@mkdir -p $(RDIR)
	@pytest tests/smoke -v \
	  --html=$(RDIR)/report_smoke_$(TIMESTAMP).html $(HTML)
	@python3 scripts/print_report_link.py $(RDIR)/report_smoke_$(TIMESTAMP).html

unit:
	pytest tests/unit -v

integration:
	pytest tests/integration -v

# ── CI / lint ─────────────────────────────────────────────────────────────────
lint:
	actionlint .github/workflows/qa.yml

# ── Setup & cleanup ───────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

report-clean:
	@rm -f $(RDIR)/*.html
	@echo "Removed all reports from $(RDIR)/"
