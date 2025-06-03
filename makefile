.PHONY: usage install serve in_virtual_env venv
VENV = .venv/bin

usage:
	@echo "Make targets: install, serve, venv"

install: 
	$(VENV)/python -m venv .venv
	$(VENV)/pip install -r requirements.txt
	@echo "\n*** Venv installed with: ***"
	@$(VENV)/pip list
	@$(VENV)/python --version

serve: 
	cd sps20 && ../$(VENV)/lektor server -f scss --browse

build: 
	$(VENV)/lektor --project sps20 build -f scss --output-path build

test:
	$(VENV)/lektor --version

# in_virtual_env:
# 	@if python -c 'import sys; (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)) and sys.exit(1) or sys.exit(0)'; then \
# 		echo "Error: An active virtual environment is required"; exit 1; \
# 		else true; fi
