##
# File:  ChemRefDataCvsUtils.py
# Date:  4-Feb-2013  J. Westbrook
#
# Updated:
#
# 4-Feb-2013 jdw  Generalized from class ChemRefDataCvsUtils() for all chemical reference data repositories.
# 7-Feb-2013 jdw  Add remove method
##
"""
Wrapper for utilities for managing chemical reference data repositories and sandboxes.

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
import traceback
from wwpdb.api.facade.ConfigInfo import ConfigInfo
from wwpdb.utils.rcsb.CvsAdmin import CvsAdmin, CvsSandBoxAdmin
from wwpdb.utils.rcsb.MultiProcUtil import MultiProcUtil
from wwpdb.apps.chem_ref_data.utils.ChemRefPathInfo import ChemRefPathInfo


class ChemRefDataCvsUtils(object):

    """ Wrapper for utilities for managing chemical reference data repositories and sandboxes.
    """
    #

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
        #self.__topPath             = self.__reqObj.getValue("TopPath")
        #self.__topSessioPath       = self.__reqObj.getValue("TopSessionPath")
        #
        self.__sObj = self.__reqObj.getSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        #self.__sessionRelativePath = self.__sObj.getRelativePath()
        #self.__sessionId           = self.__sObj.getId()
        #
        self.__siteId = self.__reqObj.getValue("WWPDB_SITE_ID")
        self.__cI = ConfigInfo(self.__siteId)
        self.__sbTopPath = self.__cI.get('SITE_REFDATA_TOP_CVS_SB_PATH')
        self.__pI = ChemRefPathInfo(configObj=self.__cI, verbose=self.__verbose, log=self.__lfh)
        #
        self.__vc, self.__vcAd = self.__setupCvs()
        #

    def __setupCvs(self):
        #  Assign site specific chemical reference data CVS repository details --
        #
        cvsRepositoryHost = self.__cI.get('SITE_REFDATA_CVS_HOST')
        cvsRepositoryPath = self.__cI.get('SITE_REFDATA_CVS_PATH')
        #
        # Assign authentication details from the request environment -
        #
        cvsUser = self.__reqObj.getValue("SITE_REFDATA_CVS_USER")
        cvsPassword = self.__reqObj.getValue("SITE_REFDATA_CVS_PASSWORD")
        #
        cvsUser = self.__cI.get("SITE_REFDATA_CVS_USER")
        cvsPassword = self.__cI.get("SITE_REFDATA_CVS_PASSWORD")
        #
        vc = CvsSandBoxAdmin(tmpPath=self.__sessionPath, verbose=self.__verbose, log=self.__lfh)
        vc.setRepositoryPath(host=cvsRepositoryHost, path=cvsRepositoryPath)
        vc.setAuthInfo(user=cvsUser, password=cvsPassword)
        vc.setSandBoxTopPath(self.__sbTopPath)
        vcAd = CvsAdmin(tmpPath=self.__sessionPath, verbose=self.__verbose, log=self.__lfh)
        vcAd.setRepositoryPath(host=cvsRepositoryHost, path=cvsRepositoryPath)
        vcAd.setAuthInfo(user=cvsUser, password=cvsPassword)

        return vc, vcAd

    def syncBird(self):
        """  Update the CVS repositories related to BIRD PRD, family and chemical component definitions.
        """
        #
        textList = []
        #
        cvsProjectName = self.__pI.assignCvsProjectName(repType="PRD")
        ok1, text = self.__vc.update(projectDir=cvsProjectName, prune=True)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(sync) CVS %s update output is:\n%s\n" % (cvsProjectName, text))
        textList.append(text)
        #
        cvsProjectName = self.__pI.assignCvsProjectName(repType="PRD_FAMILY")
        ok2, text = self.__vc.update(projectDir=cvsProjectName)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(sync) CVS %s update output is:\n%s\n" % (cvsProjectName, text))
        textList.append(text)
        #
        cvsProjectName = self.__pI.assignCvsProjectName(repType="PRDCC")
        ok3, text = self.__vc.update(projectDir=cvsProjectName)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(sync) CVS %s update output is:\n%s\n" % (cvsProjectName, text))
        textList.append(text)
        self.__vc.cleanup()
        #
        ok = ok1 and ok2 and ok3
        return (ok, textList)

    def syncChemCompSerial(self):
        """  Update the CVS repositories related to the chemical component dicitonary.
        """
        #
        textList = []
        #
        cvsProjectName = self.__pI.assignCvsProjectName(repType="CC")
        ok, text = self.__vc.update(projectDir=cvsProjectName, prune=True)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(sync) CVS %s update status is: %r\n" % (cvsProjectName, ok))
            #self.__lfh.write("+ChemRefDataCvsUtils(sync) CVS %s update output is:\n%s\n" % (cvsProjectName,text[:100]))
        textList.append(text[:100])
        #
        # self.__vc.cleanup()
        #
        return (ok, textList)

    def syncChemComp(self, numProc=8):
        """  Update the CVS repositories related to the chemical component dicitonary.
        """
        #
        startTime = time.time()
        textList = []
        #
        cvsProjectName = self.__pI.assignCvsProjectName(repType="CC")
        dataS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        dataList = [(cvsProjectName, a, True) for a in dataS]
        #
        mpu = MultiProcUtil(verbose=self.__debug, log=self.__lfh)
        mpu.set(workerObj=self.__vc, workerMethod="updateList")
        ok, failList, resultList, diagList = mpu.runMulti(dataList=dataList, numProc=numProc)
        endTime = time.time()
        if self.__verbose:
            self.__lfh.write("\n+ChemRefDataCvsUtils(syncChemComp) CVS %s update status is: %r in %.2f seconds\n" %
                             (cvsProjectName, ok, endTime - startTime))

            if len(failList) > 0:
                self.__lfh.write("\n+ChemRefDataCvsUtils(syncChemComp) diagnostics %r\n" % failList)
        return (ok, diagList)

    def updateFile(self, filePath):
        """  Update the input file within the appropriate repository.  File names must obey repository
             naming conventions.

        """
        #
        textList = []
        ok = False
        #
        if not self.checkFileName(filePath):
            textList.append("Unrecognized file name %s" % filePath)
            return ok, textList

        if not self.exists(filePath):
            textList.append("Cannot update nonexistent repository file %s" % filePath)
            return ok, textList

        #
        projName, relPath = self.__pI.getCvsProjectInfo(self.__pI.assignIdCodeFromFileName(filePath))

        dstPath = os.path.join(self.__vc.getSandBoxTopPath(), projName, relPath)
        (pth, fn) = os.path.split(dstPath)

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(updateFile) CVS update %s %s working repository path is %s\n" % (projName, relPath, dstPath))

        #
        try:
            # make sure we have the latest version
            self.__vc.checkOut(os.path.join(projName, relPath))
            shutil.copy2(filePath, dstPath)
            ok, text = self.__vc.commit(projName, relPath)

        except:
            text = "+ChemRefDataCvsUtils(updateFile) CVS update exception"
            if self.__verbose:
                self.__lfh.write("+ChemRefDataCvsUtils(updateFile) CVS update %s %s status %r output is:\n%s\n" % (projName, relPath, ok, text))
                traceback.print_exc(file=self.__lfh)

        textList.append(text)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(updateFile) CVS update %s %s status %r output is:\n%s\n" % (projName, relPath, ok, text))
        self.__vc.cleanup()
        #
        return ok, textList

    def addFile(self, filePath):
        """  Add the input file to the appropriate repository.  File names must obey repository
             naming conventions.

        """
        #
        textList = []
        ok = False
        #
        if not self.checkFileName(filePath):
            textList.append("Unrecognized file name %s" % filePath)
            return ok, textList

        if self.exists(filePath):
            textList.append("Cannot add existing repository file name %s" % filePath)
            return ok, textList

        #
        projName, relPath = self.__pI.getCvsProjectInfo(self.__pI.assignIdCodeFromFileName(filePath))

        dstPath = os.path.join(self.__vc.getSandBoxTopPath(), projName, relPath)
        (pth, fn) = os.path.split(dstPath)

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(addFile) CVS add %s %s working repository path is %s\n" % (projName, relPath, dstPath))

        # add any missing containing directories for the destination file.
        try:
            if (not os.access(pth, os.F_OK)):
                os.makedirs(pth)
                head, tail = os.path.split(relPath)
                self.__vc.add(projName, head)
            shutil.copy2(filePath, dstPath)
            self.__vc.add(projName, relPath)
            ok, text = self.__vc.commit(projName, relPath)

        except:
            text = "+ChemRefDataCvsUtils(addFile) CVS add exception"
            if self.__verbose:
                self.__lfh.write("+ChemRefDataCvsUtils(addFile) CVS add %s %s status %r output is:\n%s\n" % (projName, relPath, ok, text))
                traceback.print_exc(file=self.__lfh)

        textList.append(text)
        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(addFile) CVS add %s %s status %r output is:\n%s\n" % (projName, relPath, ok, text))
        self.__vc.cleanup()
        #
        return ok, textList

    def history(self, idCode):
        """  Return the version history for the input id code from the appropriate repository.

             Id codes must obey repository naming conventions.

        """
        #
        textList = []
        ok = False
        #
        projName, relPath = self.__pI.getCvsProjectInfo(idCode)
        if projName is None or relPath is None:
            return ok, textList

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(history) CVS history id %s project %s  path %s\n" % (idCode, projName, relPath))
        #
        try:
            cvsPath = os.path.join(projName, relPath)
            ok, text = self.__vcAd.getHistory(cvsPath)
            textList.append(text)
        except:
            textList.append("CVS history exception")
            if self.__verbose:
                self.__lfh.write("+ChemRefDataCvsUtils(history) CVS history exception %s %s status %r output is:\n%s\n" % (projName, relPath, ok, textList))
                traceback.print_exc(file=self.__lfh)

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(remove) CVS history %s %s status %r output is:\n%s\n" % (projName, relPath, ok, textList))
        self.__vcAd.cleanup()
        #
        return ok, textList

    def checkoutRevisions(self, idCode):
        """  Return the pathlist of checked out revisions for the input id code from the appropriate repository.

             Id codes must obey repository naming conventions.

        """
        #
        pathList = []
        revList = []
        ok = False
        #
        projName, relPath = self.__pI.getCvsProjectInfo(idCode)
        if projName is None or relPath is None:
            return ok, textList

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(checkoutRevisions) id %s project %s  path %s\n" % (idCode, projName, relPath))
        #
        try:
            cvsPath = os.path.join(projName, relPath)
            ok, revList = self.__vcAd.getRevisionList(cvsPath)

            (pth, fn) = os.path.split(cvsPath)
            (base, ext) = os.path.splitext(fn)

            for revId in revList:
                rId = revId[0]
                outPath = os.path.join(self.__sessionPath, idCode + "-" + rId + ext)
                ok, text = self.__vcAd.checkOutFile(cvsPath=cvsPath, outPath=outPath, revId=rId)
                if ok:
                    pathList.append(outPath)
                    self.__lfh.write("CVS checkout status %r output %s is:\n%s\n" % (ok, outPath, text))
        except:
            textList.append("Revision checkout exception")
            if self.__verbose:
                self.__lfh.write("+ChemRefDataCvsUtils(checkoutRevisions) exception %s %s status %r output is:\n%s\n" % (projName, relPath, ok, textList))
                traceback.print_exc(file=self.__lfh)

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(checkoutRevisions) done %s %s status %r output is:\n%s\n" % (projName, relPath, ok, pathList))
        self.__vcAd.cleanup()
        #
        return ok, pathList

    def remove(self, idCode):
        """  Remove the reference file associated with the input id code from the appropriate repository.
             Id codes must obey repository naming conventions.

        """
        #
        text = ''
        textList = []
        ok = False
        #
        projName, relPath = self.__pI.getCvsProjectInfo(idCode)
        if projName is None or relPath is None:
            return ok, textList

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(remove) CVS remove id %s project %s  path %s\n" % (idCode, projName, relPath))
        #
        try:
            ok1, text = self.__vc.remove(projName, relPath, saveCopy=True)
            textList.append(text)

            # Remove the containing directory if required.
            repType = self.__pI.getIdType(idCode)
            if repType == "CC":
                (pth, fn) = os.path.split(relPath)
                ok2, text = self.__vc.removeDir(projName, pth)
                textList.append(text)
                ok = ok1 and ok2
            else:
                ok = ok1
        except:
            textList.append("+ChemRefDataCvsUtils(remove) CVS remove exception")
            if self.__verbose:
                self.__lfh.write("+ChemRefDataCvsUtils(remove) CVS remove %s %s status %r output is:\n%s\n" % (projName, relPath, ok, text))
                traceback.print_exc(file=self.__lfh)

        if self.__verbose:
            self.__lfh.write("+ChemRefDataCvsUtils(remove) CVS remove %s %s status %r output is:\n%s\n" % (projName, relPath, ok, textList))
        self.__vc.cleanup()
        #
        return ok, textList

    def exists(self, filePath):
        """ Test if the input 'filePath' corresponds to an existing entry in one of
            CVS repositories.

            Return True if an existing entry is found or False otherwise
        """
        if ((filePath is None) or (len(filePath) < 7)):
            return False

        projName, relPath = self.__pI.getCvsProjectInfo(self.__pI.assignIdCodeFromFileName(filePath))
        if projName is None:
            return False

        # check existing for file within the repository sandbox -
        if os.access(os.path.join(self.__sbTopPath, projName, relPath), os.R_OK):
            return True

        return False

    def checkFileName(self, filePath):
        """ Test if the input 'filePath' corresponds to the naming conventions of on of the
            CVS repositories.

            Return True for success or False otherwise
        """
        if ((filePath is None) or (len(filePath) < 7)):
            return False
        projName, relPath = self.__pI.getCvsProjectInfo(self.__pI.assignIdCodeFromFileName(filePath))
        return (projName is not None)
