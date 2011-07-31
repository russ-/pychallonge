import decimal
import urllib
import urllib2
import dateutil.parser
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


CHALLONGE_API_URL = "challonge.com/api"

_credentials = {
    "user": None,
    "api_key": None,
}


class ChallongeException(Exception):
    pass


def set_credentials(username, api_key):
    """Set the challonge.com api credentials to use."""
    _credentials["user"] = username
    _credentials["api_key"] = api_key


def get_credentials():
    return _credentials["user"], _credentials["api_key"]


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
    d = {}
    for child in element:
        type = child.get("type") or "string"
        if child.get("nil"):
            value = None
        elif type == "boolean":
            value = True if child.text.lower() == "true" else False
        elif type == "datetime":
            value = dateutil.parser.parse(child.text)
        elif type == "decimal":
            value = decimal.Decimal(child.text)
        elif type == "integer":
            value = int(child.text)
        else:
            value = child.text
        
        d[child.tag] = value
    return d

def _verbosify_parameters(params_dict, object_type):
    converted_params = {}
    for k, v in params_dict.iteritems():
        converted_params["%s[%s]" % (object_type, k)] = v

    return converted_params
