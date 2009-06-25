#!/bin/bash

for file in *.po; do
	echo "Compiling '$file'..."
	LANG=`echo $file | sed s/.po//`
	DIR=locale/$LANG/LC_MESSAGES/
	mkdir -p $DIR
	msgfmt "$file" -o $DIR/DsRomsManager.mo
done

echo "Done."
