#!/bin/bash

if [ $# -ne 3 ]; then
    echo "Usage: `basename $0` <address> <port> <size>"
    exit 2
fi

if [ -f big-data-file ]; then
    echo "Big data file already exists..."
else
    echo "Creating big data file... (it may take some time)"
    dd if=/dev/urandom of=./big-data-file bs=1M count=$3
fi

type -P ctorrent &>/dev/null || { echo "Cannot create torrent, You don't have ctorrent :/" >&2; exit 1; }

if [ -f big-data-file.torrent ]; then
    rm big-data-file.torrent
fi

echo "Creating torrent file..."
ctorrent -t -s ./big-data-file.torrent -u http://$1:$2/announce -p ./big-data-file
