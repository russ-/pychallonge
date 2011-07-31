import threading
import urllib
import urllib2

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


CHALLONGE_API_URL = "challonge.com/api"

_auth_info = threading.local()
_auth_info.user = ""
_auth_info.api_key = ""



class ChallongeException(Exception):
    pass


def set_credentials(username, api_key):
    """Set the challonge.com api credentials to use."""
    _auth_info.user = username
    _auth_info.api_key = api_key


def get_credentials():
    return (_auth_info.user, _auth_info.api_key)


def fetch(method, uri, **params):
    params = urllib.urlencode(params)

    # build the HTTP request
    url = "https://%s/%s.xml" % (CHALLONGE_API_URL, uri)
    if method == "GET":
        req = urllib2.Request("%s?%s" % (url, params))
    else:
        req = urllib2.Request(url)
        req.add_data(params)
    req.get_method = lambda: method

    user, api_key = get_credentials()
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm="Application",
        uri=req.get_full_url(),
        user=user,
        passwd=api_key
    )
    opener = urllib2.build_opener(auth_handler)
    try:
        response = opener.open(req)
    except urllib2.HTTPError, e:
        if e.code != 422:
            raise
        # application-level errors
        doc = parse(e)
        if doc.tag != "errors":
            raise
        errors = [e.text for e in doc]
        raise ChallongeException(*errors)

    return response


def parse(fileobj):
    return ElementTree.parse(fileobj).getroot()


def fetch_and_parse(method, uri, **params):
    return parse(fetch(method, uri, **params))

def _dictify_element(element):
    """Converts children of element into key/value pairs in a dict"""
    return dict((e.tag, e.text) for e in element)

def _verbosify_parameters(params_dict, object_type):
    converted_params = {}
    for k, v in params_dict.iteritems():
        converted_params["%s[%s]" % (object_type, k)] = v

    return converted_params
