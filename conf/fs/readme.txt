mv /usr/local/freeswitch/conf/vars.xml /usr/local/freeswitch/conf/vars.xml_orig
cp vars.xml /usr/local/freeswitch/conf/

cp 02_eventsock.xml /usr/local/freeswitch/conf/dialplan/public/

mv /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml_orig
cp acl.conf.xml /usr/local/freeswitch/conf/autoload_configs/


