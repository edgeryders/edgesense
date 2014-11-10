import logger_initializer
import resource
import extract
import gexf

def sort_by(key):
    return (lambda e: e.get(key, None))

