#!/bin/sh

#python MRModel.py mass-with-dep $1.json > ../data/$1_mass_with_dep.txt
#python MRModel.py mass-without-dep $1.json > ../data/$1_mass_without_dep.txt
#python -m cProfile -o epm-profile.txt  MRModel.py step-epm $1.json > ../data3/$1_stepwise.txt
python MRModel.py step-epm $1.json > ../data6/$1_stepwise.txt
