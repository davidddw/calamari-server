#!/bin/bash

cd ../
tar zcf calamari-server-1.4.0.tar.gz calamari-server-1.4.0
/usr/bin/cp calamari-server-1.4.0.tar.gz /root/rpmbuild/SOURCES/
cd calamari-server-1.4.0
rpmbuild -ba calamari.spec