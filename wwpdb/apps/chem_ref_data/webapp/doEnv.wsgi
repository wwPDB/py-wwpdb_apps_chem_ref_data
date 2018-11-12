##
#!/opt/python/bin/python
##
# File:  doEnv.wsgi
# Date:  3-Jul-2016
#
# Updated:
##
"""
Print the Apache request environment - using mod_wsgi module protocol

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import os.path
import os
import sys
import pwd

os.environ["HOME"] = pwd.getpwuid(os.getuid()).pw_dir
# os.environ['PYTHON_EGG_CACHE'] = '/www/temporary/python-eggs'

try:
    __file__
except NameError:
    __file__ = '?'

html_template = """\
<html>
<head>
 <title>WSGI Request Environment</title>
</head>
<body>
 <h1>WSGI Request Environment</h1>
 <table border=1>
  <tr><th colspan=2>1. System Information</th></tr>
  <tr><td>Python</td><td>%(python_version)s</td></tr>
  <tr><td>Python Path</td><td>%(python_path)s</td></tr>
  <tr><td>Platform</td><td>%(platform)s</td></tr>
  <tr><td>Absolute path of this script</td><td>%(abs_path)s</td></tr>
  <tr><td>Filename</td><td>%(filename)s</td></tr>
  <tr><th colspan=2>2. WSGI Environment</th></tr>
%(wsgi_env)s
 </table>
</body>
</html>
"""

row_template = "  <tr><td>%s</td><td>%r</td></tr>"


def application(environ, start_response):
    """ Display the WSGI environment """
    # emit status / headers
    status = "200 OK"
    headers = [('Content-Type', 'text/html'), ]
    start_response(status, headers)

    # assemble and return content
    content = html_template % {
        'python_version': sys.version,
        'platform': sys.platform,
        'abs_path': os.path.abspath('.'),
        'filename': __file__,
        'python_path': repr(sys.path),
        # 'wsgi_env': '\n'.join([row_template % item for item in environ.items()]),
        'wsgi_env': '\n'.join([row_template % (ky, environ[ky]) for ky in sorted(environ.keys())]),
    }
    return [content]
