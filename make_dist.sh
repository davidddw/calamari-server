#!/bin/bash

git archive --format=tar \
    --prefix=calamari-server-1.4.0/ 1.4.0 \
    | gzip > calamari-server-1.4.0.tar.gz
/usr/bin/mv calamari-server-1.4.0.tar.gz /root/rpmbuild/SOURCES/