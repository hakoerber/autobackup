#!/bin/sh
PYTHONPATH=src python -m unittest discover  --start-directory tests --pattern 'test_*.py'
