#pip3 install neo4j-driver py2neo

from types import SimpleNamespace
    
import random,string
import sys,getopt
import json
import ipaddress
import getpass
import pyyed
from collections import deque # used for out stack
from sys import argv

from py2neo import Graph, Node, Relationship, NodeMatcher

g = pyyed.Graph()
stack = deque()

def load_json(filename):
    with open(filename) as f:
        #jsontree = json.load(f)
        try:
#            mynamespace = json.load(f,object_hook=lambda d: SimpleNamespace(**d) )
#            for i in mynamespace.Subnets:
 #               print (i.CidrBlock)
            mydict = json.load(f)
            #print(i['CidrBlock']) # = print dictionary
        except:
            print ("Json Parsing Failed")
    return mydict

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def UndefToYed(undef,g):

  if type(undef) == dict:
    for k in undef.keys():
      print(k) # create node in yed and remember parent and parent parent parent for connection
      mystr = randomword(10)
      g.add_node(mystr,label=str(k),shape_fill="#FFFFFF", width="120")
      try:
        g.add_edge(stack[-1],mystr,label="")
      except:
        print("- no parent")
      if type(undef[k]) == list:
        print("### pushed as parent:(",str(k),"): ", mystr)
        stack.append(mystr) # push parent to stack
      UndefToYed(undef[k],g)
    print ("### for ended")
    #pop parent from stack
    try:
      print ("# Parent:", parent)
      parent = stack.pop()
      g.add_edge(parent, mystr,label="")
    except:
      print ("Stack Empty")
  if type(undef) == list: # what to do with the parents and their parents and ....
    print("## should be sublist")
    for item in undef:
      UndefToYed(item,g)


def main(scriptname, argv):
    subnetfile = ''
    script_name = 'json_structure_to_yed.py.py'
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
          subnetfile = arg
    if not subnetfile:
       print(usage_msg)
       sys.exit()

    mydict = load_json(subnetfile)

#    JsonStructureToYed(mydict)
    UndefToYed(mydict,g)
    write_graphml_to_file('1.graphml', g)

def write_graphml_to_file(filename, graph):
    # To write to file:
    with open(filename, 'w') as fp:
        fp.write(graph.get_graph())
    print("\ncreated: \""+filename+"\"")
    print("STRG+SHIFT+V to arrange nodes vertically")



if __name__ == "__main__":
    main(argv[0], sys.argv[1:])


