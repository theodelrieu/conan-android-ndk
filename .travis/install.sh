#!/bin/bash

set -x
set -e

source .travis/ci.sh

install_python
run_python2 -m pip install conan conan_package_tools --user
conan user
