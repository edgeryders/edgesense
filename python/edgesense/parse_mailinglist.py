import os, sys
import json
import mailbox
from datetime import datetime
import time
import logging

from edgesense.utils.logger_initializer import initialize_logger
import edgesense.utils as eu
import edgesense.mailinglist.threading as emt
import edgesense.mailinglist.parse as emp

def write_file(elements, name, destination_path):
    # dump the network to a json file, formatted
    eu.resource.save(elements, name, destination_path, True)
    logging.info("Parsing mailing list - Saved: %(d)s/%(n)s" % {'d':destination_path, 'n':name})

def parse_options(argv):
    import getopt
    # defaults
    sources = []
    outdir = '.'
    moderators = []
    debug = False
    charset = 'utf-8'
    force_name_as_uid = False
    
    try:
        opts, args = getopt.getopt(argv,"s:o:m:",["source=","outdir=","moderators=","charset=","force-name-as-uid","debug"])
    except getopt.GetoptError:
        logging.error('parse_mailinglist.py -s <source txt file (comma separated if more than 1)> -o <output directory> -m <moderators emails, comma separated>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
           logging.info('parse_mailinglist.py -s <source txt file (comma separated if more than 1)> -o <output directory> -m <moderators emails, comma separated>')
           sys.exit()
        elif opt in ("-s", "--source"):
           sources = arg.split(',')
        elif opt in ("-o", "--outdir"):
           outdir = arg
        elif opt in ("-m", "--moderators"):
           moderators = [m.replace('@', ' at ') for m in arg.split(',')]
        elif opt in ("--charset"):
           charset = arg
        elif opt in ("--force-name-as-uid"):
           force_name_as_uid = True
        elif opt in ("--debug"):
           debug = True
    
    logging.info("parsing files %(s)s" % {'s': repr(sources)})
    return (sources,outdir,moderators,charset,force_name_as_uid,debug)

def print_container(ctr, depth=0):
    print((depth*'   ')+repr(ctr.message and ctr.message.subject))
    for c in ctr.children:
        print_container(c, depth+1)

def main():
    initialize_logger('./log')
    
    generated = datetime.now()
    sources, outdir, moderators, charset, force_name_as_uid, debug = parse_options(sys.argv[1:])
    logging.info("Parsing mailinglist - Started")
    logging.info("Parsing mailinglist - Source files: %(s)s" % {'s':repr(sources)})
    logging.info("Parsing mailinglist - Output directory: %(s)s" % {'s':outdir})
    
    # 1. load and parse each file in a list of messages
    logging.info("Parsing mailinglist - Reading the files")
    messages = []
    for file in sources:
        mbox = mailbox.mbox(file)
        for msg in mbox:
            messages.append(emt.Message(msg))
    
    # 2. build the threaded containers
    logging.info("Parsing mailinglist - Threading the messages")
    subject_table = emt.thread(messages)
    root_containers = [ctr for (subj, ctr) in subject_table.items()]
    containers = emp.promote_none_root_set_children(root_containers)
    
    if force_name_as_uid:
        emp.force_name_as_address(containers)
    
    # Debug
    if debug:
        print('==== Message threads ====')
        for container in containers:
            emp.print_container(container)
        print('=========================')

    # 3. extract the users nodes comments and sort them
    logging.info("Parsing mailinglist - Extracting the data")
    users,nodes,comments = emp.users_nodes_comments_from(containers, moderators, charset)
    sorted_users = sorted(users, key=eu.sort_by('created'))
    sorted_nodes = sorted(nodes, key=eu.sort_by('created'))
    sorted_comments = sorted(comments, key=eu.sort_by('created'))
    
    # 5. saves the files
    logging.info("Parsing mailinglist - Saving the files")
    write_file(sorted_users, 'users.json', outdir)
    write_file(sorted_nodes, 'nodes.json', outdir)
    write_file(sorted_comments, 'comments.json', outdir)
    
    logging.info("Parsing mailinglist - Completed")

if __name__ == "__main__":
   main()
