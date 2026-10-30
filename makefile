.PHONY: usage install serve build test

usage:
	@echo "Make targets: install, serve, build, test"

install:
	uv sync

serve:
	uv run lektor --project sps20 server -f scss --browse

build:
	uv run lektor --project sps20 build -f scss --output-path build

test:
	uv run lektor --version
