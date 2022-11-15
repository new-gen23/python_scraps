#pip3 install neo4j-driver py2neo
# acquire data with cloudmapper or aws ec2 describe-subnets > aws_subnets.json

from types import SimpleNamespace
    

import neo4j
import py2neo
import sys,getopt
import json
import numpy as np # used to uniq python lists
import ipaddress
import getpass
from sys import argv

from py2neo import Graph, Node, Relationship, NodeMatcher

subnetfile = ''

def load_json(filename):
    with open(filename) as f:
        #jsontree = json.load(f)
        try:
            mynamespace = json.load(f,object_hook=lambda d: SimpleNamespace(**d) )
            for i in mynamespace.Subnets:
                print (i.CidrBlock)
        except:
            print ("Json Parsing Failed")
    return mynamespace

#    if len(jsontree) > 0:
#        return jsontree
#    else:
#        print('Json Parse Failure.')

def SubnetsToNeo4j(ns_subnets, neo4j_tx):
    subnetIpAddress_list = []
    for item in ns_subnets.Subnets:
        #print(item['CidrBlock'])
#        print(item)
        subnetIpAddress_list.append(item.CidrBlock)
        print (item.SubnetId)
        print (item.CidrBlock)
        #mynode = Node("subnet", name=item.SubnetId, subnet=item.CidrBlock, VpcId=item.VpcId)
        mynode = Node("subnet", name=item.CidrBlock, SubnetId=item.SubnetId, VpcId=item.VpcId)
        neo4j_tx.create(mynode)
    print ("Number of subnets     :" + str(len(subnetIpAddress_list)))
    print ("Number of uniq subnets:" + str(len(np.unique(subnetIpAddress_list))))
    return np.unique(subnetIpAddress_list)


#def get_uniq_SubnetIpAddress(subnettree):
#    subnetIpAddress_list = []
#    for item in subnettree['Subnets']:
#        #print(item['CidrBlock'])
#        print(item)
#        subnetIpAddress_list.append(item['CidrBlock'])
#    print ("Number of subnets:" + str(len(np.unique(subnetIpAddress_list))))
#    return np.unique(subnetIpAddress_list)

#def get_uniq_addressPrefix(subnettree):
#    addressPrefix_list = []
#    for item in subnettree:
#        for route in item['properties']['routes']:
#            try:
#  #             print(route['properties']['addressPrefix'])
#                addressPrefix_list.append(route['properties']['addressPrefix'])
#            except:
##                print(route['name'] + " has no addressPrefix")
#                continue
#    print ("Number of subnets:" + str(len(np.unique(addressPrefix_list))))
#    return np.unique(addressPrefix_list)
#
def clear_graph_database(graph):
    graph.run("MATCH (n) DETACH DELETE n")

def push_SubnetIp_to_neo4j(subnetIpAddress_uniq_list, tx):
    for item in subnetIpAddress_uniq_list:
        mynode = Node("subnet", name=item)
        tx.create(mynode)
#
#def push_addressPrefix_to_neo4j(addressPrefix_uniq_list, tx):
#    for item in addressPrefix_uniq_list:
#        mynode = Node("SUBNET", name=item)
#        tx.create(mynode)
#
#def create_default_gw_connection_in_neo4j(subnettree, current_graph, tx):
#    matcher = NodeMatcher(current_graph)
#
#    for item in subnettree:
#        for route in item['properties']['routes']:
#            try:
#                gateway_node = matcher.match("gwIP", name=route['properties']['subnetIpAddress']).first()
#                subnet_node = matcher.match("SUBNET", name=route['properties']['addressPrefix']).first()
#            except:
##                print ("Subnet most likely had no gateway. they remain in neo4j but have no relation to a gateway")
#                continue
#            if(gateway_node != None and subnet_node != None):
#                relation = Relationship(gateway_node, "routes", subnet_node)
#                tx.create(relation)
#           #    print ("relation created")
#            else:
#                print ("gateway or subnet is empty")
#
#def create_gateway_to_subnet_connection_in_neo4j(subnetIpAddress_uniq_list, addressPrefix_uniq_list, tx):
#    #matcher = NodeMatcher(current_graph)
#    print("#################")
#    print(subnetIpAddress_uniq_list)
#    print("#################")
#    print(addressPrefix_uniq_list)
#    for gateway in subnetIpAddress_uniq_list:
#        for subnet in addressPrefix_uniq_list:
#            network = ipaddress.ip_network(subnet)
#            ip = ipaddress.ip_address(gateway)
#            if ip in network:
#                print (gateway + " is within " + subnet)
#
#

def main(scriptname, argv):
    subnetfile = ''
    script_name = 'aws_subnets_to_neo4ji.py'
    usage_msg=(script_name + ' -r <subnetfile.json>')
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
          subnetfile = arg
    if not subnetfile:
       print(usage_msg)
       sys.exit()

    ns_subnets = load_json(subnetfile)

    pw = getpass.getpass()
    conn_string = "bolt://neo4j:" + pw + "@localhost:7687"
    current_graph = Graph(conn_string)
    tx = current_graph.begin()
    clear_graph_database(current_graph)
    print ("Cleared neo4j db")

 #   push_SubnetIp_to_neo4j(SubnetIpAddress_uniq_list, tx)
 #   tx.commit()
 #   print ("Pushed SubnetIpAddress_uniq_list to neo4j")
    
    print ("############### Subnets:")
    SubnetsToNeo4j(ns_subnets, tx)

    tx.commit()
#    for i in SubnetIpAddress_uniq_list:
#        print (i)



if __name__ == "__main__":
    main(argv[0], sys.argv[1:])

