%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%global version   1.4.0
%global revision  1
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
Requires:       salt-master salt-minion supervisor python-twisted-core python-django-rest-framework
Requires:       python-six python-psycogreen python-zmq m2crypto python-zerorpc
Requires:       python-mako python-psycopg2 python-manhole python-dateutil python-markdown
Requires:       python-django python-django-tagging python-django-jsonfield python-django-filter
Requires:       python-django-nose python-nose python-mock python-argparse python-requests
Requires:       python-sphinx python-psycogreen python-psutil python-gevent python-greenlet
Requires:       python-wsgiref python-sqlalchemy python-alembic Cython python-coverage
Requires:       postgresql postgresql-libs postgresql-server
Requires:       dejavu-sans-fonts dejavu-serif-fonts django-tagging
Requires:       mod_wsgi pycairo pyparsing python-simplejson pytz
Requires:       graphite python-carbon python-whisper
%if 0%{?rhel} && 0%{?rhel} < 7
Requires:       python-importlib
%endif
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
cd ../

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
%if 0%{?rhel} && 0%{?rhel} >= 7
%{__install} -D -m 0644 conf/calamari/rhel7/calamari.conf \
    ${RPM_BUILD_ROOT}/etc/calamari/calamari.conf
%else
%{__install} -D -m 0644 conf/calamari/el6/calamari.conf \
    ${RPM_BUILD_ROOT}/etc/calamari/calamari.conf
%endif
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


%clean
rm -rf $RPM_BUILD_ROOT

%files -n calamari-server
/opt/calamari/
%{_bindir}/calamari-ctl
%{_bindir}/cthulhu-manager
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
%{python_sitelib}/calamari_cthulhu*.egg-info
%{python_sitelib}/calamari_web
%{python_sitelib}/cthulhu
%{python_sitelib}/calamari_web*.egg-info
%{python_sitelib}/calamari_rest
%{python_sitelib}/calamari_rest_api*.egg-info


%post -n calamari-server
chown -R apache.apache /opt/calamari/webapp/calamari
if [[ -f "/etc/httpd/conf.d/welcome.conf" ]]; then
    mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.orig
fi
chown -R apache:apache /var/log/calamari
chown -R apache:apache /var/lib/graphite
exit 0

%preun -n calamari-server
%if 0%{?rhel} && 0%{?rhel} >= 7
systemctl stop httpd
systemctl stop supervisord
systemctl stop salt-master
%else
service httpd stop
service supervisord stop
service salt-master stop
%endif
exit 0

%postun -n calamari-server
# Remove anything left behind in the calamari and graphite
# virtual environment  directories, if this is a "last-instance" call
rm -rf /opt/graphite
rm -rf /opt/calamari
rm -rf /var/log/graphite
rm -rf /var/log/calamari
rm -rf /var/lib/graphite/whisper
exit 0

%changelog
* Thu Jan 5 2016 David <d05660@gmail.com> - 1.4.0-1
- Update to new version