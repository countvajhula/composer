#!/bin/bash
if [ -d "tests/testwikis" ]
then
	cd tests/testwikis && ./reset.sh
	if [ -d "userwiki" ]
	then
		cd userwiki && yes | ./reset.sh
	fi
fi
