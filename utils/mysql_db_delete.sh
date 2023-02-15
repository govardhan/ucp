
exec 1>/home/uvadmin/log/ucp_install.log 2>&1

echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | droppinng core databasep"
mysql -uuvadmin -puvadmin -e "drop database core"

#echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | droppinng blaster databasep"
#mysql -uuvadmin -puvadmin -e "drop database blaster"
echo "`date +\"%d-%m-%y %H:%M:%S\"` | $LINENO | databases deleted"
