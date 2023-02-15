import os
import re


def putValue(search1,replaceString,path=r'/home/rup/ucp/conf/ucp.conf'):
    fileVar = open(path,'r') #open for append
    output = []
    line = fileVar.readline()
    while line:
        match = line.find(search1)
        if match != -1:
            floatVar=1
            for word in line.split():
                if len(word) == len(search1):
                    output.append(search1+' = '+replaceString+'\n')
                    floatVar=0
            if floatVar!=0:
                output.append(line)
        else:
            output.append(line)
        line = fileVar.readline()
    fileVar.close()
    fileVar = open(path,'w')
    fileVar.writelines(output)
    fileVar.close()
#if __main__ == "__main__" :

#putValue('db_user_password','test1')

