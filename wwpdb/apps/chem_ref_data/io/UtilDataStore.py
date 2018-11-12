##
# File:    UtilDataStore.py
# Date:    6-July-2012
#
# Updates:
#            7-July-2012 jdw make store path depend on entryId
#           12- Feb-2013 jdw add append/extend methods for assigning list values
##
"""
Provide a storage interface for miscellaneous key,value data.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.07"


import sys, cPickle, time, os.path


class UtilDataStore(object):
    """  Provide a storage interface for miscellaneous session key,value data.
        
    """
    def __init__(self,reqObj,prefix=None,verbose=False,log=sys.stderr):
        self.__verbose=verbose
        self.__lfh=log
        self.__reqObj=reqObj
        self.__filePrefix=prefix if prefix is not None else 'general'
        self.__sessionPath=None
        self.__filePath=None
        if reqObj is not None:
            self.__setup()
        
    def __setup(self):
        self.__siteId=self.__reqObj.getValue("WWPDB_SITE_ID")
        self.__sObj  =self.__reqObj.getSessionObj()
        self.__sessionId=self.__sObj.getId()
        self.__sessionPath=self.__sObj.getPath()
        self.__D={}
        #
        #self.__pickleProtocol = cPickle.HIGHEST_PROTOCOL
        self.__pickleProtocol=0
        try:
            self.__filePath = os.path.join(self.__sessionPath,self.__filePrefix+"-util-session.pic")
            if (self.__verbose):
                self.__lfh.write("+UtilDataStore.__setup() - session id %s \n" % self.__sessionId)
                self.__lfh.write("+UtilDataStore.__setup() - data store path %s\n" % self.__filePath)               
            self.deserialize()
        except:
            self.__lfh.write("+UtilDataStore.__setup() - Failed to open data store for session id %s data store path %s\n" %
                             (self.__sessionId,self.__filePath))            

    def reset(self):
        self.__D={}

    def getFilePath(self):
        return self.__filePath
       
    def serialize(self):
        try:
            fb=open(self.__filePath,'wb')
            cPickle.dump(self.__D,fb,self.__pickleProtocol)
            fb.close()
        except:
            pass
            
    def deserialize(self):
        try:
            fb=open(self.__filePath,'rb')
            self.__D=cPickle.load(fb)
            fb.close()
            return True
        except:
            return False

    def get(self,key):
        try:
            return(self.__D[key])
        except:
            return None

    def set(self,key,value):
        try:
            self.__D[key]=value
            return True
        except:
            return False

    def append(self,key,value):
        try:
            if not self.__D.has_key(key):
                self.__D[key]=[]
            self.__D[key].append(value)
            return True
        except:
            return False

    def extend(self,key,valueList):
        try:
            if not self.__D.has_key(key):
                self.__D[key]=[]
            self.__D[key].extend(valueList)
            return True
        except:
            return False


    def getDictionary(self):
        return self.__D
    

