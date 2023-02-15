from distutils import core
from distutils.core import setup
from distutils.command.install import install
from distutils.command.build import build
import subprocess
import os
import sys
import logging
import traceback
import getpass
import shutil
import datetime

def init_logging():
  if not os.path.exists("/home/uvadmin/log"):
    os.makedirs("/home/uvadmin/log")

  logging.basicConfig(filename="/home/uvadmin/log/ucp_install.log",format='%(asctime)s|%(process)-5d|%(thread)d|%(filename)-30s|%(funcName)-16s|%(lineno)4d|%(levelname)-8s| %(message)s', level=logging.DEBUG)

  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s|%(process)-5d|%(thread)d|%(filename)-30s|%(funcName)-16s|%(lineno)4d|%(levelname)-8s| %(message)s')
  console.setFormatter(formatter)
  # add the handler to the root logger
  logging.getLogger('').addHandler(console)


class ucp_install(install):

  #this method created/added by Ultivoz team
  def install_sanity_check(self):

    #check username. Makesure user 'uvadmin' is executing
    if(getpass.getuser() != 'uvadmin'):
      print("you must be uvadmin to install. You are {0}. Aborting ucp installation".format(getpass.getuser()))
      sys.exit(1)

    init_logging()

    #check if /home/uvadmin/ucp exists. If so abort
    if os.path.exists("/home/uvadmin/ucp"):
      logging.info("/home/uvadmin/ucp exists already. UCP already installed. you might be installing again. Erase isntallation and try again") 
      sys.exit(1)
    

  #check if the installation folder exists
  #overriding install class run method.
  def run(self):

    #pre-installation section
    print("starting UCP pre-instatllation")
    self.install_sanity_check()

    #installation
    logging.info("starting UCP instatllation.")
    install.run(self)
    logging.info("standard UCP installation completed.")

    #post-installation
    logging.info("starting UCP post-instatllation.")
    
    ucp_install_dir = self.distribution.get_option_dict("install")["install_base"][1]
    try:
      subprocess.call(ucp_install_dir+"/utils/postinstall.sh", shell=True)
      logging.info("UCP post-installation completed.")
    except:
      logging.exception("unable to run post install script {0}. aborting now".format(ucp_install_dir+"/utils/postinstall.sh"))
      sys.exit(1)

    #TODO clean build files


class ucp_uninstall(install):
  #this method created/added by Ultivoz team
  def uninstall_sanity_check(self):

    #check username. Makesure user 'uvadmin' is executing
    if(getpass.getuser() != 'uvadmin'):
      logging.info("you must be uvadmin to uninstall. You are {0}. Aborting ucp uninstallation".format(getpass.getuser()))
      sys.exit(1)

    init_logging()

    #check if /home/uvadmin/ucp exists. If so abort
    if not os.path.exists("/home/uvadmin/ucp"):
      logging.info("/home/uvadmin/ucp not found. UCP not installed.")
      sys.exit(1)

  def run(self):
    self.uninstall_sanity_check()
    #Backup first
    logging.info("starting UCP un-instatllation")
    ucp_install_dir = self.distribution.get_option_dict("install")["install_base"][1]
    bacupdir = ucp_install_dir + datetime.datetime.now().strftime("_%d%b%Y_%H%M")
    try:
      logging.info("uninstall - starting backup from {0} to {1}".format(ucp_install_dir, bacupdir))
      shutil.copytree(ucp_install_dir, bacupdir)
      logging.info("uninstall - backup completed. backup dir {0}".format(bacupdir))
    except:
      logging.error("failed to backup from {0} to {1}. aborting uninstallation".format(ucp_install_dir, bacupdir))
      sys.exit(1)

    #backup database
    try:
      logging.info("uninstall - starting database backup. using {0}".format(ucp_install_dir+"/utils/mysql_db_snapshot.sh"))
      subprocess.call(ucp_install_dir+"/utils/mysql_db_snapshot.sh", shell=True)
      logging.info("uninstall - database backup completed")
    except:
      logging.info("uninstall - failed to execute {0} script. Aborting uninstallation".format(ucp_install_dir+"/utils/mysql_db_snapshot.sh"))
      sys.exit(1)

    #drop database
    try:
      logging.info("uninstall - starting to delete databases using {0}".format(ucp_install_dir+"/utils/mysql_db_delete.sh"))
      subprocess.call(ucp_install_dir+"/utils/mysql_db_delete.sh", shell=True)
      logging.info("uninstall - databases deleted")
    except:
      logging.info("uninstall - failed to execute {0} script. Aborting uninstallation".format(ucp_install_dir+"/utils/mysql_db_delete.sh"))
      sys.exit(1)

    try:
      #uninstall/remove
      logging.info("uninstall - strting to remove ucp applicaiton {0}".format(ucp_install_dir))
      shutil.rmtree(ucp_install_dir)
      logging.info("uninstall - ucp {0} app removed".format(ucp_install_dir))
    except:
      logging.info("uninstall - failed to remove {0}. unisnstallation not completed successfuly".format(ucp_install_dir))

class ucp_build(build):
  #overriding build class run method.
  def run(self):
    logging.info("starting UCP build at {0}".format(os.getcwd()))
    build.run(self)
    logging.info("UCP build generated successfully")
    #os.remove(os.getcwd()+"/MANIFEST")
    #TODO post build activities

def gen_data_files(*dirs):
  results = []
  for src_dir in dirs:
    for root,dirs,files in os.walk(src_dir):
      results.append((root, map(lambda f:root + "/" + f, files)))
  #print("data files {0}".format(results))
  return results

#setup.py execution starts from here
#invoke distutils setup method
setup(
    name='ucp',
    version='1.0-13.4',
    packages=['api', 'core', 'apps.vt', 'apps.blaster', 'apps.postbox', 'apps.plutus', 'monitor', 'reports', 'test', 'utils', 'web'],
    data_files = gen_data_files('conf', 'utils', 'database'),
    license='Ultivoz proprietary',
    long_description=open('README.txt').read(),
    cmdclass={'build' : ucp_build, 'install' : ucp_install, 'uninstall' : ucp_uninstall},
)
