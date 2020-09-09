#!/bin/bash

# Download jsmol
echo "### Donwloading jsmol"
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
unzip jmol.zip 
cd jmol-14.29.22
unzip jsmol.zip
mv jsmol ../detail/static
cd ..
rm -r jmol-14.29.22
