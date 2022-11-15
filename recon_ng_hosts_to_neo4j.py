#pip3 install neo4j-driver py2neo

# export domains+hosts from recon-ng as json
# reads files and writes them to neo4j

from types import SimpleNamespace
    
import random,string
import sys,getopt
import json
import ipaddress
import getpass
from collections import deque # used for out stack
from sys import argv
import numpy as np

from py2neo import Graph, Node, Relationship, NodeMatcher

stack = deque()

def load_json(filename):
    json_tree = ''
    with open(filename) as f:
        try:
            json_tree = json.load(f)
        except:
            print ("Json Parsing Failed")
    return json_tree


def clear_graph_database(graph):
    graph.run("MATCH (n) DETACH DELETE n")

def UniqIPsToNeo4j(json_tree, tx):
    IpAddress_list = []
    for item in json_tree['hosts']:
        print (item['host'],":",item['ip_address'])
        IpAddress_list.append(str(item['ip_address']))

    uniq_ip_list = np.unique(IpAddress_list)
    add_uniq_ip_to_neo4j(uniq_ip_list, tx)
    return len(uniq_ip_list)

def UniqHostNamesToNeo4j(json_tree, tx):
    host_list = []
    for item in json_tree['hosts']:
        host_list.append(str(item['host']))

#    uniq_host_list = np.unique(host_list) # very slow
    uniq_host_list = sorted(set(host_list))
    add_uniq_host_to_neo4j(uniq_host_list, tx)
    return len(uniq_host_list)

def add_uniq_host_to_neo4j(uniq_host_list, tx):
    for host in uniq_host_list:
        mynode = Node("Hostname", name=str(host))
        tx.create(mynode)
    #tx.commit()
    


def add_uniq_ip_to_neo4j(uniq_ip_list, tx):
   # print (uniq_ip_list)
    for ip in uniq_ip_list:
        mynode = Node("IP", name=str(ip))
        tx.create(mynode)
    #tx.commit()
    
def add_connections(json_tree, current_graph, tx):
    con_counter = 0
    matcher = NodeMatcher(current_graph)
    for item in json_tree['hosts']:
        try:
            #mynode_ip = Node("IP", name=str(item['ip_address']))
            #mynode_hostname = Node("Hostname", name=str(item['host']))
            #found_hostname_node = matcher.match(mynode_hostname)
            #found_ip_node       = matcher.match(mynode_ip)

#            print ("searching:", str(item['host']))

            found_hostname_node = matcher.match("Hostname", name=str(item['host'])).first()
            found_ip_node       = matcher.match("IP"      , name=str(item['ip_address'])).first()
        except Exception as e:
#            print ("Something went wrong")
            print("Error:", e)
            continue
        if (found_hostname_node != None and found_ip_node != None):
            relation = Relationship(found_hostname_node, "-", found_ip_node)
            tx.create(relation)
            con_counter = con_counter +1
    return con_counter



def main(scriptname, argv):
    recon_ng_file = ''
    script_name = 'recon_ng_hosts_to_neo4j.py'
    usage_msg=(script_name + ' -r <file.json>')
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
          recon_ng_file = arg
    if not recon_ng_file:
       print(usage_msg)
       sys.exit()

    json_tree = load_json(recon_ng_file)
    
    pw = getpass.getpass()
    conn_string = "bolt://neo4j:" + pw + "@localhost:7687"
    current_graph = Graph(conn_string)
#    tx = current_graph.begin()
#    clear_graph_database(current_graph)
#    print ("Cleared neo4j db")
#
#    tx = current_graph.begin()
#    ip_counter = UniqIPsToNeo4j(json_tree, tx)
#    print ("Added IP's to neo4j: ", ip_counter )
#    tx.commit()
#
#    tx = current_graph.begin()
#    hostname_counter = UniqHostNamesToNeo4j(json_tree, tx)
#    print ("Added Host's to neo4j: ", hostname_counter)
#    tx.commit()

    tx = current_graph.begin()
    con_counter = add_connections(json_tree, current_graph, tx)
    tx.commit()
    print ("Added Relations to neo4j: ", con_counter)

if __name__ == "__main__":
    main(argv[0], sys.argv[1:])



