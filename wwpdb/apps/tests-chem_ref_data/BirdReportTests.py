##
# File:    BirdReportTests.py
# Date:    19-Nov-2010  jdw
#
# Updates:
#
# 30-Jan-2013 jdw integrate within chemical reference data module.
##
"""
Test cases BIRD reference definition report generation and rendering.

"""
__docformat__ = "restructuredtext en"
__author__    = "John Westbrook"
__email__     = "jwest@rcsb.rutgers.edu"
__license__   = "Creative Commons Attribution 3.0 Unported"
__version__   = "V0.01"

import sys, unittest, traceback
import time, os, os.path

try:
    from wwpdb.utils.config.ConfigInfo                              import ConfigInfo,getSiteId
    from wwpdb.apps.chem_ref_data.report.BirdReport               import BirdReport
    from wwpdb.apps.chem_ref_data.report.BirdReportDepict         import BirdReportDepict
    from wwpdb.apps.chem_ref_data.webapp.WebRequest               import InputRequest
    skiptests = False
except ImportError:
    skiptests = True

@unittest.skipIf(skiptests, "Openeye import failed")
class BirdReportTests(unittest.TestCase):
    def setUp(self):
        self.__verbose=True
        self.__lfh=sys.stderr

        # Pick up site information from the environment or failover to the development site id.
        self.__siteId=getSiteId(defaultSiteId='WWPDB_DEV_TEST')
        self.__lfh.write("\nTesting with site environment for:  %s\n" % self.__siteId)
        cI=ConfigInfo(self.__siteId)
        self.__topPath=self.__cI.get('SITE_WEB_APPS_TOP_PATH')
        self.__topSessionPath=self.__cI.get('SITE_WEB_APPS_TOP_SESSIONS_PATH')        
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj=InputRequest(paramDict={},verbose=self.__verbose,log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TopPath",        self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="text")
        self.__sobj=self.__reqObj.newSessionObj()
        self.__sessionPath=self.__sobj.getPath()
        self.__fileList=[(os.path.abspath('FAM_000311.cif'),'FAM_000311'),(os.path.abspath('FAM_000001.cif'),'FAM_000001')]
        

    def tearDown(self):
        pass
    
    def testReportFileOne(self): 
        """ 
        """
        self.__lfh.write("\n------------------------ ")
        self.__lfh.write("Starting test function  %s" % sys._getframe().f_code.co_name)
        self.__lfh.write(" -------------------------\n")
        try:
            prdId=self.__fileList[0][1]
            fileFormat='cif'
            filePath=self.__fileList[0][0]
            #
            self.__lfh.write("Session path is %s\n" % self.__sessionPath)
            prd=BirdReport(reqObj=self.__reqObj,verbose=self.__verbose,log=self.__lfh)
            prd.setFilePath(filePath,prdFileFormat=fileFormat,prdId=prdId)
            pD=prd.doReport()
            print pD
            print "-------------------"

            prdD=BirdReportDepict(verbose=self.__verbose,log=self.__lfh)
            oL=prdD.doRender(pD)
            self.__lfh.write("%s\n" % '\n'.join(oL))            

            
        except:
            traceback.print_exc(file=self.__lfh)
            self.fail()


def suite():
    return unittest.makeSuite(BirdReportTests,'test')

if __name__ == '__main__':
    unittest.main()

