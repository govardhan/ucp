# -*- coding: utf-8 -*-
import urllib
import urllib2

def toHex(s):
  lst = []
  for ch in s:
    hv = hex(ord(ch)).replace('x', '')
    if len(hv) == 1:
      hv = '000'+hv
    elif len(hv) == 2:
      hv = '00'+hv
    elif len(hv) == 3:
      hv = '0'+hv

    lst.append(hv)
  return reduce(lambda x,y:x+y, lst)

#http://192.168.1.3:8000/testsendsms?username=astc&source=test123&destination=6583833891&dlr=0&message=hello%20how%20are%20you&password=h1vz7v&type=2"
#url = "http://192.168.1.3:8000/testsendsms"
url = "http://smsplus1.routesms.com:8080/bulksms/bulksms"
uuid = 1

username="astc"
sender="rsmsutf8"
msisdn="6591724422"
#msisdn="6583833891"
password="h1vz7v"
type = 0 
#smstext="hello how are yoau"
smstext=u"هذا هو عادة صعبة ولكن انا ذاهب لتجاوز الصعب"
#smstext=u"Cela est gralement"
#smstext=u"Cela est généralement"
#print("len smstext = {0} ".format(len(smstext)))
#print("unicode smstext = {0} ".format(unicode(smstext)))
#print("type smstext = {0} ".format( type(smstext)))
#print type("hello").__name__

try:
  smstext.decode('ascii')
except:
  type = 2 
  smstext = toHex(smstext)
  #print("smstext after encode  = {0}".format(smstext))

params = urllib.urlencode({'username':username,'password':password,'type':type,'dlr':'1','source':sender,'destination':msisdn,'message':smstext})

print("url = {0}".format(url))
print ("params = {0}".format(params))

if True:
  try:
    #params - second arg in urllib2.urlopen() make POST reuest 
    response = urllib2.urlopen(url,params)
    #response = urllib2.urlopen(fullurl)
  except urllib2.URLError, e:
    print("{0} SMS to {1} failed to send. url {2}".format(uuid, msisdn , url ))
  else:
    responsebody = response.read()
    print("{0} HTTP response body {1}".format(uuid, responsebody))
  
