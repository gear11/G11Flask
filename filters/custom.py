__author__ = 'Andy Jenkins'

import logging
from jinja2 import evalcontextfilter
import json
import dpath.util

LOG = logging.getLogger("")

@evalcontextfilter
def json_filter(eval_ctx, value):
    LOG.info("Loading value as JSON")
    return json.loads(value)

@evalcontextfilter
def dpath_filter(eval_ctx, obj, glob):
    LOG.info("Searching value for glob: %s", glob)
    k, v = dpath.util.search(obj, glob).popitem()
    return v
