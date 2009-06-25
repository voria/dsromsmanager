#!/bin/bash

for file in *.po; do
	echo "* Updating '$file'..."
	msgmerge -U "$file" messages.pot
done
