#!/bin/bash
# Run all tests with coverage

source venv/bin/activate
pytest tests/ -v --cov=src/aicc --cov-report=term-missing --cov-report=html
