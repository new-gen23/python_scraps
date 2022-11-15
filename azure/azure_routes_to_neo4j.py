#pip3 install neo4j-driver py2neo
# acquire data with query:
# az graph query -q "Resources | where type=='microsoft.network/routetables'" > routes.json


import neo4j
import py2neo
import sys,getopt
import json
import numpy as np # used to uniq python lists
import ipaddress
import getpass
from sys import argv

from py2neo import Graph, Node, Relationship, NodeMatcher

routingfile = ''

def load_json(filename):
    with open(filename) as f:
        jsontree = json.load(f)
    if len(jsontree) > 0:
        return jsontree
    else:
        print('Json Parse Failure.')


def get_uniq_nextHopIpAddress(routingtree):
#    print(json.dumps(routingtree))
    nextHopIpAddress_list = []
    for item in routingtree:
        #print(type(item))
        #print(item['id'])
        #print (item['properties']['resourceGuid'])
        for route in item['properties']['routes']:
#            print(route['name'])
#            print(route['properties']['addressPrefix'])
            try:
#                print(route['properties']['nextHopIpAddress'])
                nextHopIpAddress_list.append(route['properties']['nextHopIpAddress'])
            except:
#                print(route['name'] + " has no nextHopIpAddress")
                continue
    print ("Number of gateways:" + str(len(np.unique(nextHopIpAddress_list))))
    return np.unique(nextHopIpAddress_list)

def get_uniq_addressPrefix(routingtree):
    addressPrefix_list = []
    for item in routingtree:
        for route in item['properties']['routes']:
            try:
  #             print(route['properties']['addressPrefix'])
                addressPrefix_list.append(route['properties']['addressPrefix'])
            except:
#                print(route['name'] + " has no addressPrefix")
                continue
    print ("Number of subnets:" + str(len(np.unique(addressPrefix_list))))
    return np.unique(addressPrefix_list)

def clear_graph_database(graph):
    graph.run("MATCH (n) DETACH DELETE n")


def push_nextHopIpAddress_to_neo4j(nextHopIpAddress_uniq_list, tx):
    for item in nextHopIpAddress_uniq_list:
        mynode = Node("gwIP", name=item)
        tx.create(mynode)

def push_addressPrefix_to_neo4j(addressPrefix_uniq_list, tx):
    for item in addressPrefix_uniq_list:
        mynode = Node("SUBNET", name=item)
        tx.create(mynode)

def create_default_gw_connection_in_neo4j(routingtree, current_graph, tx):
    matcher = NodeMatcher(current_graph)

    for item in routingtree:
        for route in item['properties']['routes']:
            try:
                gateway_node = matcher.match("gwIP", name=route['properties']['nextHopIpAddress']).first()
                subnet_node = matcher.match("SUBNET", name=route['properties']['addressPrefix']).first()
            except:
#                print ("Subnet most likely had no gateway. they remain in neo4j but have no relation to a gateway")
                continue
            if(gateway_node != None and subnet_node != None):
                relation = Relationship(gateway_node, "routes", subnet_node)
                tx.create(relation)
           #    print ("relation created")
            else:
                print ("gateway or subnet is empty")

def create_gateway_to_subnet_connection_in_neo4j(nextHopIpAddress_uniq_list, addressPrefix_uniq_list, tx):
    #matcher = NodeMatcher(current_graph)
    print("#################")
    print(nextHopIpAddress_uniq_list)
    print("#################")
    print(addressPrefix_uniq_list)
    for gateway in nextHopIpAddress_uniq_list:
        for subnet in addressPrefix_uniq_list:
            network = ipaddress.ip_network(subnet)
            ip = ipaddress.ip_address(gateway)
            if ip in network:
                print (gateway + " is within " + subnet)



def main(scriptname, argv):
    routingfile = ''
    script_name = 'routes_to_neo4ji.py'
    usage_msg=(script_name + ' -r <routingfile.json>')
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
          routingfile = arg
    if not routingfile:
       print(usage_msg)
       sys.exit()

    routing_tree = load_json(routingfile)

    print ("############### Routing Gateways:")
    nextHopIpAddress_uniq_list = get_uniq_nextHopIpAddress(routing_tree)
#    print (nextHopIpAddress_uniq_list)
    print ("############### Routing Subnets:")
    addressPrefix_uniq_list = get_uniq_addressPrefix(routing_tree)
#    print (addressPrefix_uniq_list)

    nextHopIpAddress_uniq_list = np.delete(nextHopIpAddress_uniq_list, np.argwhere(nextHopIpAddress_uniq_list == ''))

    pw = getpass.getpass()
    conn_string = "bolt://neo4j:" + pw + "@localhost:7687"
    current_graph = Graph(conn_string)
    tx = current_graph.begin()
    clear_graph_database(current_graph)
    print ("Cleared neo4j db")

    push_nextHopIpAddress_to_neo4j(nextHopIpAddress_uniq_list, tx)
    tx.commit()
    print ("Pushed nextHopIpAddress_uniq_list to neo4j")
    tx = current_graph.begin()
    push_addressPrefix_to_neo4j(addressPrefix_uniq_list, tx)
    tx.commit()
    print ("Pushed addressPrefix_uniq_list to neo4j")

    tx = current_graph.begin()
    create_default_gw_connection_in_neo4j(routing_tree, current_graph, tx)
    tx.commit()
    print ("Pushed gw-subnet connections to neo4j")

    # check, if a gateway is in a subnet so we can draw a connection between gateway and subnet
#    tx = current_graph.begin()
#    nextHopIpAddress_uniq_list = np.delete(nextHopIpAddress_uniq_list, np.argwhere(nextHopIpAddress_uniq_list == ''))
#    addressPrefix_uniq_list = np.delete(addressPrefix_uniq_list, np.argwhere(addressPrefix_uniq_list == '0.0.0.0/0'))
#    create_gateway_to_subnet_connection_in_neo4j(nextHopIpAddress_uniq_list, addressPrefix_uniq_list, tx)
#    tx.commit()
    


if __name__ == "__main__":
    main(argv[0], sys.argv[1:])

