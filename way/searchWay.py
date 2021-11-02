from . import Graph
from . import database as db
from . import Node
import json
import math

MAX_VALUE = Node.MAX_LENGTH


# Return way from p_end to p_start is string id_end > id1 > id2 > ... >
# Không chứa id_start
# id của các node kết quả trả về tương ứng với giá trị pointid trong bảng nutgiaothong
# Input: pid_start and pid_end is ID of node start and end (node closest the clicked point)
# Nhãn (minDist): trọng số nhỏ nhất để đến điểm đó
def dijkstra(graph, pid_start, pid_end):
    # try:
    # Lưu danh sách các nút được gắn nhãn và chưa được xét
    nodeValue = []

    # Gán nhãn đỉnh xuất phát bằng 0
    srcNode = graph.getNode(pid_start)
    srcNode.minDist = 0.0
    nodeValue.append(srcNode)

    for i in range(graph.numVertices):
        # Tìm đỉnh có nhãn nhỏ nhất
        id_min = Graph.idMinDistance(nodeValue)
        minNode = graph.getNode(id_min)

        if minNode is not None:
            minNode.isVisited = True
            nodeValue.remove(minNode)

            # Duyệt tất cả các đỉnh kề với nó
            for j in range(len(minNode.next)):
                nextNode = graph.getNode(minNode.next[j])

                if nextNode is not None:
                    if not nextNode.isVisited and minNode.minDist != MAX_VALUE and \
                            minNode.minDist + minNode.weight[j] < nextNode.minDist:
                        nextNode.minDist = minNode.minDist + minNode.weight[j]
                        nextNode.preResult = id_min
                        nextNode.preSeg = minNode.seg[j]
                        nodeValue.append(nextNode)

                        if nextNode.id == pid_end:
                            result = str(pid_end) + ">"
                            result1 = str(nextNode.preSeg) + ">"
                            temp = graph.getNode(pid_end)
                            while temp.id != pid_start:
                                temp = graph.getNode(temp.preResult)
                                result = result + str(temp.id) + ">"
                                result1 = result1 + str(temp.preSeg) + ">"

                            return result, result1
    # except:
    #     return -1, -1


# Đặt giá trị heuristic  cho tất cả các Node
def set_h(graph, pid_end):
    # pointID, X, Y của tất cả các Node
    allNodeInfo = db.getCoordinate()

    # X, Y của node_end
    nodeEnd = db.getCoordinateID(pid_end)[0]

    # Tính khoảng cách từ mỗi Node đến Node đích và gán vào giá trị Estimates của nó
    for item in allNodeInfo:
        distance = math.sqrt((item[1] - nodeEnd[0]) ** 2 + (item[2] - nodeEnd[1]) ** 2)
        graph.listVertices[item[0]].h = distance


def AStar(graph, pid_start, pid_end):
    set_h(graph, pid_end)

    # Lưu lại danh sách các Node đang Open
    listOpen = []

    srcNode = graph.getNode(pid_start)
    srcNode.minDist = 0.0
    srcNode.f = srcNode.minDist + srcNode.h
    srcNode.isOpen = True
    listOpen.append(srcNode)

    for i in range(graph.numVertices):
        # f = g + h
        # Trong listOpen, lấy id của node có f nhỏ nhất
        idMin_f = Graph.idMin_f(listOpen)
        minNode_f = graph.getNode(idMin_f)

        minNode_f.isOpen = False
        minNode_f.isClose = True
        listOpen.remove(minNode_f)

        for j in range(len(minNode_f.next)):
            nextNode = graph.getNode(minNode_f.next[j])

            if nextNode is not None:
                if nextNode.isOpen == True and nextNode.minDist != MAX_VALUE and nextNode.minDist > minNode_f.minDist + \
                        minNode_f.weight[j]:
                    nextNode.minDist = minNode_f.minDist + minNode_f.weight[j]
                    nextNode.f = nextNode.minDist + nextNode.h
                    nextNode.preResult = idMin_f
                    nextNode.preSeg = minNode_f.seg[j]

                if nextNode.isOpen == False and nextNode.isClose == False:
                    nextNode.minDist = minNode_f.minDist + minNode_f.weight[j]
                    nextNode.f = nextNode.minDist + nextNode.h
                    nextNode.preResult = idMin_f
                    nextNode.preSeg = minNode_f.seg[j]
                    nextNode.isOpen = True
                    listOpen.append(nextNode)

                if nextNode.isClose == True and nextNode.minDist > minNode_f.minDist + minNode_f.weight[j]:
                    nextNode.isClose = False
                    nextNode.isOpen = True
                    listOpen.append(nextNode)

                if nextNode.id == pid_end:
                    result = str(pid_end) + ">"
                    result1 = str(nextNode.preSeg) + ">"
                    temp = graph.getNode(pid_end)
                    while temp.id != pid_start:
                        temp = graph.getNode(temp.preResult)
                        result = result + str(temp.id) + ">"
                        result1 = result1 + str(temp.preSeg) + ">"

                    return result, result1


def run(click_start, click_end, algorithm):
    start = Node.Point(click_start[0], click_start[1])
    end = Node.Point(click_end[0], click_end[1])

    # pointid trong bảng thuộc tính của nutgiaothong
    node_start = db.getIdPointClosest(start)
    node_end = db.getIdPointClosest(end)

    final_GeoJSON = []

    try:
        graph = Graph.openGraph()

        if graph is None:
            graph = Graph.creatGraph()
            Graph.saveGraph(graph)
    except:
        graph = Graph.creatGraph()
        Graph.saveGraph(graph)

    # try:
    if algorithm == '0':
        node_result, seg_result = dijkstra(graph, node_start, node_end)
    else:
        node_result, seg_result = AStar(graph, node_start, node_end)
    nodes = node_result.split('>')
    nodes.remove('')
    numNodes = len(nodes)

    segs = seg_result.split('>')
    segs.remove('')
    segs.remove('-1')
    numSeg = len(segs)

    seg_start, line_start = db.query_split_select(start, node_start, int(nodes[numNodes - 2]))
    seg_end, line_end = db.query_split_select(end, node_end, int(nodes[1]))

    if len(segs) > 2:
        segs.remove((segs[0]))
        segs.remove(segs[numSeg - 2])

        list_dataGeojson = db.exportGeoJSON(segs)
    else:
        list_dataGeojson = []

    list_dataGeojson.extend(seg_start)
    list_dataGeojson.extend(seg_end)

    for row in list_dataGeojson:
        final_GeoJSON.append(json.loads(row[0]))

    final_GeoJSON.append(json.loads(line_start[0]))
    final_GeoJSON.append(json.loads(line_end[0]))

    return final_GeoJSON

    # except:
    #     return -1
