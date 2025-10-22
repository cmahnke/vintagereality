#!/usr/bin/env bash

set -e

echo "Set SKIP_IIIF to something to disable generation of IIIF derivates"
./scripts/iiif.sh

#NPM dependencies
echo "Calling theme scripts"
for SCRIPT in $PWD/themes/projektemacher-base/scripts/init/*.sh ; do
    echo "Running $SCRIPT"
    bash "$SCRIPT"
    ERR=$?
    if [ $ERR -ne 0 ] ; then
        echo "Execution of '$SCRIPT' failed!"
        exit $ERR
    fi
done

# Generate Previews
./themes/projektemacher-base/scripts/preview.sh

set -e -o pipefail

PYTHON=`./themes/projektemacher-base/scripts/find-python3.sh` ./scripts/3d.sh
./scripts/svgo.sh

SOURCE="static/images/svgs/favicon.svg" OPTIONS="-fuzz 5% -transparent white" ./themes/projektemacher-base/scripts/favicon.sh

./themes/projektemacher-base/scripts/saxon.sh -s:Source\ Files/svgs/glasses_background.svg -xsl:themes/projektemacher-base/scripts/xslt/svg-clippath.xsl -o:static/images/svgs/glasses_background-clippath.svg

./scripts/compress-gif.sh

if [ -d ./scripts/post-build ] ; then
    echo "Don't forget to run post build scripts after 'hugo'!"
fi
