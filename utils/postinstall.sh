
#by now installation done. /home/uvadmin/ucp exists
#Write all echos to this file also
exec 1>/home/uvadmin/log/ucp_install.log 2>&1

#[ "$#" -eq 1 ] || die "1 argument required, $# provided"

ucp_base_dir="/home/uvadmin/ucp"

mv /usr/local/freeswitch/conf/vars.xml /usr/local/freeswitch/conf/vars.xml_orig
cp ${ucp_base_dir}/conf/fs/vars.xml /usr/local/freeswitch/conf/

cp ${ucp_base_dir}/conf/fs/02_eventsock.xml /usr/local/freeswitch/conf/dialplan/public/

mv /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml_orig
cp ${ucp_base_dir}/conf/fs/acl.conf.xml /usr/local/freeswitch/conf/autoload_configs/

#TODO update fs_cli banners

#Freeswitch customization done


#create database and import data
ucp_db="/home/uvadmin/ucp/database"
mysql -uuvadmin -puvadmin < ${ucp_db}/core.sql

ucp_db_core_data=${ucp_db}"/data_core"

for filename in `ls -1 ${ucp_db_core_data}/*.txt`
do
  bname=`basename "$filename"`
  tname=`echo $bname | sed "s/.txt//"`
  echo "mysql -uuvadmin -puvadmin core -sNe \"SET FOREIGN_KEY_CHECKS = 0; load data local infile '$filename' into table $tname\" "
  `mysql -uuvadmin -puvadmin core -sNe "SET FOREIGN_KEY_CHECKS = 0; load data local infile '$filename' into table $tname"`
done


#remove database folder from /home/uvadmin/ucp
rm -rf $ucp_db

#mysql -uuvadmin -puvadmin web < ${ucp_db}/web.sql
#ucp_db_blaster_data=${ucp_db}"/data_blaster"
#
#for filename in `ls -1 ${ucp_db_blaster_data}/*.txt`
#do
#  bname=`basename "$filename"`
#  tname=`echo $bname | sed "s/.txt//"`
#  echo "mysql -uuvadmin -puvadmin blaster -sNe \"load data local infile '$filename' into table $tname\" "
#  `mysql -uuvadmin -puvadmin blaster -sNe "load data local infile '$filename' into table $tname"`
#done

#create and import completed
