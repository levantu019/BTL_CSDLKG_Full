from . import Node
from . import database as db
import pickle
import collections

MAX_VALUE = Node.MAX_LENGTH
nutgiaothong = "nutgiaothong2"
doanduong = "doanduong2"
file = 'graph'


class Graph:
    def __init__(self, _numVertices, _listVertices):
        self.numVertices = _numVertices
        self.listVertices = _listVertices

    # Return node in listVertices with id=pid
    def getNode(self, pid):
        # Cách 1: duyệt danh sách các đỉnh để tìm
        # result = None
        # for item in self.listVertices:
        #     if item.id == pid:
        #         return item

        # Cách 2: Vì khi thêm đỉnh vào danh sách thì id tương ứng bằng số thứ tự
        #       vì vậy có thể truy xuất theo STT cho nhanh
        result = self.listVertices[pid]

        return result


def creatGraph():
    numVertices = db.numVertices()[0][0]
    vertices = []

    for i in range(0, numVertices + 1):
        item = Node.Node()
        item.id = i
        vertices.append(item)

    doanduongLayer = db.getLayerColumn(f'{doanduong}', 'FromID, ToID, ST_Length(geom), SegmentId')
    for row in doanduongLayer:
        srcID = int(row[0])
        dstID = int(row[1])
        _weight = float(row[2])
        _seg = int(row[3])

        vertices[srcID].next.append(dstID)
        vertices[srcID].weight.append(_weight)
        vertices[srcID].seg.append(_seg)

        vertices[dstID].next.append(srcID)
        vertices[dstID].weight.append(_weight)
        vertices[dstID].seg.append(_seg)

    graph = Graph(numVertices, vertices)

    return graph


def saveGraph(graph):
    with open(f'data/{file}.bin', 'wb') as newfile:
        pickle.dump(graph, newfile)


def openGraph():
    try:
        with open(f'data/{file}.bin', 'rb') as newfile:
            graph = pickle.load(newfile)
            return graph
    except:
        return None


# Trả về id của node chưa được thăm và có giá trị minDist là nhỏ nhất
def idMinDistance(nodeValue):
    min = MAX_VALUE
    id_min = None

    for item in nodeValue:
        if item.isVisited == False and item.minDist < min:
            min = item.minDist
            id_min = item.id

    return id_min


def idMin_f(listOpen):
    min = MAX_VALUE
    id_min = None

    for item in listOpen:
        if item.f < min:
            min = item.f
            id_min = item.id

    return id_min