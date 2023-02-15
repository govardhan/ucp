
exec 1>/home/uvadmin/log/ucp_install.log 2>&1

tstamp=`date +'%d%h%Y_%H%M'`

echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | database backup will be at /tmp/dump_${tstamp}"

#make sure user running this commad has sufficient access
#mkdir -p /tmp/dump_${tstamp}/{core,blaster}
mkdir -p /tmp/dump_${tstamp}/core

echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | starting core database backup"
mysqldump -uuvadmin -puvadmin core --tab=/tmp/dump_${tstamp}/core

#echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | tarting blaster database backup"
#mysqldump -uuvadmin -puvadmin blaster --tab=/tmp/dump_${tstamp}/blaster
#echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | database backup completed"

#mv /tmp/dump .
