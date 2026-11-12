.DEFAULT_GOAL := help

ifeq ($(OS),Windows_NT)
SHELL := cmd.exe
.SHELLFLAGS := /c
PYTHON ?= $(CURDIR)/venv/Scripts/python.exe
else
PYTHON ?= $(CURDIR)/venv/bin/python
endif

.PHONY: help backend frontend test migrate lint build test-e2e

help:
	@echo make backend   - Start the FastAPI development server
	@echo make frontend  - Start the Vite development server
	@echo make test      - Run backend tests
	@echo make migrate   - Apply database migrations
	@echo make lint      - Check frontend code
	@echo make build     - Build the frontend
	@echo make test-e2e  - Run desktop and mobile browser tests

backend:
	"$(PYTHON)" -m uvicorn main:app --app-dir src/v1 --reload

frontend:
	npm --prefix trading-engine-frontend run dev

test:
	"$(PYTHON)" -m pytest -q

migrate:
	cd src/v1 && "$(PYTHON)" -m alembic upgrade head

lint:
	npm --prefix trading-engine-frontend run lint

build:
	npm --prefix trading-engine-frontend run build

test-e2e:
	npm --prefix trading-engine-frontend run test:e2e
