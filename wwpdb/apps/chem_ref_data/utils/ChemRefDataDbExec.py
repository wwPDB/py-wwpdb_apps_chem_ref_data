#!/usr/bin/env python
#!/opt/wwpdb/bin/python
##
# File:    ChemRefDataDbExec.py
# Author:  jdw
# Date:    13-Jul-2014
# Version: 0.001
#
# Updates:
##
"""
Execuction module for chemical reference data database loading --

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.001"

import sys
import os
import traceback
from optparse import OptionParser

from wwpdb.apps.chem_ref_data.utils.ChemRefDataDbUtils import ChemRefDataDbUtils
from wwpdb.apps.chem_ref_data.utils.ChemRefDataCvsUtils import ChemRefDataCvsUtils
from wwpdb.apps.chem_ref_data.utils.ChemRefDataMiscUtils import ChemRefDataMiscUtils
from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId
from wwpdb.utils.session.WebRequest import InputRequest


class ChemRefDataDbExec(object):

    def __init__(self, defSiteId='WWWDPB_INTERNAL_RU', sessionId=None, verbose=True, log=sys.stderr):
        self.__lfh = log
        self.__verbose = verbose
        self.__setup(defSiteId=defSiteId, sessionId=sessionId)

    def __setup(self, defSiteId=None, sessionId=None):
        """  Simulate the web application environment for managing session storage of  temporaty data files.
        """
        self.__siteId = getSiteId(defaultSiteId=defSiteId)
        print(self.__siteId)
        #
        self.__cI = ConfigInfo(self.__siteId)
        self.__topPath = self.__cI.get('SITE_WEB_APPS_TOP_PATH')
        self.__topSessionPath = self.__cI.get('SITE_WEB_APPS_TOP_SESSIONS_PATH')
        #
        self.__reqObj = InputRequest({}, verbose=self.__verbose, log=self.__lfh)
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TopPath", self.__topPath)
        self.__reqObj.setValue("WWPDB_SITE_ID", self.__siteId)
        #
        # self.__reqObj.setValue("SITE_REFDATA_DB_USER", os.environ["SITE_REFDATA_DB_USER"])
        # self.__reqObj.setValue("SITE_REFDATA_DB_PASSWORD", os.environ["SITE_REFDATA_DB_PASSWORD"])

        # self.__reqObj.setValue("SITE_REFDATA_CVS_USER", os.environ["SITE_REFDATA_CVS_USER"])
        # self.__reqObj.setValue("SITE_REFDATA_CVS_PASSWORD", os.environ["SITE_REFDATA_CVS_PASSWORD"])

        os.environ["WWPDB_SITE_ID"] = self.__siteId
        if sessionId is not None:
            self.__reqObj.setValue("sessionid", sessionId)

        self.__sessionId = self.__reqObj.getSessionId()
        self.__sessionObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sessionObj.getPath()
        # self.__reqObj.printIt(ofh=self.__lfh)
        #

    def doLoadChemComp(self, rptPath=None):
        """
        """
        try:
            dbu = ChemRefDataDbUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            dbu.loadChemComp()
        except:
            traceback.print_exc(file=self.__lfh)

    def doLoadChemCompMulti(self, numProc):
        """
        """
        try:
            dbu = ChemRefDataDbUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            dbu.loadChemCompMulti(numProc)
        except:
            traceback.print_exc(file=self.__lfh)

    def doLoadBird(self, rptPath=None):
        """
        """
        try:
            dbu = ChemRefDataDbUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            dbu.loadBird()
        except:
            traceback.print_exc(file=self.__lfh)

    def doCheckoutChemComp(self):
        """
        """
        try:
            cvsu = ChemRefDataCvsUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            sandbox_path = cvsu.getSandBoxTopPath()
            if sandbox_path:
                if not os.path.exists(sandbox_path):
                    os.makedirs(sandbox_path)
            cvsu.checkoutChemCompSerial()
        except:
            traceback.print_exc(file=self.__lfh)

    def doCheckoutPRD(self):
        try:
            cvsu = ChemRefDataCvsUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            sandbox_path = cvsu.getSandBoxTopPath()
            if sandbox_path:
                if not os.path.exists(sandbox_path):
                    os.makedirs(sandbox_path)
            cvsu.checkoutPRDSerial()
        except:
            traceback.print_exc(file=self.__lfh) 

    def doSyncChemComp(self, numProc):
        """
        """
        try:
            cvsu = ChemRefDataCvsUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            sandbox_path = cvsu.getSandBoxTopPath()
            if sandbox_path:
                if not os.path.exists(sandbox_path):
                    os.makedirs(sandbox_path)
            cvsu.syncChemComp(numProc)
        except:
            traceback.print_exc(file=self.__lfh)

    def doSyncBird(self):
        """
        """
        try:
            cvsu = ChemRefDataCvsUtils(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            sandbox_path = cvsu.getSandBoxTopPath()
            if sandbox_path:
                if not os.path.exists(sandbox_path):
                    os.makedirs(sandbox_path)
            cvsu.syncBird()
        except:
            traceback.print_exc(file=self.__lfh)

    def doUpdateSupportFiles(self):
        """Update chemical component definition file idList, pathList, concatenated dictionary,
        serialized dictionary, dictionary search index, and several Python serialized support files.
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        try:
            mu = ChemRefDataMiscUtils(self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            mu.updateChemCompSupportFiles()
            mu.updateChemCompPySupportFiles()
            mu.updatePrdSupportFiles()
        except:
            self.__lfh.write("\nFailed %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
            traceback.print_exc(file=self.__lfh)


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    parser.add_option("--load", dest="load", action='store_true', default=False, help="Load database from repository sandbox")
    parser.add_option("--sync", dest="sync", action='store_true', default=False, help="Synchronize repository sandbox")
    parser.add_option("--checkout", dest="checkout", action='store_true', default=False, help="Checkout repository into sandbox")
    parser.add_option("--update", dest="update", action='store_true', default=False, help="Update support files from repository sandbox")

    parser.add_option("--db", dest="db", default='PRD', help="Database to load (CC,PRD)")

    parser.add_option("--numproc", dest="numProc", default=8, help="Number of processors to engage.")

    parser.add_option("-v", "--verbose", default=False, action="store_true", dest="verbose")

    (options, args) = parser.parse_args()

    crx = ChemRefDataDbExec(defSiteId='WWWDPB_INTERNAL_RU', sessionId=None, verbose=options.verbose, log=sys.stderr)

    if options.checkout:
        if options.db == 'CC':
            crx.doCheckoutChemComp()
        if options.db == 'PRD':
            crx.doCheckoutPRD()

    if options.sync:
        if options.db == 'CC':
            crx.doSyncChemComp(options.numProc)
        elif options.db == 'PRD':
            crx.doSyncBird()

    if options.load:
        if options.db == 'CC':
            crx.doLoadChemCompMulti(options.numProc)
        elif options.db == 'PRD':
            crx.doLoadBird()

    if options.update:
        crx.doUpdateSupportFiles()

if __name__ == '__main__':
    main()
