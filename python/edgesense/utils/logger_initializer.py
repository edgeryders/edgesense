import logging
import os.path
from edgesense.utils.resource import mkdir
 
def initialize_logger(output_dir, file_level=logging.DEBUG, console_level=logging.DEBUG, file_mode='a'):
    mkdir(output_dir)
    
    # set up logging to file (default)
    file_name = os.path.join(output_dir, "edgesense.log")
    logging.basicConfig(level=file_level,
                        format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=file_name,
                        filemode=file_mode)
    logging.getLogger('rdflib').setLevel(logging.ERROR)
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(console_level)
    formatter = logging.Formatter("[%(asctime)s] %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
 