""" main.py is the top level script.

Return "Hello World" at the root URL.
"""

import sys

# sys.path includes 'server/lib' due to appengine_config.py
from flask import Flask
from flask import render_template, request, abort, Response, redirect, url_for
import requests
import logging
app = Flask(__name__.split('.')[0])

#APPROVED_HOSTS = [ "*.google.com", "www.g"]
CHUNK_SIZE = 1024

LOG = logging.getLogger("main.py")

logging.basicConfig(level=logging.INFO)

LOG.info("Loading main.py")

def is_approved(host):
    return True

def split_url(url):
    proto, rest = url.split(':', 1)
    host, uri = rest[2:].split('/', 1)
    return (proto, host, uri)


#
# Parses out info indicating the request is from a previously proxied page

# Referer: http://localhost:8080/p/google.com
#
def proxy_ref_info(request):
    ref = request.headers.get('referer')

    if ref:
        _, _, uri = split_url(ref)
        if uri.find("/") < 0:
            return None
        first, rest = uri.split("/", 1)
        if first == ("p"):
            parts = rest.split("/", 1)
            r = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
            LOG.info("Referred by proxy host, uri: %s, %s", r[0], r[1])
            return r
    return None



@app.route('/<path:url>')
def root(url):
    LOG.info("Root route, path: %s", url)
    proxy_ref = proxy_ref_info(request)

    if proxy_ref:
        url = proxy_ref[0] + "/" + url
        url = url + "?" + request.query_string if request.query_string else url
        #redirect_url = url_for('proxy', url=url)
        redirect_url = '/p/%s' % url
        LOG.info("Redirecting referred URL to: %s", redirect_url)
        return redirect(redirect_url)
        #return proxy(proxy_ref[0] + "/" + url)


    return render_template('hello.html', name=url,request=request)


@app.route('/p/<path:url>')
def proxy(url):
    try:
        url = 'http://%s' % url
        LOG.info("Proxying %s", url)
        #host = url.split('/', 1)[0]
        if not is_approved(url):
            abort(403)

        proxy_ref = proxy_ref_info(request)
        headers = { "Referer" : "http://%s/%s" % (proxy_ref[0], proxy_ref[1])} if proxy_ref else {}
        LOG.info("Fetching with headers: %s, %s", url, headers)
        r = requests.get(url, stream=True , params = request.args, headers=headers)
        LOG.info("Got %s response from %s",r.status_code, url)
        headers = dict(r.headers)
        #LOG.info("Received response: %s", headers)

        def generate():
            for chunk in r.iter_content(CHUNK_SIZE):
                yield chunk
        resp = Response(generate(), headers = headers)
        #resp.set_cookie('proxied-host', host)
        return resp
    except Exception, ex:
        LOG.exception(ex)
        abort(500)