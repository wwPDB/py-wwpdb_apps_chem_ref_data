##
#
# File:    ChemCompSearchIndexUtilsTests.py
# Author:  J. Westbrook
# Date:    1-Feb-2017
# Version: 0.001
#
# Updates:
#
##
"""
Test cases for ChemCompSearchIndexUtils demonstrating formula searchs.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import unittest
import time
import os
import logging

if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from commonsetup import HERE  # noqa:  F401 pylint: disable=import-error,unused-import
else:
    from .commonsetup import HERE  # noqa: F401 pylint: disable=relative-beyond-top-level

from wwpdb.apps.chem_ref_data.search.ChemCompSearchIndexUtils import ChemCompSearchIndexUtils
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon
from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId
from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils
from wwpdb.utils.session.WebRequest import InputRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)


class ChemCompSearchIndexUtilsTests(unittest.TestCase):
    def setUp(self):
        self.__lfh = sys.stderr
        self.__siteId = None
        self.__verbose = True
        #
        self.__cc_index = ConfigInfoAppCommon().get_cc_index()

        #
        # Create a request object and session directories for test cases
        #
        self.__cI = ConfigInfo(self.__siteId)
        self.__siteId = getSiteId(defaultSiteId="WWPDB_DEPLOY_TEST_RU")
        self.__topPath = self.__cI.get("SITE_WEB_APPS_TOP_PATH")
        self.__topSessionPath = self.__cI.get("SITE_WEB_APPS_TOP_SESSIONS_PATH")
        self.__reqObj = InputRequest(paramDict={}, verbose=self.__verbose, log=self.__lfh)
        self.__reqObj.setValue("WWPDB_SITE_ID", self.__siteId)
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setDefaultReturnFormat(return_format="html")

    def tearDown(self):
        pass

    def testCreateIndex(self):
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # Generate combined file - skip index and sdb generation
        ok = mu.updateChemCompSupportFiles(skipIndex=True)
        self.assertTrue(ok)
        ok = mu.updateChemCompPySupportFiles()

    def testIndexSearchRange(self):
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        ky = "formulaWeight"
        vl = "10 20"
        rD = ccsi.searchIndexRange(vl, ky)
        logger.info("Key %r search result length %r", ky, len(rD))
        self.assertTrue(len(rD) > 0, "IndexSearchRange failed: %s: %s" % (ky, vl))

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)

    def testIndexSearchAll(self):
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        for ky in ["InChIKey14"]:
            rD = ccsi.searchIndexAll(ky)
            logger.info("Key %r search result length %r", ky, len(rD))
            self.assertTrue(len(rD) > 0, "IndexSearchAll: %s" % ky)

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)

    def testTautomerSearch(self):
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        ccIdList = ["atp", "gtp", "ala", "gly"]
        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        for ccId in ccIdList:
            ik = ccsi.getValue(ccId, "InChIKey")
            if ik is not None:
                mL = ccsi.searchIndex(ik, "InChIKey")
                logger.info("Index search %r %r result length %r", ccId, ik, len(mL))
                self.assertTrue(len(mL) > 0, "Tautomer search failed")

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)

    def testIsomerSearch(self):
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        ccIdList = ["atp", "gtp", "ala", "gly"]
        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        for ccId in ccIdList:
            smi = ccsi.getValue(ccId, "smiles")
            if smi is not None:
                mL = ccsi.searchIndex(smi, "smiles")
                logger.info("Index search %r %r result length %r", ccId, smi, len(mL))
                self.assertTrue(len(mL) > 0, "Isomer Search Failed %s")

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)

    def testBoundedFormulaSearch1(self):
        """Test case -  bounded formula search of index file with element count dictionary input"""
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        formulaD = {"t1": {"C": 16, "O": 2}, "t2": {"C": 14, "O": 4}, "t3": {"C": 12, "N": 1, "Cl": 2}}
        #
        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        for _sId, eD in formulaD.items():
            mL = ccsi.searchFormulaBounded(elementCounts=eD)
            logger.info("Search %r result length %r", eD, len(mL))
            self.assertTrue(len(mL) > 0, "Must have one result at least for bounded search")

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)

    def testBoundedFormulaSearch2(self):
        """Test case -  bounded formula search of index file with formula string input"""
        if not os.path.exists(self.__cc_index):
            self.testCreateIndex()

        startTime = time.time()
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        formulaL = ["c10", "ru n2", "C16 o2", "c12 n1 cl2"]

        #
        ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
        for formula in formulaL:
            tf, eD = ccsi.parseFormulaInput(formula)
            mL = ccsi.searchFormulaBounded(elementCounts=eD)
            logger.info("Search %r %r result length %r", tf, eD, len(mL))
            self.assertTrue(len(mL) > 0, "Must have one result at least for boundedformualsearch2 search %s" % formula)

        endTime = time.time()
        logger.info("Completed at %s (%.3f seconds)", time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - startTime)


def suiteChemCompSearchIndexAll():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testIndexSearchAll"))
    return suiteSelect


def suiteChemCompSearchIndexRange():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testIndexSearchRange"))
    return suiteSelect


def suiteChemCompSearchIndex():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testBoundedFormulaSearch1"))
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testBoundedFormulaSearch2"))
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testTautomerSearch"))
    suiteSelect.addTest(ChemCompSearchIndexUtilsTests("testIsomerSearch"))
    return suiteSelect


if __name__ == "__main__":
    #
    if True:  # pylint: disable=using-constant-test
        mySuite1 = suiteChemCompSearchIndex()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
    if False:  # pylint: disable=using-constant-test
        mySuite1 = suiteChemCompSearchIndexAll()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)

    #
    if True:  # pylint: disable=using-constant-test
        mySuite1 = suiteChemCompSearchIndexRange()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
