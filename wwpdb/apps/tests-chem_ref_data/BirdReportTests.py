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
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import unittest
import os.path
import logging

if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from commonsetup import HERE  # noqa:  F401 pylint: disable=import-error,unused-import
else:
    from .commonsetup import HERE  # noqa: F401 pylint: disable=relative-beyond-top-level

try:
    from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId
    from wwpdb.apps.chem_ref_data.report.BirdReport import BirdReport
    from wwpdb.utils.session.WebRequest import InputRequest

    skiptests = False
except ImportError:
    skiptests = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@unittest.skipIf(skiptests, "Openeye import failed")
class BirdReportTests(unittest.TestCase):
    def setUp(self):
        self.__verbose = True
        self.__lfh = sys.stderr

        # Pick up site information from the environment or failover to the development site id.
        self.__siteId = getSiteId(defaultSiteId="WWPDB_DEV_TEST")
        logger.info("\nTesting with site environment for:  %s", self.__siteId)
        cI = ConfigInfo(self.__siteId)
        self.__topPath = cI.get("SITE_WEB_APPS_TOP_PATH")
        self.__topSessionPath = cI.get("SITE_WEB_APPS_TOP_SESSIONS_PATH")
        #
        # Create a request object and session directories for test cases
        #
        self.__reqObj = InputRequest(paramDict={}, verbose=self.__verbose, log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="text")
        self.__sobj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sobj.getPath()
        datadir = os.path.join(HERE, "data")
        self.__fileList = [(os.path.join(datadir, "FAM_000312.cif"), "FAM_000312"), (os.path.join(datadir, "FAM_000001.cif"), "FAM_000001")]

    def tearDown(self):
        pass

    def testReportFileOne(self):
        """ """
        logger.info("\n------------------------ ")
        logger.info("Starting test function  testReportFileOne")
        logger.info(" -------------------------")
        try:
            prdId = self.__fileList[0][1]
            fileFormat = "cif"
            filePath = self.__fileList[0][0]
            #
            logger.info("Session path is %s", self.__sessionPath)
            prd = BirdReport(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            prd.setFilePath(filePath, prdFileFormat=fileFormat, prdId=prdId)
            pD = prd.doReport()
            print("-------------------")
            print(pD)
            print("-------------------")

            # prdD=BirdReportDepict(verbose=self.__verbose,log=self.__lfh)
            # oL=prdD.doRender(pD)
            # logger.info("%s\n" % '\n'.join(oL))

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure")
            self.fail()


def suite():
    return unittest.makeSuite(BirdReportTests, "test")


if __name__ == "__main__":
    unittest.main()
