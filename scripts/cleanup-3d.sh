#!/bin/sh

find content \( -name '*.mpo' -o -name '*.gif' -o -name '*.jps' -o -name '*-anaglyph.*' -o -name '*-left.*' -o -name '*-right.*' \) -print -exec rm {} \;
