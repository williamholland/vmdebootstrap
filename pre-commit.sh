#!/bin/sh

set -e

if [ -x /usr/bin/yarn ]; then
    yarns/run-tests --env TESTS=fast
else
    echo "Please install cmdtest to use the pre-commit hook!"
    exit 1
fi
