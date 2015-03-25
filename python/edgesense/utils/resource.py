import os
import json
import csv
import urllib2
import base64
import logging
from . import gexf

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

def dump_to_file(data, where):
    if where:
        with open(where, 'wb') as f:
            f.write(data.read())
        logging.info("Dumped data to %(s)s" % {'s': where})
        return get_data(where)
    return data
    
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
    
def load(thing, username=None, password=None, dump_to=None):
    data = get_data(thing, username, password)
    data = dump_to_file(data, dump_to)
    parsed = json.load(data)
    return parsed

def load_csv(thing, username=None, password=None, dump_to=None):
    data = get_data(thing, username, password)
    data = dump_to_file(data, dump_to)
    parsed = [row for row in csv.DictReader(data)]
    return parsed

def write_network(network, multi_network, timestamp, create_datapackage, datapackage_title, license_type, license_url, destination_path):
    tag = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    tagged_dir = os.path.join(destination_path, "data", tag)

    # dump the network to a json file, minified
    save(network, 'network.min.json', tagged_dir)
    logging.info("network dumped")  
    
    # create the datapackage
    if create_datapackage:
        try:
            # load the datapackage template
            basepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(basepath, "datapackage_template.json"), 'r') as datafile:
                datapackage = json.load(datafile)
                datapackage['license'] = {'type': license_type, 'url': license_url}
                if datapackage_title:
                    datapackage['title'] = datapackage_title
                datapackage['last_updated'] = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                datapackage['resources'][0].pop('url', None)
                datapackage['resources'][0]['path'] = os.path.join('data', tag, 'network.gexf')

                # dump the gexf file
                gexf_file = os.path.join(tagged_dir, 'network.gexf')
                gexf.save_gexf(multi_network, gexf_file)
                # dump the datapackage
                save(datapackage, 'datapackage.json', destination_path, True)
                logging.info("datapackage saved")
        except:
            logging.error("Error reading the datapackage template")
            create_datapackage = False
    
    save({'last': tag, 'datapackage': create_datapackage}, 'last.json', destination_path)

