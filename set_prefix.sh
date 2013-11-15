#!/bin/bash
# This script is intended to be called from Makefile, it sets the work directory where needed

PREFIX=$1

sed -i "s|LOCALE_DIR = .*|LOCALE_DIR = \"$PREFIX/share/locale/\"|" src/globals.py
sed -i "s|Icon=.*|Icon=$PREFIX/share/dsromsmanager/data/images/icon.png|" dsromsmanager.desktop
sed -i "s|cd .*|cd $PREFIX/share/dsromsmanager/|" dsromsmanager

