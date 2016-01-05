%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%global version   1.4.0
%global revision  1
%global FLAVOR    rhel7
%global src_name  calamari


Name:           calamari-server
Version:        %{version}
Release:        %{?revision}%{?dist}
License:        LGPL-2.1+
Summary:        Manage and monitor Ceph with a REST API
Group:          System/Filesystems
BuildRoot:      %{_tmppath}/%{src_name}-%{version}-%{release}-buildroot
Vendor:         Inktank Storage Inc. <info@inktank.com>
Url:            http://www.inktank.com/enterprise/
BuildRequires:  postgresql-libs
BuildRequires:  python-coverage m2crypto salt python-zerorpc python-twisted-core redhat-lsb-core
Requires:       httpd mod_wsgi cairo logrotate redhat-lsb-core pycairo python-setuptools
Requires:       salt-master salt-minion python-twisted-core python-django-rest-framework
Requires:       python-six python-psycogreen python-zmq m2crypto python-zerorpc
Requires:       python-mako python-psycopg2 python-manhole python-dateutil python-markdown
Requires:       python-django python-django-tagging python-django-jsonfield python-django-filter
Requires:       python-django-nose python-nose python-mock python-argparse python-requests
Requires:       python-sphinx python-psycogreen python-psutil python-gevent python-greenlet
Requires:       python-wsgiref python-sqlalchemy python-alembic Cython python-coverage
Requires:       postgresql postgresql-libs postgresql-server
Requires:       dejavu-sans-fonts dejavu-serif-fonts django-tagging
Requires:       mod_wsgi pycairo pyparsing python-simplejson pytz
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

%description -n calamari-server
Calamari is a webapp to monitor and control a Ceph cluster via a web
browser. 


%prep
%setup -q -n %{name}-%{version}


%build
cd calamari-common
%{__python} setup.py build
cd ../cthulhu
%{__python} setup.py build
cd ../calamari-web
%{__python} setup.py build
cd ../rest-api
%{__python} setup.py build
cd ../whisper
%{__python} setup.py build
cd ../carbon
%{__python} setup.py build
cd ../graphite
%{__python} setup.py build
cd ..


%install
cd calamari-common
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT 
cd ../cthulhu
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
cd ../calamari-web
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
cd ../rest-api
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
cd ../whisper
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
cd ../carbon
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT \
    --install-lib=%{python_sitelib} \
    --install-scripts=%{_bindir}
