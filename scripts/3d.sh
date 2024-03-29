#!/usr/bin/env bash

set -e -o pipefail

IMAGE_PREFIX=content/
IMG_NAME_PREFIX=front
IMG_METADATA=3d-images.json
SCRIPT=`dirname $0`/./image-splitter.py


if [ -z "$PYTHON" ] ; then
  PYTHON=python3
else
  echo "Using python command '$python'"
fi

if [ `$PYTHON -V|cut -d ' ' -f2|cut -d '.' -f2` -gt 10 ] ; then
  echo "Warning PyJXL not working with newer python versions"
  PARALLEL_OPTS="--halt-on-error 2"
fi

if [ -z "$CORES" ] ; then
  # https://stackoverflow.com/a/45181694
  if [ ! command -v getconf &> /dev/null ] ; then
    CORES=2
  else
    CORES=$(getconf _NPROCESSORS_ONLN)
  fi
fi
JOBFILE=$(mktemp) # The GNU version of the tool is a step backwards, on BSD this works as well: -t 3D_JOBS
mkdir -p ~/.parallel
touch ~/.parallel/will-cite

for META in `find "$IMAGE_PREFIX" -name "$IMG_METADATA"`
do
    DIR=`dirname $META`
    if [ -r "$DIR/$IMG_NAME_PREFIX.jpg" ] ; then
      IMG_FILE="$DIR/$IMG_NAME_PREFIX.jpg"
    elif [ -r "$DIR/$IMG_NAME_PREFIX.jxl" ] ; then
      IMG_FILE="$DIR/$IMG_NAME_PREFIX.jxl"
    else
      IMG_FILE=$DIR/$(jq -r .file $META)
    fi
    echo "$PYTHON $SCRIPT -d -s --image $IMG_FILE --coords $DIR/3d-images.json --output jps images gif jpg mpo depthmap" >> $JOBFILE

done
echo "Running generated jobs from $JOBFILE, $CORES in parallel"
parallel $PARALLEL_OPTS --jobs $CORES < $JOBFILE
if [ $? -ne 0 ] ; then
  echo "Image processing failed!"
  exit 10
fi
