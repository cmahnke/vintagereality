#!/usr/bin/env bash

for IMAGE in $(find content/post -name '*.gif') ;
do
  FILENAME=$(basename $IMAGE)
  DIRNAME=$(dirname $IMAGE)

  TMP_FILE="$DIRNAME/$FILENAME-tmp.gif"
  echo "$IMAGE -> $TMP_FILE"
  gifsicle -O3 --lossy=30 -o "$TMP_FILE" "$IMAGE"
  rm "$IMAGE"
  mv "$TMP_FILE" "$IMAGE"
done
