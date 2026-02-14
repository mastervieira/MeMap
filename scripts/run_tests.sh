#!/bin/bash

# Script to run the full test suite with coverage report

poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
