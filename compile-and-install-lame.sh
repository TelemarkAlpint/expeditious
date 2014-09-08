#!/bin/bash

# Laster ned kildekoden til lame og kompilere lokalt til /home/groups/telemark/local

set -e

if [[ $(whoami) == "vagrant" ]]; then
    echo "Running in vagrant!"
    INSTALL_LOC=/home/vagrant/local
else
    echo "Running elsewhere, assuming stud!"
    INSTALL_LOC=/home/groups/telemark/local
fi

source="http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz"
wget $source -nv
tar xf lame-3.99.5.tar.gz
cd lame-3.99.5
./configure --prefix=$INSTALL_LOC
make
make install
cd ..
rm -rf lame-3.99*
