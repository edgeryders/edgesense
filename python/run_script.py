import sys

from edgesense.build_network import main as build_network_main
from edgesense.catalyst_server import main as catalyst_server_main
from edgesense.drupal_script import main as drupal_script_main
from edgesense.parse_catalyst import main as parse_catalyst_main
from edgesense.parse_mailinglist import main as parse_mailinglist_main
from edgesense.parse_tweets import main as parse_tweets_main

functions = {
    'build_network': build_network_main,
    'catalyst_server': catalyst_server_main,
    'drupal_script': drupal_script_main,
    'parse_catalyst': parse_catalyst_main,
    'parse_mailinglist': parse_mailinglist_main,
    'parse_tweets': parse_tweets_main
}
if __name__ == "__main__":
    what = sys.argv[1]
    sys.argv.remove(what)
    if functions.has_key(what):
        functions[what]()
    else:
        print('Wrong function called, valid: '+', '.join(function.keys()))


