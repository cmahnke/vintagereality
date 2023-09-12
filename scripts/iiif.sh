#!/usr/bin/env bash

IMAGES=$(find content -maxdepth 5 \( -name '*.jpg' -o -name '*.jxl' \) -a ! -name '*-*') ./themes/projektemacher-base/scripts/iiif.sh
