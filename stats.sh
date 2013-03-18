#!/bin/bash

wc -l \
$(find \
-name "*.py" -o \
-name "*.txt" -o \
-name "*.md" -o \
-name ".gitconfig" -o \
-name "*.sh" -o \
-name "*.cfg" -o \
-name "*.xml" -o \
-name "*.xsd") \
| sort -gr | less

