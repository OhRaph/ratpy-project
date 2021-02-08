#!/bin/bash

while getopts cd: option
do
case "${option}"
in
c) rm -rf `find -type d -name __pycache__`;;
d) rm -rf ${OPTARG};;
esac
done

clear
