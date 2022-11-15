# pip install evtxtoelk

import sys,getopt
from sys import argv

from evtxtoelk import EvtxToElk

def main(scriptname, argv):
    my_file = ''
    script_name="EvtxToElk.py"
    usage_msg=(script_name + ' -r <log.evtx>')
#    usage_msg="\n".join(usage_msg)
    try:
        opts, args = getopt.getopt(argv,"hr:")
    except getopt.GetoptError:
       print(usage_msg)
       sys.exit()
    for opt, arg in opts:
       if opt == '-h':
          print(usage_msg)
          sys.exit()
       elif opt in ("-r"):
          my_file = arg
    if not my_file:
       print(usage_msg)
       sys.exit()

    EvtxToElk.evtx_to_elk(my_file,"http://localhost:9200")



if __name__ == "__main__":
    main(argv[0], sys.argv[1:])

