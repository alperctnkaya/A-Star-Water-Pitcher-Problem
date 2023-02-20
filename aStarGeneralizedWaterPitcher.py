import copy
from collections import deque
import queue


class node():
    def __init__(self, nodeLevel=None, listOfJugs=[], parentNode=None):
        self.nodeLevel = nodeLevel
        self.listOfJugs = listOfJugs  # last jug has Infinite capacity
        self.g = self.nodeLevel
        self.h = 0
        self.parentNode = parentNode

        self.jugVolumes = [jug.volume for jug in self.listOfJugs]
        self.nodeID = str(self.nodeLevel) + str(self.jugVolumes)  # Unique ID of the Node

    def computeF(self):
        self.f = self.g + self.h

        return self.f


def heuristic(node, target):
    sumOfVolumes = 0
    maxVolume = 0
    minCapacity = 2 ** 100
    for jug in node.listOfJugs[:-1]:
        if jug.volume > maxVolume:
            maxVolume = jug.volume
        if jug.capacity < minCapacity:
            minCapacity = jug.capacity

        sumOfVolumes += jug.volume

    return abs(int(target - node.listOfJugs[-1].volume - maxVolume))
    # return abs(int(target - node.listOfJugs[-1].volume - maxVolume) / minCapacity) * 2
    # return abs(int(((target - sumOfVolumes - node.listOfJugs[-1].volume) / minCapacity) * 2 ))


class jug():
    def __init__(self, capacity, volume=0):
        self.capacity = capacity
        self.volume = volume

    def fill(self, volume=None):
        if volume is None:
            self.volume = self.capacity
        else:
            self.volume = volume

    def isEmpty(self):
        if self.volume == 0:
            return True
        else:
            return False

    def isFull(self):
        if self.volume == self.capacity:
            return True
        else:
            return False

    def pour(self, volume=None):
        if volume == None:
            temp = self.volume
            self.volume = 0

            return temp
        else:
            if volume > self.volume:
                temp = self.volume
                self.volume = 0
                return temp
            else:
                self.volume = self.volume - volume
                return volume

    def availableCapacity(self):
        return self.capacity - self.volume


def pourWater(jugA, jugB):

        if jugA.volume < jugB.availableCapacity():
            jugB.volume = jugB.volume + jugA.pour()

        else:
            jugB.volume = jugB.volume + jugA.pour(jugB.availableCapacity())


def createNodes(sourceNode):
    nodes = []

    # EMPTY JUGs
    for i in range(0, len(sourceNode.listOfJugs) - 1):
        tempJugs = copy.deepcopy(sourceNode.listOfJugs)

        if tempJugs[i].isEmpty():
            continue

        else:
            tempJugs[i].pour(tempJugs[i].volume)
            newNode = node(sourceNode.nodeLevel + 1, tempJugs, parentNode=sourceNode)
            nodes.append(newNode)

    # FILL JUGs
    for i in range(0, len(sourceNode.listOfJugs) - 1):
        tempJugs = copy.deepcopy(sourceNode.listOfJugs)

        if tempJugs[i].isFull():
            continue

        else:
            tempJugs[i].fill()
            newNode = node(sourceNode.nodeLevel + 1, tempJugs, parentNode=sourceNode)
            nodes.append(newNode)

    # pour from ith jug to INF jug
    for i in range(0, len(sourceNode.listOfJugs) - 1):
        tempJugs = copy.deepcopy(sourceNode.listOfJugs)

        if tempJugs[i].isEmpty():
            continue
        else:
            pourWater(tempJugs[i], tempJugs[-1])
            newNode = node(sourceNode.nodeLevel + 1, tempJugs, parentNode=sourceNode)
            nodes.append(newNode)

    # pour from INF jug to ith jug
    for i in range(0, len(sourceNode.listOfJugs) - 1):
        tempJugs = copy.deepcopy(sourceNode.listOfJugs)

        if tempJugs[-1].isEmpty():
            continue
        else:
            pourWater(tempJugs[-1], tempJugs[i])
            newNode = node(sourceNode.nodeLevel + 1, tempJugs, parentNode=sourceNode)
            nodes.append(newNode)

    # pour water from one jug to another for every combination
    for i in range(0, len(sourceNode.listOfJugs) - 2):
        for j in range(i + 1, len(sourceNode.listOfJugs) - 1):
            tempJugs1 = copy.deepcopy(sourceNode.listOfJugs)
            tempJugs2 = copy.deepcopy(sourceNode.listOfJugs)

            # pour from ith jug to jth jug
            if tempJugs1[j].isFull() or tempJugs1[i].isEmpty():
                continue
            else:
                pourWater(tempJugs1[i], tempJugs1[j])
                newNode = node(sourceNode.nodeLevel + 1, tempJugs1, parentNode=sourceNode)
                nodes.append(newNode)

            # pour from jth jug to ith jug
            if tempJugs2[i].isFull() or tempJugs2[j].isEmpty():
                continue
            else:
                pourWater(tempJugs2[j], tempJugs2[i])
                newNode = node(sourceNode.nodeLevel + 1, tempJugs2, parentNode=sourceNode)
                nodes.append(newNode)

    return nodes


