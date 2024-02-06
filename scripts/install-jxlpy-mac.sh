#!/bin/sh
PYTHON=`./scripts/find-python3.sh`

export LDFLAGS=-L/opt/homebrew/lib
export CPPFLAGS=-I/opt/homebrew/include

$PYTHON -m pip install 'jxlpy @ git+https://github.com/olokelo/jxlpy@4cc41c4ec51dc2099c5b4b65235859f869e98ea0'
