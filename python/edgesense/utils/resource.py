import os
import json
import csv
import urllib2
import base64

def mkdir(newdir):
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)

def save(thing, filename, dirname='', formatted=False):
    mkdir(dirname)
    filename = os.path.join(dirname, filename)
    with open(filename, 'w') as outfile:
        if formatted:
            json.dump(thing, outfile, indent=4, sort_keys=True)
        else:
            json.dump(thing, outfile)

def get_data(thing, username=None, password=None):
    if thing.startswith("/") :
        thing = "file://"+thing
    # Adds the Basic http authenticaton header if needed
    if username and password:
        thing = urllib2.Request(thing)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        thing.add_header("Authorization", "Basic %s" % base64string)   
           
    data = urllib2.urlopen(thing)
    return data
    
def load(thing, username=None, password=None):
    data = get_data(thing, username, password)
    parsed = json.load(data)
    return parsed

def load_csv(thing, username=None, password=None):
    data = get_data(thing, username, password)
    parsed = [row for row in csv.DictReader(data)]
    return parsed
