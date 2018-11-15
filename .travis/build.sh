#!/bin/bash

set -x
set -e

source .travis/ci.sh

run_python2 build.py
