##
# File:     doServiceRequest.wsgi
# Created:  8-July-2016
# Updates:
#     3-Aug-2016  jdw integrate JWT token verification -
#     2-Dec-2016  jdw allow for API key bypass to support fully anonymous sessions.
#     2-Dec-2016  jdw pass remote_addr into the parameter dictionary -
#    27-Jan-2017  jdw adapt to chem_ref_dara service
#    20-May-2017  jdw Cleanup -
##
"""
This top-level responder for web service requests ...

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"


# import json
import sys
import logging
# Create logger
logger = logging.getLogger()
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(module)s.%(funcName)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)
logger.debug("LOADING - WSGI CHEMREF HANDLER ENTRY POINT")

import datetime
from webob import Request, Response

USEKEY = False

from wwpdb.utils.ws_utils.TokenUtils import JwtTokenReader
from wwpdb.apps.chem_ref_data.webapp.ChemRefDataWebApp import ChemRefDataWebApp
#


class MyRequestApp(object):
    """  Process request and response from WSGI server using WebOb Request/Response objects.
    """

    def __init__(self, serviceName="my service", authVerifyFlag=False):
        """

        """
        logger.debug("CHEMREF - IN WSGI CLASS CONSTRUCTOR - 1 %r %r" % (serviceName, authVerifyFlag))
        self.__serviceName = serviceName
        self.__authVerifyFlag = authVerifyFlag
        #
        self.__verbose = True
        self.__lfh = sys.stderr
        #

    def __dumpRequest(self, request):
        outL = []
        outL.append('%s' % ('-' * 80))
        outL.append("Web server request data content:")
        try:
            outL.append("Host:            %s" % request.host)
            outL.append("Remote host:     %s" % request.remote_addr)
            outL.append("Path:            %s" % request.path)
            outL.append("Method:          %s" % request.method)
            outL.append("wwpdb-api-token: %s" % request.headers.get('wwpdb-api-token'))
            outL.append("Headers:         %r" % sorted(request.headers.items()))
            # outL.append("Environ:         %r" % sorted(request.environ.items()))
            outL.append("Query string:    %s" % request.query_string)
            outL.append("Parameter List:")
            for name, value in request.params.items():
                outL.append("  ++  Request parameter:    %s:  %r\n" % (name, value))
        except:
            logger.exception("FAILING for service %s" % self.__serviceName)
        return outL

    def __isHeaderApiToken(self, request):
        try:
            tok = request.headers.get('wwpdb-api-token')
            if tok and len(tok) > 20:
                return True
        except:
            pass

        return False

    def __authVerify(self, authHeader, siteId, serviceUserId):
        """ Check the validity of the input API access token - check for user id consistency .

            Return: True for success or False otherwise
        """
        tD = {'errorCode': 401, 'errorMessage': "Token processing error", 'token': None, 'errorFlag': True}

        try:
            jtu = JwtTokenReader(siteId=siteId)
            tD = jtu.parseAuth(authHeader)
            if tD['errorFlag']:
                return tD
            tD = jtu.parseToken(tD['token'])
            logger.debug("authVerify tD %r" % tD)
            #
            if ((len(serviceUserId) > 0) and (serviceUserId != str(tD['sub']))):
                tD['errorMessage'] = 'Token user mismatch'
                tD['errorFlag'] = True
                tD['errorCode'] = 401
            #

            return tD
        except:
            logging.exception("Failed site %r auth header %r" % (siteId, authHeader))
            return tD

    def __call__(self, environment, responseApplication):
        """          Request callable entry point
        """
        #
        myRequest = Request(environment)
        logger.debug("CHEMREF - WSGI REQUEST ENTRY POINT - ")
        logger.debug("%s" % ("\n ++ ".join(self.__dumpRequest(request=myRequest))))
        siteId = ''
        #
        myParameterDict = {'request_host': [''], 'wwpdb_site_id': [''], 'service_user_id': [''], 'remote_addr': ['']}
        #
        try:
            #
            # Injected from the web server environment
            if 'WWPDB_SITE_ID' in environment:
                myParameterDict['wwpdb_site_id'] = [environment['WWPDB_SITE_ID']]

            if 'HTTP_HOST' in environment:
                myParameterDict['request_host'] = [environment['HTTP_HOST']]

            myParameterDict['remote_addr'] = [myRequest.remote_addr]
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
        logger.debug("Parameter dict:\n%s" % '\n'.join(["  ++  %s: %r" % (k, v) for k, v in myParameterDict.items()]))
        try:
            ok = True
            apiTokFlag = self.__isHeaderApiToken(myRequest)
            logger.debug("Request API token flag: %s" % apiTokFlag)
            if self.__authVerifyFlag and apiTokFlag:
                #  Verify API token -
                authD = self.__authVerify(myRequest.headers.get('wwpdb-api-token'), myParameterDict['wwpdb_site_id'][0], myParameterDict['service_user_id'][0])
                logger.debug("Authorization error flag is %r" % authD['errorFlag'])
                if authD['errorFlag']:
                    ok = False
                else:
                    myParameterDict['jwt-sub'] = [str(authD['sub'])]
                    myParameterDict['jwt-exp'] = [authD['exp']]
                    myParameterDict['jwt-iat'] = [authD['iat']]
                    myParameterDict['jwt-exp-ts'] = [datetime.datetime.utcfromtimestamp(authD['exp']).strftime("%Y-%b-%d %H:%M:%S")]
                    myParameterDict['jwt-iat-ts'] = [datetime.datetime.utcfromtimestamp(authD['iat']).strftime("%Y-%b-%d %H:%M:%S")]
                    myParameterDict['service_user_id'] = myParameterDict['jwt-sub']
            else:
                myParameterDict['service_user_id'] = ['CHEMREFWS_ANONYMOUS']

            if ok:
                siteId = myParameterDict['wwpdb_site_id'][0]
                ###
                # At this point we have everything needed from the request !
                ###
                myResponse = Response()
                ##
                # Default return type and status
                ##
                myResponse.status = '200 OK'
                myResponse.content_type = 'text/html'
                ###
                # Application specific functionality called here --
                ###
                myReq = ChemRefDataWebApp(parameterDict=myParameterDict, verbose=self.__verbose, log=self.__lfh, siteId=siteId)
                rspD = myReq.doOp()
                myResponse.content_type = rspD['CONTENT_TYPE']
                myResponse.body = rspD['RETURN_STRING']
                logger.debug("Response content_type %r \n" % rspD['CONTENT_TYPE'])
                logger.debug("Response body  %r \n" % rspD['RETURN_STRING'])
                #
        except:
            logger.exception("Service request processing exception")

        #
        logger.debug("Request processing completed for service %s\n\n" % self.__serviceName)
        ###
        return myResponse(environment, responseApplication)

##
##
application = MyRequestApp(serviceName="ChemRefDataApp", authVerifyFlag=USEKEY)
