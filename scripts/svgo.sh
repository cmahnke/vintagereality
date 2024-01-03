#!/usr/bin/env bash

IMAGES=$(find "Source Files" -name '*.svg') ./themes/projektemacher-base/scripts/svgo.sh static/images/svgs
