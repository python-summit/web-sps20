usage:
	@echo "Make targets: install, serve, venv"

install: in_virtual_envma
# install: 
	pip install -r requirements.txt

# venv:
# 	. venv/bin/activate || . .venv/bin/activate

serve: in_virtual_env
# serve: 
	cd sps20 && lektor server -f scss --browse

build: in_virtual_env
# build: 
	cd sps20 && lektor build -f scss --output-path build

in_virtual_env:
	@if python -c 'import sys; (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)) and sys.exit(1) or sys.exit(0)'; then \
		echo "Error: An active virtual environment is required"; exit 1; \
		else true; fi

.PHONY: usage install serve in_virtual_env venv
