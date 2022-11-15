#!/usr/bin/python3
#pip3 install neo4j-driver py2neo

#acquire raw info with aws cli:
# aws ec2 describe-vpcs > aws_vpcs
# aws ec2 describe-network-acls > aws_network_acls.json
# aws ec2 describe-security-groups  > aws_security_groups.json
# aws ec2 describe-instances > aws_instances.json

# usage: python3 parse_aws.py -i aws_instances.json -s aws_security_groups.json

# CURRENT STATUS:
# the script does not parse acls (which can override SG's
# ports are parsed but should be rearranged in the graph between SG and ingress/egress

import neo4j
import py2neo
from py2neo import Graph, Node, Relationship, NodeMatcher


import sys, getopt
import json
from sys import argv
import ipaddress

def load_json(filename):
    with open(filename) as fh:
        jsontree = json.load(fh)
    if len(jsontree) > 0:
        return jsontree
    else:
        print ('Json Parse Failure.')

def parse_instances(jsontree, current_graph):
    for instance in jsontree['Reservations']:
        tx = current_graph.begin()
        #print (instance)
        #print(json.dumps(instance, indent=4, sort_keys=True))
        #print ('###################################################################\n')
        i_node = Node("Instance", id=instance['Instances'][0]['InstanceId'], PrivateIpAddress=instance['Instances'][0]['PrivateIpAddress'])
        tx.create(i_node)

        #print ("InstanceID: ",instance['Instances'][0]['InstanceId'])
        for sg in instance['Instances'][0]['SecurityGroups']:
            sg_node = Node("SG", GroupId=sg['GroupId'], name=sg['GroupName'])
            tx.create(sg_node)
            node_rel = Relationship(sg_node, "has", i_node)
            tx.create(node_rel)

            #print ("SecGroupId: ",sg['GroupId'], " name: ", sg['GroupName'])
        #print ("\n")
        #instance_id = instance['InstanceId']
        tx.commit()

def parse_sg(jsontree, current_graph):
    matcher = NodeMatcher(current_graph)
    for sg in jsontree['SecurityGroups']:
        tx = current_graph.begin()
        sg_node = matcher.match("SG", GroupId=sg['GroupId']).first()
        if (sg_node == None):
            sg_node = Node("SG", GroupId=sg['GroupId'], name=sg['GroupName'])
            tx.create(sg_node)
        print (sg['GroupName'])
        port_restriction = False
        ## parse ingress
        for ingress_permissions in sg['IpPermissions']:
            try:
                source_port = ingress_permissions['FromPort']
                destination_port = ingress_permissions['ToPort']
                if (source_port != None and destination_port != None):
                    port_restriction_node = Node("Port", id=destination_port, protocol=ingress_permissions['IpProtocol'], s_port=source_port, d_port = destination_port)
                elif (source_port != None):
                    port_restriction_node = Node("Port", id=destination_port, protocol=ingress_permissions['IpProtocol'], d_port=destination_port)

                tx.create(port_restriction_node)
                port_restriction = True
            except:
                print("No port restriction")


            for CidrIp in ingress_permissions['IpRanges']:
                ingress_node = matcher.match("Ingress", id=CidrIp['CidrIp']).first()
                if (ingress_node == None):
                    print ("Creating node:", CidrIp['CidrIp'])
                    ingress_node = Node("Ingress", id=CidrIp['CidrIp'])
                    tx.create(ingress_node)
                relation = Relationship(ingress_node, "ingress", sg_node)
                tx.create(relation)

                if(port_restriction == True):
                    port_relation = Relationship(ingress_node, "from_to", port_restriction_node)
                    tx.create(port_relation)

        ## parse egress
        for egress_permissions in sg['IpPermissionsEgress']:
            for CidrIp in egress_permissions['IpRanges']:
                egress_node = matcher.match("Egress", id=CidrIp['CidrIp']).first()
                if (egress_node == None):
                    print ("Creating node:", CidrIp['CidrIp'])
                    egress_node = Node("Egress", id=CidrIp['CidrIp'])
                    tx.create(egress_node)
                relation = Relationship(sg_node, "egress", egress_node)
                tx.create(relation)
            #sg_ingress_permission = Node("Ingress", id=ingress_ranges['IpRanges']['CidrIp'])
            #tx.create(sg_ingress_permission)
        tx.commit()




def clear_graph_database(graph):
    graph.run("MATCH (n) DETACH DELETE n")


def main(script_name, argv):
    print("Neo4j password:")
    pw = getpass.getpass()
    current_graph = Graph("bolt://neo4j:"+pw+"@localhost:7687")
    tx = current_graph.begin()
    clear_graph_database(current_graph)

    filename = ''
    filetype = ''
    usage_msg = (script_name + ' -i <inputfile.json>', "eg. ./aws_sg_to_neo4j.py -i aws_instances.json -s aws_security_groups.json")
    usage_msg = "\n".join(usage_msg)


    try:
        opts, args = getopt.getopt(argv,"hi:s:")
    except getopt.GetoptError:
       print (usage_msg)
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print (usage_msg)
          sys.exit()
       elif opt in ("-i"):
          filename_in = arg
       elif opt in ("-s"):
          filename_sg = arg
    if not filename_in and not filename_sg:
        print (usage_msg)
        sys.exit(2)


    #print ('Input file is ', filename)
    print (" ### Loading Instances ###")
    instance_tree = load_json(filename_in)
    parse_instances(instance_tree, current_graph)
    print ('###################################################################\n')
    print (" ### Loading SecurityGroups ###")
    sg_tree = load_json(filename_sg)
    parse_sg(sg_tree, current_graph)

    #print(tree['SecurityGroups'])

	#print blockgroup['properties']['addressPrefixes']
	#for ip_prefix in blockgroup['properties']['addressPrefixes']:
	#    db_string = group_name + ' ' + ip_prefix 
	#    #print db_string
    #    print ip_prefix
    #    net = ipaddress.ip_network(ip_prefix)
    #    print 'net[0]: ' + str(net[0]) + " Dec: " + str(int (net[0]))
    #    print 'net[max]: ' + str(net[ net.num_addresses-1 ] ) + " Dec: " + str(int(net[ net.num_addresses-1 ]))


    #print ip_prefix
if __name__ == "__main__":
    main(argv[0], sys.argv[1:])

