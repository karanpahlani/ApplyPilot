.PHONY: help setup install playwright init scrape apply watch email web clean lint test

# Default target
help:
	@echo "Available commands:"
	@echo "  setup      - Create virtual environment and install dependencies"
	@echo "  install    - Install Python dependencies"
	@echo "  playwright - Install Playwright browsers"
	@echo "  init       - Initialize the database"
	@echo "  scrape     - Scrape LinkedIn jobs"
	@echo "  apply      - Run semi-automatic application process"
	@echo "  watch      - Watch for confirmation emails"
	@echo "  email      - Send cold emails to recruiters"
	@echo "  web        - Run FastAPI web dashboard"
	@echo "  clean      - Clean up temporary files"
	@echo "  lint       - Run code linting (if available)"
	@echo "  test       - Run tests (if available)"

# Setup virtual environment and install dependencies
setup:
	python3 -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"
	@echo "Then run: make install"

# Install dependencies
install:
	source .venv/bin/activate && pip3 install -r requirements.txt

# Install Playwright browsers
playwright:
	source .venv/bin/activate && python3 -m playwright install

# Initialize database
init:
	source .venv/bin/activate && python3 -c "from models import init_db; init_db(); print('DB ready')"

# Scrape LinkedIn jobs
scrape:
	source .venv/bin/activate && python3 main.py scrape

# Run semi-automatic application process
apply:
	source .venv/bin/activate && python3 main.py apply

# Watch for confirmation emails
watch:
	source .venv/bin/activate && python3 main.py watch

# Send cold emails to recruiters
email:
	source .venv/bin/activate && python3 cold_email.py

# Run FastAPI web dashboard
web:
	source .venv/bin/activate && uvicorn app:app --reload

# Run web dashboard in production mode
web-prod:
	source .venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8000

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf dist/
	rm -rf build/

# Run linting (add tools as needed)
lint:
	@echo "No linting tools configured. Add flake8, black, or other tools to requirements.txt"

# Run tests (add test framework as needed)
test:
	@echo "No test framework configured. Add pytest or other testing tools to requirements.txt"

# Full setup from scratch
full-setup: setup install playwright init
	@echo "Full setup complete! Don't forget to:"
	@echo "1. Copy .env.example to .env and configure it"
	@echo "2. Add your resume to data/karan_resume.pdf"
	@echo "3. Update data/static_profile.json"