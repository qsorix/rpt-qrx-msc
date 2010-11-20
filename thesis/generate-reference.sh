#!/bin/sh

SOURCE=reference/source
TARGET=reference/build/latex

sphinx-build -b latex "$SOURCE" "$TARGET" || exit 1
make -C "$TARGET" || exit 1
sed -e '1,/--MAGIC-START-TAG--/d' -e '/--MAGIC-END-TAG--/,$ d' "$TARGET/Reference.tex" > a2-reference-content.tex || exit 1
sed -e 's/\\hyperref\[[^]]\+]//g' -e 's/\\phantomsection//g' -i a2-reference-content.tex || exit 1

