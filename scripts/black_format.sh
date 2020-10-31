#!/usr/bin/env bash
for f in $(find 'setup.py' 'fuegodata' 'tests' -name "*.py"); do black --target-version py36 "$f"; done
