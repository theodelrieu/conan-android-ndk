#!/bin/bash

set -x
set -e

run_python2() {
  case $TRAVIS_OS_NAME in
    linux*)
      run_python2_linux "$@"
      ;;
    osx*)
      run_python2_osx "$@"
      ;;
    windows*)
      run_python2_windows "$@"
      ;;
    esac
}

run_python2_linux() {
  python2.7 "$@"
}

run_python2_osx() {
  /usr/local/bin/python $@
}

run_python2_windows() {
  /c/python27/python $@
}

install_python() {
  case $TRAVIS_OS_NAME in
    linux*)
      install_python_linux
      export PATH="${HOME}/.local/bin:${PATH}"
      ;;
    osx*)
      install_python_osx
      export PATH="${HOME}/Library/Python/2.7/bin/:${PATH}"
      ;;
    windows*)
      install_python_windows
      export PATH="/c/python27/scripts:${PATH}"
      ;;
    esac
}

install_python_linux() {
  :
}

install_python_osx() {
  :
}

install_python_windows() {
   choco install python2
}
