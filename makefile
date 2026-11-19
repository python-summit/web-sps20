.PHONY: usage install serve build test

usage:
	@echo "Make targets: install, serve, build, test"

install:
	uv sync --locked

serve:
	uv run --locked lektor --project sps20 server -f scss --browse

build:
	uv run --locked lektor --project sps20 build -f scss --output-path build

test:
	uv run --locked lektor --version
