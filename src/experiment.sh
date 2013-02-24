#!/bin/sh

python MRModel.py mass-with-dep $1.json > ../data/$1_mass_with_dep.txt
python MRModel.py mass-without-dep $1.json > ../data/$1_mass_without_dep.txt
python MRModel.py step-dm $1.json > ../data/$1_stepwise.txt
