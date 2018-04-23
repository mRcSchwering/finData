#!/usr/bin/env bash

# test
if [ $1 ] && [ "$1" = "test" ]; then
  echo "Running tests..."
  if  [ $2 ]; then
    echo "look for tests with $2..."
    echo
    python3 -m unittest discover -s test -v -p "*test_$2*"
  else
    echo "running all tests ..."
    echo
    python3 -m unittest discover -s test -v
  fi

# no argument
if [ -z $1 ]; then
  echo "no argument given"
fi


#python3 -m unittest discover -s test -v -p "*test_scrape*"
#python3 -m unittest discover -s test -v -p "*test_load*"
