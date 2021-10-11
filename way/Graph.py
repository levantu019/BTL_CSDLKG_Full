from . import Node
from . import database as db
import pickle
import collections

MAX_VALUE = Node.MAX_LENGTH


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

    for i in range(1, numVertices + 1):
        item = Node.Node()
        item.id = i
        vertices.append(item)

    doanduongLayer = db.getLayerColumn('doanduong2', 'FromID, ToID, ST_Length(geom)')
    for row in doanduongLayer:
        srcID = int(row[0])
        dstID = int(row[1])
        _weight = float(row[2])

        vertices[srcID].next.append(dstID)
        vertices[srcID].weight.append(_weight)
        vertices[srcID].status.append(True)

        vertices[dstID].next.append(srcID)
        vertices[dstID].weight.append(_weight)
        vertices[dstID].status.append(True)

    graph = Graph(numVertices, vertices)

    return graph


# Các đoạn cùng chung 2 node, mở đoạn ngắn nhất, các đoạn còn lại thì khoá
def scanGraph(graph):
    for node in graph.listVertices:
        # Ở đây hàm set() chuyển list về tập có các phần tử không trùng nhau
        if len(node.next) > len(set(node.next)):
            # collections.Counter(list) trả về các giá trị trong list và số lần lặp lại của chúng
            duplicate = [key for key, value in collections.Counter(node.next).items() if value > 1]
            for item in duplicate:
                min_length = Node.MAX_LENGTH
                pos = 0
                for i in range(len(node.next)):
                    # Kiểm tra xem đỉnh kề nào có sự trùng nhau
                    # và tìm chiều dài ngắn nhất trong số các đoạn trùng nhau đó
                    # lưu vị trí (đoạn) có chiều dài ngắn nhất
                    if node.next[i] == item:
                        node.status[i] = False
                        if node.weight[i] < min_length:
                            min_length = node.weight[i]
                            pos = i
                node.status[pos] = True

    return graph


def saveGraph(graph):
    with open('data/graph1.bin', 'wb') as newfile:
        pickle.dump(graph, newfile)


def openGraph():
    try:
        with open('data/graph1.bin', 'rb') as newfile:
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