##
# File:  ChemRefDataDbUtils.py
# Date:  24-Jan-2013  J. Westbrook
#
# Updated:
#  4-Feb-2013  jdw generalized for BIRD and chemical component database loading.
# 14-Aug-2013  jdw misc updates
# 11-Nov-2014  jdw add multiprocessing loader for chemical component data -
#  1-Feb-2017  jdw change base class
#
"""
Wrapper for utilities for database loading of chemical reference data content from
repositories and sandboxes.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import sys
import os
import os.path
import time
import scandir
import traceback
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from wwpdb.utils.config.ConfigInfo import ConfigInfo
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoApp
from wwpdb.utils.db.MyDbSqlGen import MyDbAdminSqlGen
from wwpdb.utils.db.SchemaDefLoader import SchemaDefLoader
from wwpdb.utils.db.MyDbUtil import MyDbQuery

from rcsb.utils.multiproc.MultiProcUtil import MultiProcUtil

from wwpdb.utils.db.BirdSchemaDef import BirdSchemaDef
from wwpdb.utils.db.ChemCompSchemaDef import ChemCompSchemaDef

from mmcif_utils.bird.PdbxPrdIo import PdbxPrdIo
from mmcif_utils.bird.PdbxFamilyIo import PdbxFamilyIo
from mmcif_utils.bird.PdbxPrdUtils import PdbxPrdUtils

from mmcif_utils.chemcomp.PdbxChemCompIo import PdbxChemCompIo

# from mmcif.io.IoAdapterPy       import IoAdapterPy
from mmcif.io.IoAdapterCore import IoAdapterCore

from wwpdb.utils.db.MyConnectionBase import MyConnectionBase


class ChemRefDataDbUtils(MyConnectionBase):
    """ Wrapper for utilities for database loading of content from PRD repositories and sandboxes.
    """
    #

    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__siteId = self.__reqObj.getValue("WWPDB_SITE_ID")
        #
        super(ChemRefDataDbUtils, self).__init__(siteId=self.__siteId, verbose=verbose, log=log)
        """
        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = verbose
        #
        # Information injected from the request object -
        #
        self.__topPath = self.__reqObj.getValue("TopPath")
        self.__topSessioPath = self.__reqObj.getValue("TopSessionPath")
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        self.__sessionRelativePath = self.__sObj.getRelativePath()
        self.__sessionId = self.__sObj.getId()
        #

        self.__ioObj = IoAdapterCore(verbose=self.__verbose, log=self.__lfh)
        #
        self.__siteId = self.__reqObj.getValue("WWPDB_SITE_ID")
        self.__cI = ConfigInfo(self.__siteId)
        self.__cICommon = ConfigInfoApp(self.__siteId)
        self.__sbTopPath = self.__cICommon.get_site_refdata_top_cvs_sb_path()
        self.__projName = self.__cI.get('SITE_REFDATA_PROJ_NAME_CC')

    def loadBird(self):
        """  Load database containing BIRD PRD and PRD Family data.  Materialized some sequence
             details prior to load.
        """
        startTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(loadBird) Starting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name,
                                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            birdCachePath = self.__cICommon.get_site_prd_cvs_path()
            birdFamilyCachePath = self.__cICommon.get_site_family_cvs_path()
            #
            #
            prd = PdbxPrdIo(verbose=self.__verbose, log=self.__lfh)
            prd.setCachePath(birdCachePath)
            self.__pathList = prd.makeDefinitionPathList()
            #
            for pth in self.__pathList:
                prd.setFilePath(pth)
            if self.__verbose:
                self.__lfh.write("+ChemRefDataLoad(loadBird) PRD repository read completed\n")
            #
            prdU = PdbxPrdUtils(prd, verbose=self.__verbose, log=self.__lfh)
            rD = prdU.getComponentSequences(addCategory=True)
            #
            #
            prdFam = PdbxFamilyIo(verbose=self.__verbose, log=self.__lfh)
            prdFam.setCachePath(birdFamilyCachePath)
            self.__familyPathList = prdFam.makeDefinitionPathList()
            #
            for pth in self.__familyPathList:
                prdFam.setFilePath(pth)
            if self.__verbose:
                self.__lfh.write("+ChemRefDataLoad(loadBird) Family repository read completed\n")
            #
            # Combine containers -
            containerList = prd.getCurrentContainerList()
            containerList.extend(prdFam.getCurrentContainerList())
            #
            # Run loader on container list --
            #
            self.setResource(resourceName="PRD")
            ok = self.openConnection()
            if ok:
                sd = BirdSchemaDef()
                self.__schemaCreate(schemaDefObj=sd)

                sdl = SchemaDefLoader(schemaDefObj=sd, ioObj=self.__ioObj, dbCon=self._dbCon, workPath=self.__sessionPath,
                                      cleanUp=False, warnings='error', verbose=self.__verbose, log=self.__lfh)
                ok = sdl.load(containerList=containerList, loadType='batch-file', deleteOpt='truncate')

                self.closeConnection()
            else:
                if self.__verbose:
                    self.__lfh.write("+ChemRefDataLoad(loadBird) database connection failed\n")

        except:
            self.closeConnection()
            traceback.print_exc(file=self.__lfh)
            ok = False

        endTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(loadBird) Completed %s %s at %s (%.4f seconds)\n" % (self.__class__.__name__,
                                                                                                  sys._getframe().f_code.co_name,
                                                                                                  time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                                                  endTime - startTime))
        return ok

    def loadChemComp(self):
        startTime = time.time()
        self.__lfh.write("\n+ChemRefDataDbUtils(loadChemComp) Starting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name,
                                                                                         time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            chemCompCachePath = self.__cICommon.get_site_cc_cvs_path()
            #
            cc = PdbxChemCompIo(verbose=self.__verbose, log=self.__lfh)
            cc.setCachePath(chemCompCachePath)
            self.__pathList = cc.makeComponentPathList()
            #
            for pth in self.__pathList:
                cc.setFilePath(pth)

            containerList = cc.getCurrentContainerList()
            if self.__verbose:
                self.__lfh.write("+ChemRefDataDbUtils(loadChemComp) Reading definitions in chemical component repository read completed length %r\n" % len(containerList))

            # --------------------------------------------------
            # Create schema and run loader on container list --
            #
            self.setResource(resourceName="CC")
            ok = self.openConnection()
            if ok:
                sd = ChemCompSchemaDef()
                self.__schemaCreate(schemaDefObj=sd)
                #
                # sdl=SchemaDefLoader(schemaDefObj=sd,ioObj=self.__ioObj,dbCon=self._dbCon,workPath='.',
                #                cleanUp=False,warnings='error',verbose=self.__verbose,log=self.__lfh)
                sdl = SchemaDefLoader(schemaDefObj=sd, ioObj=self.__ioObj, dbCon=self._dbCon, workPath=self.__sessionPath,
                                      cleanUp=False, warnings='error', verbose=self.__verbose, log=self.__lfh)
                ok = sdl.load(containerList=containerList, loadType='batch-file', deleteOpt='truncate')
                self.closeConnection()
            else:
                if self.__verbose:
                    self.__lfh.write("+ChemRefDataDbUtils(loadChemComp) database connection failed\n")

        except:
            self.closeConnection()
            traceback.print_exc(file=self.__lfh)
            ok = False

        endTime = time.time()
        self.__lfh.write("\n+ChemRefDataDbUtils(loadChemComp) Completed %s %s at %s (%.4f seconds)\n" % (self.__class__.__name__,
                                                                                                         sys._getframe().f_code.co_name,
                                                                                                         time.strftime("%Y %m %d %H:%M:%S", time.localtime()),                                                                                                         endTime - startTime))
        return ok

    def __schemaCreate(self, schemaDefObj):
        """Create and load table schema using schema definition
        """
        startTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(__schemaCreate) Starting %s %s at %s\n" % (self.__class__.__name__,
                                                                                        sys._getframe().f_code.co_name,
                                                                                        time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            tableIdList = schemaDefObj.getTableIdList()
            sqlGen = MyDbAdminSqlGen(self.__verbose, self.__lfh)
            sqlL = []
            for tableId in tableIdList:
                tableDefObj = schemaDefObj.getTable(tableId)
                sqlL.extend(sqlGen.createTableSQL(databaseName=schemaDefObj.getDatabaseName(), tableDefObj=tableDefObj))

            if (self.__debug):
                self.__lfh.write("\n+ChemRefDataLoad(__schemaCreate) Schema creation SQL string\n %s\n\n" % '\n'.join(sqlL))

            myQ = MyDbQuery(dbcon=self._dbCon, verbose=self.__verbose, log=self.__lfh)
            #
            # Permit warnings to support "drop table if exists" for missing tables.
            #
            myQ.setWarning('default')
            ret = myQ.sqlCommand(sqlCommandList=sqlL)
            if (self.__verbose):
                self.__lfh.write("\n\n+INFO mysql server returns %r\n" % ret)
        except:
            traceback.print_exc(file=self.__lfh)
            return False

        endTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(__schemaCreate) Completed %s %s at %s (%.2f seconds)\n" % (self.__class__.__name__,
                                                                                                        sys._getframe().f_code.co_name,
                                                                                                        time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                                                        endTime - startTime))
        return ret

    def __makeSubLists(self, n, iterable):
        args = [iter(iterable)] * n
        return ([e for e in t if e is not None] for t in zip_longest(*args))


    def makeComponentPathListMulti(self, dataList, procName, optionsD, workingDir):
        """ Return the list of chemical component definition file paths in the current repository.
        """
        pathList = []
        for subdir in dataList:
            dd = os.path.join(self.__sbTopPath, self.__projName, subdir)
            for root, dirs, files in scandir.walk(dd, topdown=False):
                if "REMOVE" in root:
                    continue
                for name in files:
                    if name.endswith(".cif") and len(name) <= 7:
                        pathList.append(os.path.join(root, name))

        return dataList, pathList, []

    def loadChemCompMulti(self, numProc=8):
        """ Create batch load files for all chemical component definition data files - (multiprocessing for file generation only)
        """
        if self.__verbose:
            self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()
        try:
            dataS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            dataList = [a for a in dataS]
            mpu = MultiProcUtil(verbose=True)
            mpu.set(workerObj=self, workerMethod="makeComponentPathListMulti")
            ok, failList, retLists, diagList = mpu.runMulti(dataList=dataList, numProc=numProc, numResults=1)
            pathList = retLists[0]
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nPath list length %d  in %.2f seconds\n" % (len(pathList), endTime0 - startTime))

            ccsd = ChemCompSchemaDef()
            sml = SchemaDefLoader(schemaDefObj=ccsd, ioObj=self.__ioObj, dbCon=None, workPath=self.__sessionPath, cleanUp=False,
                                  warnings='default', verbose=self.__verbose, log=self.__lfh)

            #
            mpu = MultiProcUtil(verbose=True)
            mpu.set(workerObj=sml, workerMethod="makeLoadFilesMulti")
            mpu.setWorkingDir(self.__sessionPath)
            ok, failList, retLists, diagList = mpu.runMulti(dataList=pathList, numProc=numProc, numResults=2)
            #
            #containerNameList = retLists[0]
            tList = retLists[1]

            if self.__verbose:
                for tId, fn in tList:
                    self.__lfh.write("\nCreated table %s load file %s\n" % (tId, fn))
            #
            endTime1 = time.time()
            if self.__verbose:
                self.__lfh.write("\nBatch files %r created in %.4f seconds\n" % (len(tList), endTime1 - endTime0))

            #
            # --------------------------------------------------
            #               Recreate schema
            #
            self.setResource(resourceName="CC")
            ok = self.openConnection()
            if ok:
                # sd = ChemCompSchemaDef()
                self.__schemaCreate(schemaDefObj=ccsd)
                self.closeConnection()
            else:
                if self.__verbose:
                    self.__lfh.write("+ChemRefDataDbUtils(loadChemCompMulti) database connection failed\n")
                return False
            #
            #
            self.setResource(resourceName="CC")
            ok = self.openConnection()
            #
            sdl = SchemaDefLoader(schemaDefObj=ccsd, ioObj=self.__ioObj, dbCon=self._dbCon, workPath=self.__sessionPath, cleanUp=False,
                                  warnings='default', verbose=self.__verbose, log=self.__lfh)

            ok = sdl.loadBatchFiles(loadList=tList, containerNameList=None, deleteOpt=None)
            self.closeConnection()

            # --------------------------------------------------
            endTime2 = time.time()
            if self.__verbose:
                self.__lfh.write("\nLoad completed in %.4f seconds\n" % (endTime2 - endTime1))
            return ok
        except:
            traceback.print_exc(file=self.__lfh)
            return False

        endTime = time.time()
        self.__lfh.write("\nCompleted %s %s at %s (%.4f seconds)\n" % (self.__class__.__name__,
                                                                       sys._getframe().f_code.co_name,
                                                                       time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                       endTime2 - startTime))