def goalTest(tempNode, target):
    if tempNode.listOfJugs[-1].volume == target:
        return True
    else:
        return False

def printNode(node):
    print("NODE LEVEL: " + str(node.nodeLevel))
    for jug in node.listOfJugs:
        print(jug.volume)

def printPath(node):
    while node.parentNode is not None:
        printNode(node)
        node = node.parentNode


def aStar(initialNode, target):
    nodeInit = initialNode

    frontier = queue.PriorityQueue()
    frontier.put((nodeInit.computeF(), 0, nodeInit))

    explored = set()
    frontierSet = dict()

    entryCounter = 1
    while (frontier.qsize() > 0):

        (currNodePriority, _, currNode) = frontier.get()

        #printNode(currNode)
        #print("CURR NODE F VAL : " + str(currNode.f))

        if currNode.f > target * 10:
            break

        # TEST The node after popping and item from priority queue
        if goalTest(currNode, target):
            goalNode = currNode
            # print(goalNode.nodeLevel)
            # printNode(currNode)

            return goalNode

        explored.add(str(currNode.jugVolumes))

        createdNodes = createNodes(currNode)

        for tempNode in createdNodes:
            tempNode.h = heuristic(tempNode, target)
            tempNode.computeF()

            if str(tempNode.jugVolumes) not in explored and str(tempNode.jugVolumes) not in frontierSet:
                frontier.put((tempNode.f, entryCounter, tempNode))
                frontierSet[str(tempNode.jugVolumes)] = tempNode.f
                entryCounter += 1
                # entryCounter is kept to have a priority over the nodes that has same f value

            elif str(tempNode.jugVolumes) in frontierSet:
                # if the node is also reachable through a shorter path
                if tempNode.f < frontierSet[str(tempNode.jugVolumes)]:
                    frontier.put((tempNode.f, entryCounter, tempNode))
                    frontierSet[str(tempNode.jugVolumes)] = tempNode.f
                    entryCounter += 1


    return -1


def mainTest(capacities, target):
    jugs = [jug(int(capacity)) for capacity in capacities]
    jugInf = jug(2 ** 100)
    jugs.append(jugInf)
    nodeInit = node(0, jugs)
    nodeInit.h = heuristic(nodeInit, target)

    result = aStar(nodeInit, target)
    if result == -1:
        return -1
    else:
        return result.nodeLevel


def test():
    assert mainTest([1,4,10,15,22], 181) == 20, "Should be 19"
    assert mainTest([2,5,6,72], 143) == 10, "Should be 10"
    assert mainTest([3,6], 2) == -1, "Should be -1"
    assert mainTest([2], 143) == -1, "Should be -1"
    assert mainTest([2,3,5,19,121,852], 11443) == 36, "Should be 36"


def main():
    file = open("input.txt", "r")
    capacities = file.readline().rstrip('\n')
    capacities = capacities.split(",")
    target = int(file.readline().rstrip('\n'))

    jugs = [jug(int(capacity)) for capacity in capacities]

    jugInf = jug(2 ** 100)

    jugs.append(jugInf)

    nodeInit = node(0, jugs)
    nodeInit.h = heuristic(nodeInit, target)

    goalNode = aStar(nodeInit, target)

    if goalNode == -1:
        print("THERE IS NO PATH AVAILABLE")
        return -1
    else:
        print(goalNode.nodeLevel)
        return goalNode.nodeLevel

if __name__ == "__main__":
    main()