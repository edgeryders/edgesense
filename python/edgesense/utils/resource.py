import os
import json
import urllib2

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

def load(thing):
    if thing.startswith("/") :
        thing = "file://"+thing
    data = urllib2.urlopen(thing)
    parsed = json.load(data)
    return parsed
