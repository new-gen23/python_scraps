#pip3 install neo4j-driver py2neo


import neo4j
import py2neo
import json
import sys
import pyyed

from py2neo import Graph, Node, Relationship, NodeMatcher

def main():
    g = pyyed.Graph()

    print("Neo4j password:")
     pw = getpass.getpass()
    current_graph = Graph("bolt://neo4j:"+pw+"@localhost:7687")

    nodes = NodeMatcher(current_graph)
    matches = nodes.match("gwIP").all()
    # add the uniq list of gwIP's
    for node in matches:
        print(node['name'])
        gwIP = str(node['name'])
        g.add_node(gwIP,shape_fill="#3333FF", width="120")
#
    matches2 = nodes.match("SUBNET").all()
    # add the uniq list of subnets
    for node in matches2:
#        print(node['name'])
        subnet = str(node['name'])
        g.add_node(subnet,shape_fill="#FF9900", width="120")

    # get all relations
    results = current_graph.run("Match (n)-[r]->(m) Return n,r,m").data()
    for result in results:
#        print ("GW: ")
#        print (dict(result)['n']['name'])
        gwIP = str(dict(result)['n']['name'])
#        print ("REL: ")
#        print (dict(result)['r'])
#        print ("SUBNET: ")
#        print (dict(result)['m']['name'])
        subnet = str(dict(result)['m']['name'])
#        print ("###########")
#        g.add_node(gwIP,shape_fill="#3333FF")
#        g.add_node(subnet,shape_fill="#FF9900")
        #add the relations to the graph with the already existing nodes
        g.add_edge(gwIP,subnet, label="routes to")


#        list_of_things_in_record = list(my_record)
#        print (list_of_things_in_record)
        #print (result.data())
        #print (result.items())
#        print ("Keys:")
#        print (my_record.keys())
#        print ("Values:")
#        print (my_record.values())
#        print ("Items:")
#        print (my_record.items())
#        print ("Subgraph:")
#        print (my_record.to_subgraph())
#        for entry in my_record.to_subgraph():
#            print (entry)

#    for index in range(len(dataList)):
#        for key in dataList[index]:
            #print(dataList[index][key]['name'])
    write_graphml_to_file('1.graphml', g)

def write_graphml_to_file(filename, graph):
    # To write to file:
    with open(filename, 'w') as fp:
        fp.write(graph.get_graph())
    
    print("\ncreated: \""+filename+"\"")
    print("STRG+SHIFT+V to arrange nodes vertically")


main()
