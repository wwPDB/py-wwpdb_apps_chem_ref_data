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
import traceback
import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


from wwpdb.apps.chem_ref_data.search.ChemCompSearchIndexUtils import ChemCompSearchIndexUtils


class ChemCompSearchIndexUtilsTests(unittest.TestCase):

    def setUp(self):
        self.__lfh = sys.stderr
        self.__siteId = None
        self.__verbose = True
        self.__debug = True
        #
        # Should exist from a previous test case --

    def tearDown(self):
        pass

    def testIndexSearchRange(self):
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            ky = 'formulaWeight'
            vl = '10 20'
            rD = ccsi.searchIndexRange(vl, ky)
            logger.info("Key %r search result length %r\n" % (ky, len(rD)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))

    def testIndexSearchAll(self):
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            for ky in ['InChIKey14']:
                rD = ccsi.searchIndexAll(ky)
                logger.info("Key %r search result length %r\n" % (ky, len(rD)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))

    def testTautomerSearch(self):
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccIdList = ["atp", "gtp", "ala", "gly"]
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            for ccId in ccIdList:
                ik = ccsi.getValue(ccId, 'InChIKey')
                if ik is not None:
                    mL = ccsi.searchIndex(ik, 'InChIKey')
                    logger.info("Index search %r %r result length %r\n" % (ccId, ik, len(mL)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))

    def testIsomerSearch(self):
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccIdList = ["atp", "gtp", "ala", "gly"]
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            for ccId in ccIdList:
                smi = ccsi.getValue(ccId, 'smiles')
                if smi is not None:
                    mL = ccsi.searchIndex(smi, 'smiles')
                    logger.info("Index search %r %r result length %r\n" % (ccId, smi, len(mL)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))

    def testBoundedFormulaSearch1(self):
        """Test case -  bounded formula search of index file with element count dictionary input

        """
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            formulaD = {'t1': {'C': 16, 'O': 2}, 't2': {'C': 14, 'O': 4}, 't3': {'C': 12, 'N': 1, 'Cl': 2}}
            #
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            for sId, eD in formulaD.items():
                mL = ccsi.searchFormulaBounded(elementCounts=eD)
                logger.info("Search %r result length %r\n" % (eD, len(mL)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))

    def testBoundedFormulaSearch2(self):
        """Test case -  bounded formula search of index file with formula string input

        """
        startTime = time.time()
        logger.info("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                  sys._getframe().f_code.co_name,
                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            formulaL = ['c10', 'ru n2', 'C16 o2', 'c12 n1 cl2']

            #
            ccsi = ChemCompSearchIndexUtils(siteId=self.__siteId, verbose=self.__verbose, log=self.__lfh)
            for formula in formulaL:
                tf, eD = ccsi.parseFormulaInput(formula)
                mL = ccsi.searchFormulaBounded(elementCounts=eD)
                logger.info("Search %r %r result length %r\n" % (tf, eD, len(mL)))
        except Exception as e:
            logger.exception("Error '{0}' occured. Arguments {1}.".format(e.message, e.args))
            self.fail()

        endTime = time.time()
        logger.info("\nCompleted %s %s at %s (%.3f seconds)\n" % (self.__class__.__name__,
                                                                  sys._getframe().f_code.co_name,
                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                  endTime - startTime))


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


if __name__ == '__main__':
    #
    if (True):
        mySuite1 = suiteChemCompSearchIndex()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
    if (False):
        mySuite1 = suiteChemCompSearchIndexAll()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)

    #
    if (True):
        mySuite1 = suiteChemCompSearchIndexRange()
        unittest.TextTestRunner(verbosity=2).run(mySuite1)
    #
