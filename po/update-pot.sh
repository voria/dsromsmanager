#!/bin/bash

# Extract strings from *.glade files
intltool-extract --type=gettext/glade ../data/*.glade
mv ../data/*.glade.h .

# Create messages.pot
echo "Creating messages.pot..."
xgettext -k_ -kN_ -o messages.pot ../src/*.py *.glade.h

# Remove unneeded files
echo "Removing unneeded files..."
rm *.glade.h

echo "Done."
