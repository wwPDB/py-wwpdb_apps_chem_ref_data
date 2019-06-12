##
# File:  ChemRefDataMiscUtils.py
# Date:  16-Mar-2016  Migrated from cc_dict_utils  - J. Westbrook
#
# Updated:
#  18-Mar-2016  jdw adjust mode on data products to g+rw
#  18-Mar-2016  jdw add extra newline between concatenated components
#
"""
Wrapper for utilities for creating and maintaining various resource files containing
chemical reference data content stored in repositories and sandboxes.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import sys
import os
import os.path
import shutil
import time
import copy
import scandir
import traceback
import filecmp
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
import string
import fnmatch

from wwpdb.utils.config.ConfigInfo import ConfigInfo

from rcsb.utils.multiproc.MultiProcUtil import MultiProcUtil

from mmcif_utils.bird.PdbxPrdIo import PdbxPrdIo
from mmcif_utils.bird.PdbxPrdCcIo import PdbxPrdCcIo
from mmcif_utils.bird.PdbxFamilyIo import PdbxFamilyIo
from mmcif_utils.bird.PdbxPrdUtils import PdbxPrdUtils

from mmcif_utils.chemcomp.PdbxChemCompIo import PdbxChemCompIo

# from mmcif.io.IoAdapterPy       import IoAdapterPy
from mmcif.io.IoAdapterCore import IoAdapterCore
from wwpdb.utils.dp.RcsbDpUtility import RcsbDpUtility
from wwpdb.io.file.DataFile import DataFile

from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictUtil import PdbxChemCompDictUtil
from wwpdb.utils.cc_dict_util.persist.PdbxChemCompDictIndex import PdbxChemCompDictIndex


class ChemRefDataMiscUtils(object):
    """ Wrapper for utilities for creating and maintaining various resource files containing
       chemical reference data content stored in repositories and sandboxes.
    """

    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        """
        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        #
        # Information injected from the request object -
        #
        self.__reqObj = reqObj
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
        self.__sbTopPath = self.__cI.get('SITE_REFDATA_TOP_CVS_SB_PATH')
        self.__projName = self.__cI.get('SITE_REFDATA_PROJ_NAME_CC')
        self.__ccDictPath = self.__cI.get('SITE_CC_DICT_PATH')
        #
        self.__pathCCDict = os.path.join(self.__ccDictPath, "Components-all-v3.cif")
        self.__pathCCPathList = os.path.join(self.__ccDictPath, "PATHLIST-v3")
        self.__pathCCIdList = os.path.join(self.__ccDictPath, "IDLIST-v3")
        self.__pathCCDictSerial = os.path.join(self.__ccDictPath, "Components-all-v3.sdb")
        self.__pathCCDictIdx = os.path.join(self.__ccDictPath, "Components-all-v3-r4.idx")
        #
        self.__pathCCDb = os.path.join(self.__ccDictPath, "chemcomp.db")
        self.__pathCCIndex = os.path.join(self.__ccDictPath, "chemcomp-index.pic")
        self.__pathCCParentIndex = os.path.join(self.__ccDictPath, "chemcomp-parent-index.pic")

        self.__pathPrdChemCompCVS = self.__cI.get('SITE_PRDCC_CVS_PATH')
        self.__pathPrdDictRef = os.path.join(self.__sbTopPath, 'prd-dict')
        self.__pathPrdDictFile = os.path.join(self.__pathPrdDictRef, "Prd-all-v3.cif")
        self.__pathPrdDictSerial = os.path.join(self.__pathPrdDictRef, "Prd-all-v3.sdb")
        self.__pathPrdCcFile = os.path.join(self.__pathPrdDictRef, "Prdcc-all-v3.cif")
        self.__pathPrdCcSerial = os.path.join(self.__pathPrdDictRef, "Prdcc-all-v3.sdb")
        self.__pathPrdSummary = os.path.join(self.__pathPrdDictRef, "prd_summary.cif")
        self.__pathPrdSummarySerial = os.path.join(self.__pathPrdDictRef, "prd_summary.sdb")
        self.__pathPrdFamilyMapping = os.path.join(self.__pathPrdDictRef, "PrdFamilyIDMapping.lst")
        #

    def getBirdPathList(self):
        """  Get pathlist for BIRD PRD and PRD Family data.
        """
        startTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(getBirdPathList) Starting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name,
                                                                                         time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            sbTopPath = self.__sbTopPath
            projNamePrd = self.__cI.get('SITE_REFDATA_PROJ_NAME_PRD')
            projNamePrdFamily = self.__cI.get('SITE_REFDATA_PROJ_NAME_PRD_FAMILY')
            projNamePrdCC = self.__cI.get('SITE_REFDATA_PROJ_NAME_PRDCC')
            #
            birdCachePath = os.path.join(sbTopPath, projNamePrd)
            birdFamilyCachePath = os.path.join(sbTopPath, projNamePrdFamily)
            birdCcCachePath = os.path.join(sbTopPath, projNamePrdCC)
            #
            #
            prd = PdbxPrdIo(verbose=self.__verbose, log=self.__lfh)
            prd.setCachePath(birdCachePath)
            pathList = prd.makeDefinitionPathList()
            #
            prdFam = PdbxFamilyIo(verbose=self.__verbose, log=self.__lfh)
            prdFam.setCachePath(birdFamilyCachePath)
            familyPathList = prdFam.makeDefinitionPathList()
            #
            prdCc = PdbxPrdCcIo(verbose=self.__verbose, log=self.__lfh)
            prdCc.setCachePath(birdCcCachePath)
            prdCcPathList = prdCc.makeDefinitionPathList()
            #
            return pathList, familyPathList, prdCcPathList
        except:
            traceback.print_exc(file=self.__lfh)

        endTime = time.time()
        self.__lfh.write("\n+ChemRefDataLoad(getBirdPathList) Completed %s %s at %s\n" % (self.__class__.__name__,
                                                                                          sys._getframe().f_code.co_name,
                                                                                          time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        return [], [], []

    def __makeTempPath(self, inpPath):
        try:
            pid = str(os.getpid())
            return inpPath + pid
        except:
            return inpPath

    def writeList(self, myList, outPath, mode=0o664):
        """
        """
        try:
            tPath = self.__makeTempPath(outPath)
            ofh = open(tPath, 'w')
            for el in myList:
                ofh.write("%s\n" % el)
            ofh.close()
            os.chmod(tPath, 0o664)
            shutil.move(tPath, outPath)
            return True
        except:
            return False

    def concatPathList(self, pathList, outPath, mode=0o664):
        """
        """
        (ok, update) = self.concatPathListExt(pathList, outPath, mode)
        return ok

    def concatPathListExt(self, pathList, outPath, mode=0o664, avoidUpdate = False):
        """
        Concatenates files in pathList. If avoidUpdate is set, compare temporary file
        vs. destination.

        Returns (status, updated) - status if concatenation good. If True, updated will be 
        set of file moved into place.
        """
        try:
            tPath = self.__makeTempPath(outPath)
            with open(tPath, "wb") as outfile:
                for f in pathList:
                    with open(f, "rb") as infile:
                        outfile.write(infile.read())
                        # to handle missing trailing newlines =
                        outfile.write("\n")
            os.chmod(tPath, 0o664)

            if avoidUpdate and os.path.exists(outPath):
                if filecmp.cmp(tPath, outPath, shallow=False):
                    os.unlink(tPath)
                    return(True, False)

            shutil.move(tPath, outPath)
            return (True, True)
        except:
            traceback.print_exc(file=sys.stderr)
            return (False, False)


    def updateChemCompSupportFiles(self, idMaxLen=3, numProc=4):
        """  Create full idlist, pathlist, concatenated chemical component dictionary file,
        serialized dictionary, and dictionary index.
        """
        ok1 = ok2 = ok3 = False
        pathList = self.getChemCompPathListMulti(numProc=numProc)
        idList = []
        for pth in pathList:
            (dn, fn) = os.path.split(pth)
            (ccId, ext) = os.path.splitext(fn)
            if ((len(ccId) <= idMaxLen) and (ext == '.cif')):
                idList.append(ccId)
        self.writeList(idList, self.__pathCCIdList)
        self.writeList(pathList, self.__pathCCPathList)
        ok1 = self.concatPathList(pathList, self.__pathCCDict)
        #
        ok2 = self.__serializeDictOp()
        ok3 = self.__indexDictOp()
        return ok1 and ok2 and ok3

    def updateChemCompPySupportFiles(self):
        """Create BSD DB of full chemical component dictionary, PRD CC files, index and parent index pickle files.
        """
        ok = False
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                       sys._getframe().f_code.co_name,
                                                       time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            dU = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            ok = dU.makeStoreFromFile(dictPath=self.__pathCCDict, storePath=self.__pathCCDb)
            ok = self.updatePrdCCFiles()
            if ok:
                dIndx = PdbxChemCompDictIndex(verbose=self.__verbose, log=self.__lfh)
                dIndx.makeIndex(storePath=self.__pathCCDb, indexPath=self.__pathCCIndex)
                pD, cD = dIndx.makeParentComponentIndex(storePath=self.__pathCCDb, indexPath=self.__pathCCParentIndex)
                ok = True
            else:
                ok = False
        except:
            traceback.print_exc(file=self.__lfh)
            ok = False

        endTime = time.time()
        self.__lfh.write("\nCompleted %s %s at %s (%d seconds)\n" % (self.__class__.__name__,
                                                                     sys._getframe().f_code.co_name,
                                                                     time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                     endTime - startTime))
        return ok

    def __getPathList(self, topPath, pattern='*', excludeDirs=[], recurse=True):
        """ Return a list of file paths in the input topPath which satisfy the input search criteria.

            This version does not follow symbolic links.
        """
        pathList = []
        #
        try:
            names = os.listdir(topPath)
        except os.error:
            return pathList

        # expand pattern
        pattern = pattern or '*'
        patternList = string.splitfields(pattern, ';')

        for name in names:
            fullname = os.path.normpath(os.path.join(topPath, name))
            # check for matching files
            for pat in patternList:
                if fnmatch.fnmatch(name, pat):
                    if os.path.isfile(fullname):
                        pathList.append(fullname)
                        continue
            if recurse:
                # recursively scan directories
                if os.path.isdir(fullname) and not os.path.islink(fullname) and (name not in excludeDirs):
                    pathList.extend(self.__getPathList(topPath=fullname, pattern=pattern, excludeDirs=excludeDirs, recurse=recurse))

        return pathList

    def updatePrdCCFiles(self):
        """Update persistent store from a path list of PRD chemical component defintions.
        """
        ok = False
        startTime = time.time()
        self.__lfh.write("\nStarting %s %s at %s\n" % (self.__class__.__name__,
                                                       sys._getframe().f_code.co_name,
                                                       time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            ccPathList = self.__getPathList(topPath=self.__pathPrdChemCompCVS, pattern="*.cif", excludeDirs=['CVS', 'REMOVED', 'FULL'])
            if (self.__verbose):
                self.__lfh.write("PRD CC pathlist length is %d\n" % len(ccPathList))
            #
            dUtil = PdbxChemCompDictUtil(verbose=self.__verbose, log=self.__lfh)
            dUtil.updateStoreByFile(pathList=ccPathList, storePath=self.__pathCCDb)
            ok = True
            #
        except:
            traceback.print_exc(file=self.__lfh)

        endTime = time.time()
        self.__lfh.write("\nCompleted %s %s at %s (%d seconds)\n" % (self.__class__.__name__,
                                                                     sys._getframe().f_code.co_name,
                                                                     time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                     endTime - startTime))
        return ok

    def __indexDictOp(self, minSize=10):
        """  Make chemical component dictionary index from serialized dictionary.
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()
        try:
            outPathTmp = self.__makeTempPath(self.__pathCCDictIdx)
            inpPath = self.__pathCCDictSerial
            logPath = os.path.join(self.__ccDictPath, "chem-comp-dict-makeindex.log")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose)
            #
            dp.setDebugMode(flag=self.__debug)
            dp.imp(inpPath)
            dp.op("chem-comp-dict-makeindex")
            dp.expLog(logPath)
            dp.exp(outPathTmp)
            fSize = dp.expSize()
            if fSize > minSize:
                os.chmod(outPathTmp, 0o664)
                shutil.move(outPathTmp, self.__pathCCDictIdx)
                os.chmod(self.__pathCCDictIdx, 0o664)
                ok = True
            else:
                ok = False
            if not self.__debug:
                dp.cleanup()
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nDictionary index file size %d  in %.2f seconds\n" % (fSize, endTime0 - startTime))
            return ok
        except:
            traceback.print_exc(file=self.__lfh)
        return False

    def __serializeDictOp(self, minSize=10):
        """  Serialize chemical component dictionary from concatenated dictionary text.
        """
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()
        try:
            outPathTmp = self.__makeTempPath(self.__pathCCDictSerial)
            inpPath = self.__pathCCDict
            logPath = os.path.join(self.__ccDictPath, "chem-comp-dict-serialize.log")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose)
            #
            dp.setDebugMode(flag=self.__debug)
            dp.imp(inpPath)
            dp.op("chem-comp-dict-serialize")
            dp.expLog(logPath)
            dp.exp(outPathTmp)
            fSize = dp.expSize()
            if fSize > minSize:
                os.chmod(outPathTmp, 0o664)
                shutil.move(outPathTmp, self.__pathCCDictSerial)
                os.chmod(self.__pathCCDictSerial, 0o664)
                ok = True
            else:
                ok = False
            if not self.__debug:
                dp.cleanup()
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nSerialized dictionary file size %d  in %.2f seconds\n" % (fSize, endTime0 - startTime))
            return ok
        except:
            traceback.print_exc(file=self.__lfh)
        return False

    def getChemCompPathList(self):
        startTime = time.time()
        self.__lfh.write("\n+ChemRefDataDbUtils(getChemCompPathList) Starting %s %s at %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name,
                                                                                                time.strftime("%Y %m %d %H:%M:%S", time.localtime())))
        try:
            sbTopPath = self.__cI.get('SITE_REFDATA_TOP_CVS_SB_PATH')
            projNameChemComp = self.__cI.get('SITE_REFDATA_PROJ_NAME_CC')
            chemCompCachePath = os.path.join(sbTopPath, projNameChemComp)
            #
            #
            cc = PdbxChemCompIo(verbose=self.__verbose, log=self.__lfh)
            cc.setCachePath(chemCompCachePath)
            pathList = cc.makeComponentPathList()
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nPath list length %d  in %.2f seconds\n" % (len(pathList), endTime0 - startTime))
            return pathList
        except:
            traceback.print_exc(file=self.__lfh)

        endTime = time.time()
        self.__lfh.write("\n+ChemRefDataDbUtils(getChemCompPathList) Completed %s %s at %s (%.2f seconds)\n" % (self.__class__.__name__,
                                                                                                                sys._getframe().f_code.co_name,
                                                                                                                time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                                                                endTime - startTime))
        return []

    def __makeSubLists(self, n, iterable):
        args = [iter(iterable)] * n
        return ([e for e in t if e is not None] for t in zip_longest(*args))

    def _makeComponentPathListMulti(self, dataList, procName, optionsD, workingDir):
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

    def getChemCompPathListMulti(self, numProc=8):
        """ Return path list for all chemical component definition data files - (multiprocessing version)
        """
        if self.__verbose:
            self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()
        try:
            dataS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            dataList = [a for a in dataS]
            mpu = MultiProcUtil(verbose=True)
            mpu.set(workerObj=self, workerMethod="_makeComponentPathListMulti")
            ok, failList, retLists, diagList = mpu.runMulti(dataList=dataList, numProc=numProc, numResults=1)
            pathList = retLists[0]
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nPath list length %d  in %.2f seconds\n" % (len(pathList), endTime0 - startTime))

            return pathList
        except:
            traceback.print_exc(file=self.__lfh)

        endTime = time.time()
        self.__lfh.write("\nCompleted %s %s at %s (%.2f seconds)\n" % (self.__class__.__name__,
                                                                       sys._getframe().f_code.co_name,
                                                                       time.strftime("%Y %m %d %H:%M:%S", time.localtime()),
                                                                       endTime - startTime))
        return []

    def updatePrdSupportFiles(self, idMaxLen=14, numProc=4):
        """  Create full idlist, pathlist, concatenated PRD dictionary file,
        serialized dictionary, and dictionary index.
        """
        ok1 = ok2 = ok3 = ok4 = ok5 = ok6 = False
        pathList, familyPathList, ccPathList = self.getBirdPathList()

#        self.writeList(idList, self.__pathCCIdList)
#        self.writeList(pathList, self.__pathCCPathList)
        (ok1, updated) = self.concatPathListExt(pathList, self.__pathPrdDictFile, avoidUpdate = True)
        # If prd file updated, then need serial
        if ok1 and updated:
            ok2 = self.__serializePrdDictOp('prd')
        else:
            ok2 = True

        (ok3, updated) = self.concatPathListExt(ccPathList, self.__pathPrdCcFile, avoidUpdate = True)
        if ok3 and updated:
            ok4 = self.__serializePrdDictOp('prdcc')
        else:
            ok4 = True

        # PRD summary files
        ok5 = self.__generatePrdSummaryOp()

        # Get family mappings
        ok6 = self.__generatePrdFamilyMapOp(familyPathList)

            
#        #
#        ok2 = 
#        ok3 = self.__indexDictOp()
#        return ok1 and ok2 and ok3
        return ok1 and ok2 and ok3 and ok4 and ok5 and ok6


    def __serializePrdDictOp(self, which, minSize=10):
        """  Serialize chemical component dictionary from concatenated dictionary text.
        """
        self.__lfh.write("\nStarting %s %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name, which))
        startTime = time.time()

        fList = {'prd' : [ self.__pathPrdDictFile, self.__pathPrdDictSerial, "prd-dict-serialize.log"],
                 'prdcc' : [ self.__pathPrdCcFile, self.__pathPrdCcSerial, "prdcc-dict-serialize.log"],
                 }
        try:
            ref = fList[which]
            outPathTmp = self.__makeTempPath(ref[1])
            inpPath = ref[0]
            logPath = os.path.join(self.__pathPrdDictRef, ref[2])
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose)
            #
            dp.setDebugMode(flag=self.__debug)
            dp.imp(inpPath)
            dp.op("chem-comp-dict-serialize")
            dp.expLog(logPath)
            dp.exp(outPathTmp)
            fSize = dp.expSize()
            if fSize > minSize:
                os.chmod(outPathTmp, 0o664)
                shutil.move(outPathTmp, ref[1])
                os.chmod(ref[1], 0o664)
                ok = True
            else:
                ok = False
            if not self.__debug:
                dp.cleanup()
            endTime0 = time.time()
            if self.__verbose:
                self.__lfh.write("\nSerialized dictionary file size %d  in %.2f seconds\n" % (fSize, endTime0 - startTime))
            return ok
        except:
            traceback.print_exc(file=self.__lfh)
        return False

    def __generatePrdSummaryOp(self, minSize=10):
        """Generate summary cif file and serialize it"""
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()

        ccSDBin = self.__pathCCDictSerial
        prdSDBin = self.__pathPrdDictSerial        
        outPathTmp = self.__makeTempPath(self.__pathPrdSummary)
        outPathSerialTmp = self.__makeTempPath(self.__pathPrdSummarySerial)

        ok1 = ok2 = False
        try:
            logPath = os.path.join(self.__pathPrdDictRef, "prd-summary.log")
            dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose)
            dp.setDebugMode(flag=self.__debug)
            dp.imp(prdSDBin)
            dp.addInput(name="ccsdb_path", value = ccSDBin)
            dp.op("prd-summary-serialize")
            dp.expLog(logPath)
            dp.expList([outPathTmp, outPathSerialTmp])
            # If changed....
            updated = False
            f1 = DataFile(outPathTmp)
            if f1.srcFileExists():
                ok1 = True
                fSize = f1.srcFileSize()
                if fSize > minSize:
                    outPath = self.__pathPrdSummary
                    if os.path.exists(outPath):
                        if not filecmp.cmp(outPathTmp, outPath, shallow=False):
                            updated = True
                            os.unlink(outPath)
                    else:
                        updated = True

                    if updated:
                        os.chmod(outPathTmp, 0o664)
                        shutil.move(outPathTmp, outPath)
                        os.chmod(outPath, 0o664)
                    else:
                        f1.remove()
            else:
                ok1 = False

            f1 = DataFile(outPathSerialTmp)
            if updated:
                if f1.srcFileExists():
                    ok2 = True

                    updated = False
                    fSize = f1.srcFileSize()
                    if fSize > minSize:
                        outPath = self.__pathPrdSummarySerial
                        updated = False
                        if os.path.exists(outPath):
                            if not filecmp.cmp(outPathSerialTmp, outPath, shallow=False):
                                os.unlink(outPath)
                                updated = True
                        else:
                            updated = True

                    if updated:
                        os.chmod(outPathSerialTmp, 0o664)
                        shutil.move(outPathSerialTmp, outPath)
                        os.chmod(outPath, 0o664)
                    else:
                        f1.remove()
            else:
                f1.remove()
                ok2 = False

            if not self.__debug:
                dp.cleanup()
            endTime0 = time.time()

            #self.__lfh.write("\nDictionary summary update ok1 %s ok2 %s\n" % (ok1, ok2))
            if self.__verbose:
                self.__lfh.write("\nDictionary summary file size %d  in %.2f seconds\n" % (fSize, endTime0 - startTime))
            return ok1 and ok2

        except:
            traceback.print_exc(file=self.__lfh)

        return False

    def __generatePrdFamilyMapOp(self, familyPathList, minSize=10):
        """Generate family mapping file"""
        self.__lfh.write("\nStarting %s %s\n" % (self.__class__.__name__, sys._getframe().f_code.co_name))
        startTime = time.time()

        # We do not retain concatenation when done...
        tempFamilyFile = os.path.join(self.__pathPrdDictRef, "prd-family-temp.cif")
        outPathTmp = self.__makeTempPath(self.__pathPrdFamilyMapping)

        ok = self.concatPathList(familyPathList, tempFamilyFile)


        if ok:
            try:
                logPath = os.path.join(self.__pathPrdDictRef, "prd-family.log")
                dp = RcsbDpUtility(tmpPath=self.__sessionPath, siteId=self.__siteId, verbose=self.__verbose)
                dp.setDebugMode(flag=self.__debug)
                dp.imp(tempFamilyFile)
                dp.op("prd-family-mapping")
                dp.expLog(logPath)
                dp.exp(outPathTmp)
                fSize = dp.expSize()
                if fSize > minSize:
                    outPath = self.__pathPrdFamilyMapping
                    updated = False
                    if os.path.exists(outPath):
                        if not filecmp.cmp(outPathTmp, outPath, shallow=False):
                            os.unlink(outPath)
                            updated = True
                    else:
                        updated = True

                    if updated:
                        os.chmod(outPathTmp, 0o664)
                        shutil.move(outPathTmp, outPath)
                        os.chmod(outPath, 0o664)
                    else:
                        try:
                            os.unlink(outPathTmp)
                        except:
                            pass
                    # Remove tempFamilyFile
                    try:
                        os.unlink(tempFamilyFile)
                    except:
                        pass

                if not self.__debug:
                    dp.cleanup()
                return True

            except:
                traceback.print_exc(file=self.__lfh)

        return False
