#!/bin/bash -e

BASEDIR=`dirname $0`/..
source "${BASEDIR}/sbin/.env"


# PYTHON_VERSION=${PYTHON_VERSION:=${DEVELOP_PYTHON_VERSION}}

virtualenv -p python${PYTHON_VERSION} -q ${BASEDIR}/env

source $BASEDIR/env/bin/activate

pip install -r $BASEDIR/requirements.txt # --process-dependency-links
