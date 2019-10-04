usage:
	@echo "Make targets: install, serve"

install: in_virtual_env
	pip install lektor

serve: in_virtual_env
	cd "Swiss Python Summit 2020" && lektor server -f scss --browse

in_virtual_env:
	@if python -c 'import sys; (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)) and sys.exit(1) or sys.exit(0)'; then \
		echo "Error: An active virtual environment is required"; exit 1; \
		else true; fi

.PHONY: usage install serve in_virtual_env
