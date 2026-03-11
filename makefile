.PHONY: usage install serve in_virtual_env
VENV=.venv
VENV_BIN=$(VENV)/bin

usage:
	@echo "Make targets: install, serve, venv"

install: 
	rm -rf $(VENV)
	python -m venv $(VENV)
	# source $(VENV_BIN)/activate
	$(VENV_BIN)/pip install -r requirements.txt
	@echo "\n*** Venv installed with: ***"
	@$(VENV_BIN)/pip list
	@$(VENV_BIN)/python --version

serve: 
	cd sps20 && ../$(VENV_BIN)/lektor server -f scss --browse

build: 
	$(VENV_BIN)/lektor --project sps20 build -f scss --output-path build

test:
	$(VENV_BIN)/lektor --version

# in_virtual_env:
# 	@if python -c 'import sys; (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)) and sys.exit(1) or sys.exit(0)'; then \
# 		echo "Error: An active virtual environment is required"; exit 1; \
# 		else true; fi
