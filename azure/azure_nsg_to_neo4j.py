#pip3 install neo4j-driver py2neo

# Get the nsg into a file
'''
az graph query -q "Resources\
| where type == 'microsoft.network/networksecuritygroups'\
| extend rulecount = array_length(properties.defaultSecurityRules)\
| mvexpand rules=properties.defaultSecurityRules\
| mvexpand sec_rules=properties.securityRules\
| project nsg_name=name,\
rulename=sec_rules.name,\
sec_rules.properties.access,\
direction=sec_rules.properties.direction,\
destination=sec_rules.properties.destinationAddressPrefix,\
source=sec_rules.properties.sourceAddressPrefix,\
dport=sec_rules.properties.destinationPortRange,\
sport=sec_rules.properties.sourcePortRange,\
rulecount" > nsg.json
'''

import neo4j
import py2neo
import sys,getopt
import json
import numpy as np # used to uniq python lists
import ipaddress
import getpass
from sys import argv

from py2neo import Graph, Node, Relationship, NodeMatcher
from azure_routes_to_neo4j import get_uniq_nextHopIpAddress
from azure_routes_to_neo4j import push_nextHopIpAddress_to_neo4j

nsgfile = ''

def load_json(filename):
    with open(filename) as f:
        jsontree = json.load(f)
    if len(jsontree) > 0:
        return jsontree
    else:
        print('Json Parse Failure.')
        
        
def clear_graph_database(graph):
    graph.run("MATCH (n) DETACH DELETE n")


def main(scriptname, argv):

    nsgfile = ''
    script_name = 'nsg_to_neo4j.py'
    usage_msg = (script_name + ' -n <nsg.json> -r <routes.json>')
    #    usage_msg="\n".join(usage_msg)
    try:
        opts, args = getopt.getopt(argv, "hn:r:")
    except getopt.GetoptError:
        print(usage_msg)
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print(usage_msg)
            sys.exit()
        elif opt in ("-n"):
            nsg_file = arg
        elif opt in ("-r"):
            routes_file = arg
    if not nsg_file or not routes_file:
        print(usage_msg)
        sys.exit()

    nsg_tree = load_json(nsg_file)
    routing_tree = load_json(routes_file)

    print ("############### Routing Gateways:")
    nextHopIpAddress_uniq_list = get_uniq_nextHopIpAddress(routing_tree)
    #    print (nextHopIpAddress_uniq_list)

    pw = getpass.getpass()
    conn_string = "bolt://neo4j:" + pw + "@localhost:7687"

    # what is this doing?
    nextHopIpAddress_uniq_list = np.delete(nextHopIpAddress_uniq_list, np.argwhere(nextHopIpAddress_uniq_list == ''))

    print (nextHopIpAddress_uniq_list)
    current_graph = Graph(conn_string)
    tx = current_graph.begin()
#    clear_graph_database(current_graph)
#    print ("Cleared neo4j db")

    push_nextHopIpAddress_to_neo4j(nextHopIpAddress_uniq_list, tx)
    tx.commit()
    print ("Pushed nextHopIpAddress_uniq_list to neo4j")



if __name__ == "__main__":
    main(argv[0], sys.argv[1:])
