#!/usr/bin/env bash
IFS=$(echo -en "\n\b")
for IMAGE in $(find ./Source\ Files/ -name '*.svg')
do
    IMAGE_PREFIX=$(basename "$IMAGE" .svg)
    TMP_FILE=static/images/svgs/$(echo $IMAGE_PREFIX | tr '[:upper:]' '[:lower:]').svg

    echo "Processing $IMAGE..."
    yarn run svgo --config ./config/svgo.config.js -i "$IMAGE" -o "$TMP_FILE" --multipass

done
