#!/bin/bash
for ((counter = $1; counter <= $2; counter++))
do
cat booksDataFiltered_$counter.csv | grep ^de, | grep -v Excellent | grep -v excellent | grep -v outstanding | grep -v Outstanding | grep -v great | grep -v Great | grep -v good | grep -v Good | grep -v nice | grep -v Nice | grep -v written | grep -v Written >> new_de_collected.csv
done
