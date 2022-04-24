import networkx as nx
import argparse
import json
import math
import markdown
import matplotlib.pyplot as plt
import pdfkit
import pandoc
import subprocess
import os
import trivium
import datetime



class victimNode:

    def __init__(self, ip):

        # Init the variables
        self.ip = ip

        # a list of paths, sorted by weight
        self.compromisePaths = []

    def addPath(self, path):

        # If first path just append
        if(len(self.compromisePaths) == 0):
            self.compromisePaths.append(path)

        else:

            # Loop through the existing paths
            for i in range(0,len(self.compromisePaths)):

                # See if the weight of the new path is higher
                # If yes, insert into list
                if(path.weight > self.compromisePaths[i].weight):
                    self.compromisePaths.insert(i, path)
                    break

            # If it is the new worst path, insert at end
            else:
                self.compromisePaths.append(path)

    def CalculateScore(self):

        # Code goes here
        return True

class compromisePath:

    # Init vars
    def __init__(self):
        self.weight = 0
        self.path = []

    # Add to path
    def addToPath(self, node):
        self.path.append(node)

    # Increase weight of path
    def addToWeight(self, weight):
        self.weight += weight

    def addToPath(self, node, weight):
        self.weight += weight
        self.path.append(node)



class Network:

    attackingNode = ""

    # Init the diagram. Data is the json data.
    def __init__(self, data, victimNodes, attackingNode, triviumData):

        # Import the graph
        self.G = nx.readwrite.node_link_graph(json.loads(data))

        # Init the attacker and the victims
        self.victimNodes = []
        for victim in victimNodes:

            # Create a new victim node and add to list
            self.victimNodes.append(victimNode(victim))

        self.attackingNode = attackingNode

        self.triviumData = triviumData


    def Sublimate(self, number_of_paths):

        paths = nx.all_simple_paths(self.G, source=ipToTid(self.attackingNode), target=ipToTid(self.victimNodes[0].ip))

        pathWeightPairs = []
        max_weight = float("-inf")
        min_weight = float("inf")
        for path in paths:
            weight = math.prod(float(self.G.nodes[node]['distill_score']) for node in path)
            pathWeightPairs.append((path,weight))
            
            if weight > max_weight:
                max_weight = weight
            if weight < min_weight:
                min_weight = weight

        pathWeightPairs.sort(key=lambda p: p[1], reverse=True)
        pathWeightPairs = pathWeightPairs[:number_of_paths]


        for victim in self.victimNodes:
            trivium_id = ipToTid(victim.ip)
            for p,w in pathWeightPairs:
                w = float((w - min_weight) / (max_weight - min_weight))
                if p[-1] != trivium_id: continue
                path_to_victim = compromisePath()
                path_to_victim.addToWeight(w)
                ipPath = list(map(tidToIp, p))
                path_to_victim.path = ipPath
                victim.addPath(path_to_victim)
                
        return True


    def MarkdownExport(self, fileName):

        # Open the file and write the header
        f = open(fileName + ".md", "w")
        f.write("# " + fileName + " Attack Traversal Report\n")
        f.close()

        # State the attacking node
        f = open(fileName+".md", "a")
        f.write("## Attacking Node: " + self.attackingNode + '\n')

        # Loop through the victims
        for victim in self.victimNodes:
            f.write("## Victim Node: " + victim.ip + '\n')

            # Edge case: if there are no paths, print notice
            if(len(victim.compromisePaths) == 0):
                f.write('#### No Paths of Compromise for This Node\n')

            else:

                # For each victim, loop through the paths and print them
                for compromisePath in victim.compromisePaths:

                    # print the markdown formatting
                    f.write("#### ")

                    # loop through the ips in the path and print arrows between them
                    for ip in compromisePath.path:
                        f.write(ip)
                        f.write("->")

                    # At the end output the ip of the victim node
                    f.write(victim.ip + '\n')

                    # Output the weight and number of nodes
                    f.write("**Weight of Path:** {:.6f}\n\n".format(compromisePath.weight))
                    f.write("**Number of Nodes in Path:** " + str(len(compromisePath.path) + 1) + "\n\n")


        f.close()

    def MermaidExport(self, fileName):

        # Create the header of the document and the summary graph
        text = ""
        victimList = ""
        header = ('<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>\n')
        summaryGraph = "# "+ str(fileName).split("/")[-1] + " Attack Traversal Report {: id=top} \n## Summary Graph\n~~~mermaid\nflowchart LR\n"
        summaryGraphCounter = {}

        # Create a set of nodes that must be listed at the end
        listedNodes = set()

        # State the attacking node
        text += "## Attacking Node: " + self.attackingNode + '\n\n'

        # Loop through the victims
        for victim in self.victimNodes:
            text += ("## Victim Node: [" + victim.ip + "](#" + victim.ip + ')\n\n')

            # Edge case: if there are no paths, print notice
            if(len(victim.compromisePaths) == 0):
                text += '#### No Paths of Compromise for This Node\n\n'

            else:

                # For each victim, loop through the paths and print them
                for compromisePath in victim.compromisePaths:

                    # Temporary Variable to store the graph
                    temp = ""

                    # Create the mermaid graph
                    text += '~~~mermaid\nflowchart LR\n'

                    # loop through the ips in the path and print arrows between them
                    i = 0
                    for i in range(len(compromisePath.path) - 1):
                        temp += compromisePath.path[i]
                        temp += "-->"
                        temp += compromisePath.path[i+1] + "\n"

                        # add the link to the last node in the chain
                        temp += 'click ' + compromisePath.path[i+1] + ' "./' + fileName + '.html#' + compromisePath.path[i+1] + '" "Link to Vulnerability Report"\n'

                        # add the effected node to the effected nodes set if applicable
                        listedNodes.add(compromisePath.path[i+1])


                        # Add one occurence to the node that is being accessed for the summaryGraph
                        if not compromisePath.path[i+1] in summaryGraphCounter:
                            summaryGraphCounter[compromisePath.path[i+1]] = 0

                        summaryGraphCounter[compromisePath.path[i+1]] += 1

                    # At the end output the path to the victim node
                    # temp += compromisePath.path[len(compromisePath.path)-1]
                    # temp += "-->"
                    # temp += (victim.ip + '\n')

                    # Attach the temp graph to the diagram in both places
                    text += temp
                    summaryGraph += temp

                    # Output the weight and number of nodes
                    text += "~~~\n\n#### Weight of Path: {:.6f}\n\n".format(compromisePath.weight)
                    text += "#### Number of Nodes in Path: " + str(len(compromisePath.path) + 1) + "\n\n"



        # Create the list of effected nodes
        for listedNode in listedNodes:

            # Create a header
            victimList += "\n##" + listedNode + " CVE Report &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; [Go back to top](#top)  {: id=" + listedNode + "} \n" 
            cves = self.G.nodes[self.ipToTid(listedNode)]['cve_info']

            for cve in cves:
                victimList += "["+cve+"](https://cve.mitre.org/cgi-bin/cvename.cgi?name="+cve+")\n\n"



        # Finish formatting the summary graph

        # Find the node with the highest weight
        if len(summaryGraphCounter) != 0:
            top = max(summaryGraphCounter, key=summaryGraphCounter.get)
            top = summaryGraphCounter[top]

        # Loop through the nodes and apply the color weighting
        for node in summaryGraphCounter:

            redness = '{:02x}'.format(int(((summaryGraphCounter[node] / top) * -255) + 255))
            redval = "FF" + redness + redness
            summaryGraph += "classDef cl" + node.replace('.','') +" fill:#" + redval + ";\n"
            summaryGraph += "class " + node + " cl" + node.replace('.','') + ";\n"
        summaryGraph += "~~~\n\n"

        # Convert the text into mermaid markdown
        html = markdown.markdown((summaryGraph + text + victimList), extensions=['md_mermaid', 'attr_list'])
        finalHtml = header + html

        # Write the markdown to disk
        f = open(fileName + ".md", "w")
        f.write((summaryGraph + text + victimList))
        f.close()


        # Write the html to disk
        f = open(fileName + ".html", "w")
        f.write(finalHtml)
        f.close()


    # Utilities
    def ipToTid(self, ip):
        trivium_id = [id for id,attributes in self.G.nodes.items() if attributes['ip'] == ip][0]
        return trivium_id
    
    
    def tidToIp(tid):
        return self.G.nodes[tid]['ip']


