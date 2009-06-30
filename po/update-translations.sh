#!/bin/bash

# Extract strings from *.glade files
intltool-extract --type=gettext/glade ../data/*.glade
mv ../data/*.glade.h .

# Create messages.pot
echo
echo "*** Creating messages.pot..."
xgettext -k_ -kN_ -o messages.pot ../src/*.py *.glade.h

# Remove unneeded files
echo
echo "*** Removing unneeded files..."
rm *.glade.h

echo
for file in *.po; do
	echo "*** Updating '$file'..."
	msgmerge -U "$file" messages.pot
done

echo
echo "Done."