cd ../graphite
%{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT \
    --install-lib=%{python_sitelib} \
    --install-data=%{_datadir}/graphite \
    --install-scripts=%{_bindir}
cd ../

# remove .py suffix
for i in $RPM_BUILD_ROOT%{_bindir}/*.py; do
    mv ${i} ${i%%.py}
done

%{__install} -d ${RPM_BUILD_ROOT}%{_sysconfdir}/graphite
%{__install} -Dp -m0644 graphite/webapp/graphite/local_settings.py.example \
    ${RPM_BUILD_ROOT}%{_sysconfdir}/graphite/local_settings.py
ln -sf %{_sysconfdir}/graphite/local_settings.py \
    ${RPM_BUILD_ROOT}%{python_sitelib}/graphite/local_settings.py
%{__install} -Dp -m0644 graphite/conf/dashboard.conf.example  \
    ${RPM_BUILD_ROOT}%{_sysconfdir}/graphite/dashboard.conf
%{__install} -Dp -m0644 graphite/conf/graphite.wsgi.example \
    ${RPM_BUILD_ROOT}%{_datadir}/graphite/graphite.wsgi

# Make manage.py available at an easier location.
ln -s %{python_sitelib}/graphite/manage.py \
    %{buildroot}%{_bindir}/graphite-manage

# Rename build-index.sh.
mv ${RPM_BUILD_ROOT}%{_bindir}/build-index.sh ${RPM_BUILD_ROOT}%{_bindir}/graphite-build-index

%{__install} -D -m 0644 conf/calamari.wsgi \
    ${RPM_BUILD_ROOT}/opt/calamari/conf/calamari.wsgi

# install supervisord config
%{__install} -D -m 0644 conf/supervisord.calamari.ini \
    ${RPM_BUILD_ROOT}/etc/supervisord.d/calamari.ini

%{__install} -d ${RPM_BUILD_ROOT}/etc/salt/master.d
%{__install} -D -m 0644 conf/salt.master.conf \
    ${RPM_BUILD_ROOT}/etc/salt/master.d/calamari.conf


%{__install} -D -m 0644 conf/carbon/carbon.conf \
    ${RPM_BUILD_ROOT}/etc/graphite/carbon.conf
%{__install} -D -m 0644 conf/carbon/storage-schemas.conf \
    ${RPM_BUILD_ROOT}/etc/graphite/storage-schemas.conf
# wsgi conf for graphite constructed in postinst
# log dirs for Django apps
%{__install} -d ${RPM_BUILD_ROOT}/var/log/graphite
%{__install} -d ${RPM_BUILD_ROOT}/var/log/calamari
%{__install} -d ${RPM_BUILD_ROOT}/var/lib/graphite/log/webapp
%{__install} -d ${RPM_BUILD_ROOT}/var/lib/graphite/whisper
%{__install} -d ${RPM_BUILD_ROOT}/var/lib/graphite/rrd
%{__install} -d ${RPM_BUILD_ROOT}/var/lib/calamari
%{__install} -d ${RPM_BUILD_ROOT}/var/lib/cthulhu

%{__install} -d ${RPM_BUILD_ROOT}/etc/calamari
%{__install} -D -m 0644 conf/calamari/%{FLAVOR}/calamari.conf \
    ${RPM_BUILD_ROOT}/etc/calamari/calamari.conf
sed -i 's#/opt/calamari/venv#/usr/share/graphite#g' \
    ${RPM_BUILD_ROOT}/etc/calamari/calamari.conf
%{__install} -D -m 0644 conf/alembic.ini \
    ${RPM_BUILD_ROOT}/etc/calamari/alembic.ini
%{__install} -d ${RPM_BUILD_ROOT}/etc/logrotate.d
%{__install} -D -m 0644 conf/logrotate.d/calamari \
    ${RPM_BUILD_ROOT}/etc/logrotate.d/calamari

# copy calamari webapp files into place
%{__install} -d -m 755 ${RPM_BUILD_ROOT}/opt/calamari/webapp
cp -rp webapp/calamari ${RPM_BUILD_ROOT}/opt/calamari/webapp

# generate secret_key
echo 'yunshan-0wn7b=wiud8u9-)%b(l1#&ph1f+npvpej_e_+-er465*@(w9@livecloud' > \
        ${RPM_BUILD_ROOT}/opt/calamari/webapp/secret.key

%{__install} -d ${RPM_BUILD_ROOT}/opt/calamari/salt
cp -rp salt/srv/* ${RPM_BUILD_ROOT}/opt/calamari/salt/
%{__install} -d ${RPM_BUILD_ROOT}/opt/calamari/salt-local
cp -rp salt/local/*.sls ${RPM_BUILD_ROOT}/opt/calamari/salt-local

%{__install} -d ${RPM_BUILD_ROOT}/opt/calamari/alembic
cp -rp alembic/* ${RPM_BUILD_ROOT}/opt/calamari/alembic

# add WSGISocketPrefix, see:
# http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGISocketPrefix
%{__install} -D conf/httpd/calamari.conf \
    ${RPM_BUILD_ROOT}/etc/httpd/conf.d/calamari.conf
sed -i '1iWSGISocketPrefix run/wsgi' ${RPM_BUILD_ROOT}/etc/httpd/conf.d/calamari.conf

rm -rf ${RPM_BUILD_ROOT}/opt/graphite/examples
rm -rf ${RPM_BUILD_ROOT}%{python_sitelib}/graphite/thirdparty


%clean
rm -rf $RPM_BUILD_ROOT

%files -n calamari-server
%{_bindir}/rrd2whisper
%{_bindir}/whisper-create
%{_bindir}/whisper-dump
%{_bindir}/whisper-diff
%{_bindir}/whisper-fetch
%{_bindir}/whisper-fill
%{_bindir}/whisper-info
%{_bindir}/whisper-merge
%{_bindir}/whisper-resize
%{_bindir}/whisper-set-aggregation-method
%{_bindir}/whisper-update
%{_bindir}/carbon-aggregator
%{_bindir}/carbon-cache
%{_bindir}/carbon-client
%{_bindir}/carbon-relay
%{_bindir}/validate-storage-schemas
%{_bindir}/calamari-ctl
%{_bindir}/cthulhu-manager
%{_bindir}/graphite-build-index
%{_bindir}/graphite-manage

/opt/calamari/
%{_sysconfdir}/supervisord.d/calamari.ini
%{_sysconfdir}/salt/master.d/calamari.conf
%{_sysconfdir}/logrotate.d/calamari
%{_sysconfdir}/httpd/conf.d/calamari.conf
%{_sysconfdir}/calamari/
%{_sysconfdir}/graphite/
%dir /var/lib/calamari
%dir /var/lib/cthulhu
%dir /var/lib/graphite
%dir /var/lib/graphite/log
%dir /var/lib/graphite/log/webapp
%dir /var/lib/graphite/whisper
%attr (755, apache, apache) /var/log/calamari
%attr (755, apache, apache) /var/log/graphite

%{python_sitelib}/calamari_common
%{python_sitelib}/calamari_common*.egg-info
%{python_sitelib}/whisper.py*
%{python_sitelib}/whisper*.egg-info
%{python_sitelib}/cthulhu
%{python_sitelib}/carbon
%{python_sitelib}/carbon*.egg-info
%{python_sitelib}/twisted
%{python_sitelib}/calamari_cthulhu*.egg-info
%{python_sitelib}/calamari_web
%{python_sitelib}/calamari_web*.egg-info
%{python_sitelib}/calamari_rest
%{python_sitelib}/calamari_rest_api*.egg-info
%{python_sitelib}/graphite/
%{python_sitelib}/graphite_web-*-py?.?.egg-info

%{_datadir}/graphite

%post -n calamari-server
calamari_httpd()
{
    d=$(pwd)

    # allow apache access to all
    chown -R apache.apache /opt/calamari/webapp/calamari

    # apache shouldn't need to write, but it does because
    # graphite creates index on read
    chown -R apache.apache /var/lib/graphite

    # centos64
    mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.orig
    chown -R apache:apache /var/log/calamari
    cd $d

    # Load our salt config
    %if 0%{?rhel} && 0%{?rhel} >= 7
    systemctl enable salt-master > /dev/null 2>&1
    systemctl restart salt-master
    systemctl enable supervisord > /dev/null 2>&1
    systemctl restart supervisord.service > /dev/null 2>&1
    %else
    service salt-master restart
    # Load our supervisor config
    service supervisord stop
    sleep 3
    service supervisord start
    %endif   
}

calamari_httpd
%if 0%{?rhel} && 0%{?rhel} >= 7
systemctl restart httpd
%else
service httpd stop || true
service httpd start
%endif

# Prompt the user to proceed with the final script-driven
# part of the installation process
echo "Thank you for installing Calamari."
echo ""
echo "Please run 'sudo calamari-ctl initialize' to complete the installation."
exit 0

%preun -n calamari-server
if [ $1 == 0 ] ; then 
#rm /etc/httpd/conf.d/calamari.conf
#       rm /etc/httpd/conf.d/wsgi.conf
#       mv /etc/httpd/conf.d/welcome.conf.orig /etc/httpd/conf.d/welcome.conf
    %if 0%{?rhel} && 0%{?rhel} >= 7
    systemctl stop httpd
    systemctl stop supervisord
    systemctl stop salt-master
    %else
    service httpd stop || true
    service httpd start || true
    service supervisord stop
    sed -i '/^### START calamari-server/,/^### END calamari-server/d' /etc/supervisord.conf
    service supervisord start
    %endif
fi
exit 0

%postun -n calamari-server
# Remove anything left behind in the calamari and graphite
# virtual environment  directories, if this is a "last-instance" call
if [ $1 == 0 ] ; then
    rm -rf /opt/graphite
    rm -rf /opt/calamari
    rm -rf /var/log/graphite
    rm -rf /var/log/calamari
    rm -rf /var/lib/graphite/whisper
fi
exit 0

%changelog
* Thu Jan 5 2016 David <d05660@gmail.com> - 0.9.15-1
- Update to new version