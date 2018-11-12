##
# File:     doServiceRequestRegister.wsgi
# Created:  8-Sept-2016
# Updates:
#   30-Sep-2016  Increase the token expiration to 14 days for the friendly test.
#    2-Dec-2016  Increase token expiration 30 days --
##
"""
This top-level responder for web service API registration requests ...

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"


import json
import logging
import datetime
from webob import Request, Response

from wwpdb.utils.ws_utils.TokenUtils import JwtTokenUtils
from wwpdb.utils.ws_utils.ServiceSmtpUtils import ServiceSmtpUtils


# Create logger
logger = logging.getLogger()
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s]-%(module)s.%(funcName)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


from wwpdb.utils.ws_utils.ServiceResponse import ServiceResponse
# from wwpdb.apps.val_ws_server.webapp.WebServiceApp import WebServiceApp
# from wwpdb.utils.ws_utils.TokenUtils import JwtTokenReader


class MyRequestApp(object):
    """  Process request and response from WSGI server using WebOb Request/Response objects.
    """

    def __init__(self, serviceName="my service", authVerifyFlag=False):
        """

        """
        self.__serviceName = serviceName
        self.__authVerifyFlag = authVerifyFlag
        #

    def __dumpRequest(self, request):
        outL = []
        outL.append('%s' % ('-' * 80))
        outL.append("Web server request data content:")
        try:
            outL.append("Host:            %s" % request.host)
            outL.append("Path:            %s" % request.path)
            outL.append("Method:          %s" % request.method)
            outL.append("wwpdb-api-token: %s" % request.headers.get('wwpdb-api-token'))
            outL.append("Headers:         %r" % request.headers.items())
            outL.append("Query string:    %s" % request.query_string)
            outL.append("Parameter List:")
            for name, value in request.params.items():
                outL.append("  ++  Request parameter:    %s:  %r" % (name, value))
        except:
            logger.exception("FAILING for service %s" % self.__serviceName)
        return outL

    def sendAccessToken(self, emailAddress, tokenPrefix, expireDays):
        '''Test acquire new or existing token and send token to recipient '''
        tU = JwtTokenUtils(tokenPrefix=tokenPrefix)
        tokenId, jwtToken = tU.getToken(emailAddress, expireDays=expireDays)
        logging.debug("tokenid %r is %r " % (tokenId, jwtToken))
        tD = tU.parseToken(jwtToken)
        #tId = tD['sub']
        logging.debug("token %r payload %r " % (tokenId, tD))
        #
        msgText = '''
Thank you for requesting an API access key for a OneDep webservice. Your access key is included
in the text of the message below and as a file attachment.  This access key is valid for %d days.

----------------- Access Key (160 characters on one-line) - Remove this surrounding text  ---------------------
%s
------------------------------------------- Remove this surrounding text  ---------------------------------------
        ''' % (expireDays, jwtToken)
        #
        if False:
            tokenFileName = "onedep_apikey.jwt"
            with open(tokenFileName, 'wb') as outfile:
                outfile.write("%s" % jwtToken)
        smtpU = ServiceSmtpUtils()
        ok = smtpU.emailFiles('noreply@mail.wwpdb.org', emailAddress, 'OneDep Access Token', msgText,
                              textAsAttachment=jwtToken, textAttachmentName="onedep_apikey.jwt")
        # ok = smtpU.emailFiles('noreply@mail.wwpdb.org', emailAddress, 'wwPDB Access Token', msgText,
        #                      fileList=[tokenFileName])

        return ok

    def __call__(self, environment, responseApplication):
        """          Request callable entry point
        """
        #
        myRequest = Request(environment)
        logger.debug("%s" % ("\n ++ ".join(self.__dumpRequest(request=myRequest))))
        #
        myParameterDict = {'request_host': [''], 'wwpdb_site_id': [''], 'service_user_id': ['']}
        #
        try:
            #
            # Injected from the web server environment
            if 'WWPDB_SITE_ID' in environment:
                myParameterDict['wwpdb_site_id'] = [environment['WWPDB_SITE_ID']]

            if 'HTTP_HOST' in environment:
                myParameterDict['request_host'] = [environment['HTTP_HOST']]
            #
            # Injected from the incoming request payload
            #
            for name, value in myRequest.params.items():
                if (name not in myParameterDict):
                    myParameterDict[name] = []
                myParameterDict[name].append(value)
            myParameterDict['request_path'] = [myRequest.path.lower()]

        except:
            logging.exception("Exception processing %s request parameters" % self.__serviceName)

        ###
        # At this point we have everything needed from the request !
        ###
        #logger.debug("%s" % ("\n ++ ".join(self.__dumpRequest(request=myRequest))))

        try:
            logger.debug("Processing request %r" % myParameterDict['request_path'])
            ok = False
            if '/service/register/accesstoken' in myParameterDict['request_path'] and 'email' in myParameterDict:
                ok = self.sendAccessToken(myParameterDict['email'][0], tokenPrefix="VALWS", expireDays=30)
                if ok:
                    rD = {}
                    sR = ServiceResponse(returnFormat='json', injectStatus=False)
                    rD['errorflag'] = False
                    rD['statusmessage'] = 'registration success'
                    sR.setData(rD)
                    myResponse = sR.getResponse()
        except:
            logger.exception("Service request processing exception")
        #
        if not ok:
            logger.debug("Registration failure returning error status")
            sR = ServiceResponse(returnFormat='json')
            sR.setError(statusCode=500, msg="Access token registration failure")
            myResponse = sR.getResponse()
        #
        #
        logger.debug("Request processing completed registration service %s\n\n" % self.__serviceName)
        ###
        return myResponse(environment, responseApplication)

##
##
application = MyRequestApp(serviceName="RegistrationService", authVerifyFlag=False)
