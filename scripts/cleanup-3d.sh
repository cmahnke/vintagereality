#!/bin/sh

find content \( -name '*.mpo' -o -name '*.gif' -o -name '*.jps' -o -name '*-anaglyph.*'  -o -name '*-depthmap.*' -o -name '*-white_balance.*' -o -name '*-left.*' -o -name '*-right.*' -o -name '*.gif-tmp.gif' \) -print -exec rm {} \;
