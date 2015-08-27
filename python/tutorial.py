# This program rearranges raw Egderyders data and builds two lists of dicts, userlist and ciommentslist, containing 
# of the data needed to buildm graphs. These objects are then saved into files.
import os, sys
import json
import csv
from datetime import datetime
import time
import logging
import re

from edgesense.utils.logger_initializer import initialize_logger
from edgesense.utils.resource import mkdir

def parse_options(argv):
    import getopt

    basepath = '.'
    
    timestamp = datetime.now()
    tag = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    filename = tag+".csv"  

    try:
        opts, args = getopt.getopt(argv,"s:f:",["source=","file="])
    except getopt.GetoptError:
        print 'tutorial.py -s <source dir> -f <output filename>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           print 'tutorial.py -s <source dir> -f <output filename>' 
           sys.exit()
        elif opt in ("-s", "--source"):
           basepath = arg
        elif opt in ("-f", "--filename"):
           filename = arg
           
    destination_path = os.path.abspath(os.path.join(basepath, "output"))
    mkdir(destination_path)
    outuput_filename = os.path.join(destination_path, filename)
    source_path = os.path.abspath(basepath)
    
    logging.info("parsing files %(s)s to %(f)s" % {'s': source_path, 'f': outuput_filename})
    return (source_path,outuput_filename)

def main(argv):
    initialize_logger('./log')

    source_path, outuput_filename = parse_options(argv)
    
    logging.info("Tutorial result processing - started")
    
    all_files = [ f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path,f)) ]
    
    runs = {}
    timestamp = datetime.now()
    base_run_id = timestamp.strftime('%Y-%m-%d-%H-%M-%S')
    fake_run_id = 1
    for filename in all_files:
        logging.info("Tutorial result processing - loading:"+os.path.join(source_path,filename))
        f = open(os.path.join(source_path,filename), 'r')
        try:
            parsed = json.load(f)
            if parsed.has_key('run_id'):
                run_id = parsed['run_id']
            else:
                run_id = base_run_id+'--'+str(fake_run_id)
                fake_run_id += 1
            
            if not runs.has_key(run_id):
                runs[run_id] = {}
        
            run_obj = runs[run_id]
            run_obj['run_id'] = run_id
            if parsed.has_key('base'):
                run_obj['base'] = parsed['base']
                m = re.search('(\d\d\d\d)-(\d\d)-(\d\d)-\d\d-\d\d-\d\d$', parsed['base'])
                if m:
                    run_obj['date'] = m.group(1)+"-"+m.group(2)+"-"+m.group(3)
            if parsed.has_key('comments'):
                run_obj['comments'] = parsed['comments'].encode('utf-8').strip()
            # collect the tutorial answer results
            if parsed.has_key('answers'):
                for a in parsed['answers']:
                    run_obj[a['step']] = a['success']
            # collect the tutorial survey results
            if parsed.has_key('surveys'):
                for a in parsed['surveys']:
                    run_obj[a['step']] = a['value']
            
                
        except:
            logging.info("Tutorial result processing - error parsing:"+os.path.join(source_path,filename))
        
    
    # save the runs to a CSV file
    logging.info("Tutorial result processing - Writing:"+outuput_filename) 
    headers = [ 'run_id','base', 'date', \
                'betweenness_bin', 'relationship_percentage', \
                'posts_percentage', 'comments_share', \
                'modularity_increase', 'survey-1', \
                'survey-2', 'survey-3', 'survey-4', \
                'survey-5', 'comments']
    with open(outuput_filename, 'wb') as f:  
        w = csv.DictWriter(f, headers)
        w.writeheader()
        w.writerows(runs.values())
        
    logging.info("Tutorial result processing - Completed")  

if __name__ == "__main__":
   main(sys.argv[1:])

