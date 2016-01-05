Calamari server
===============

1. run command.

/usr/bin/calamari-ctl initialize \
     --admin-username admin \
     --admin-password yunshan3302 \
     --admin-email x@yunshan.net.cn

systemctl restart httpd
systemctl restart supervisord.service
systemctl restart salt-master.service

salt-key -A -y