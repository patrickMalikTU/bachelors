#!/bin/bash
for ((counter = $1; counter <= $2; counter++))
do
cat booksDataFiltered_$counter.csv | grep ' [dD]er \| [dD]ie \| [dD]as \| [uU]nd \| [oO]der \| [bB]uch \| [lL]ieferung \| [gG]ut \| [sS]chlecht \| [sS]ehr \| [gG]eschenk \| [iI]ch \| [dD]enke \| [vV]iel \| [lL]ang \| [dD]ass \| [iI]n \| [zZ]u \| [dD]en \| [nN]icht \| [vV]on \| [sS]ie \| [iI]st \| [dD]es \| [sS]ich \| [mM]it \| [dD]em \| [eE]r \| [eE]in \| [aA]uf \| [sS]o \| [eE]ine \| [aA]uch \| [aA]ls \| [aA]n \| [nN]ach \| [wW]ie \| [iI]m \| [fF]ür ' >> new_de_collected.csv
done