# Testing zone
def main():

    # initialize parser
    parser = argparse.ArgumentParser()

    # parse the arguments
    parser.add_argument("-m", "--model", type=str, help="Model Name")
    parser.add_argument("-d", "--diagram", type=str, help="Diagram Name")
    parser.add_argument("-i", "--input", type=str, help="Input ", required=True)
    parser.add_argument("-o", "--output", type=str, help="Nessus Files", required=True)
    parser.add_argument("-a", "--attacker", type=str, help="Override attacking nodes from diagram")
    parser.add_argument("-v", "--victim", type=str, help="Override victim nodes from diagram")
    parser.add_argument("-n", "--number_paths", type=int, help="Quantity of top N paths to display")
    args = parser.parse_args()

    print("Starting Sublimate at " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print()

    # Create placeholder data
    triviumData = {}
    triviumData['diagramName'] = args.diagram
    victimNodes = [args.victim]
    attackingNode = args.attacker

    # Read victim and attackers from Trivium
    if not args.victim or not args.attacker:
        if args.model and args.diagram:
            print("Reading attack and victim from Trivium...")
            print()
            
            diagramData = trivium.api.element.get(args.model, element=args.diagram)
            ids = list(diagramData["custom"]["diagramContents"].keys())
            params = {'ids' : ','.join(ids)}
            elements = trivium.api.element.get(args.model, params=params)
            actorNodes = [e for e in elements if e['type'] == 'td.systems.actor']

            if not args.attacker:
                attackingActorNodes = [actor for actor in actorNodes if actor['name'].lower() == 'start']
                if len(attackingActorNodes) != 1:
                    print('error: the attacker must be labeled with an actor named \'start\' in the diagram')
                    exit()

                # Ignore additional actors called 'start' and additional edges to nodes
                startEdgeID = attackingActorNodes[0]['sourceOf'][0]
                startNode = [node for node in elements if startEdgeID in node['targetOf']][0]
                attackingNode = startNode['custom']['properties']['ip']['value']
            if not args.victim:
                victimActorNodes = [actor for actor in actorNodes if actor['name'].lower() == 'end']
                if len(victimActorNodes) != 1:
                    print('error: the victim must be labeled with an actor named \'end\' in the diagram')
                    exit()

                # Ignore additional actors called 'end' and additional edges to nodes
                startEdgeID = victimActorNodes[0]['sourceOf'][0]
                endNode = [node for node in elements if startEdgeID in node['targetOf']][0]
                victimNodes = [endNode['custom']['properties']['ip']['value']]

        else:
            print("error: attacker or victim nodes not specified")
            exit()

    # Read in data
    print("Reading in graph data...")
    print()
    f = open(args.input, "r")
    data = f.read()
    f.close()

    print("Finding paths...")
    print()
    # Create test network
    testing = Network(data, victimNodes, attackingNode, triviumData)

    # Find paths to victims
    testing.Sublimate(args.number_paths)

    print("Outputting report...")
    print()
    # Run the export function
    testing.MermaidExport(args.output)

    print("DONE")


if __name__ == "__main__":
    main()

