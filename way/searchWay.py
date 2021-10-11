from . import Graph
from . import database as db
from . import Node
import json

MAX_VALUE = Node.MAX_LENGTH


# Return way from p_end to p_start is string id_end > id1 > id2 > ... >
# Không chứa id_start
# id của các node kết quả trả về tương ứng với giá trị pointid trong bảng nutgiaothong
# Input: pid_start and pid_end is ID of node start and end (node closest the clicked point)
# Nhãn (minDist): trọng số nhỏ nhất để đến điểm đó
def dijkstra(graph, pid_start, pid_end):
    try:
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
                    _status = minNode.status[j]

                    if _status == True and nextNode is not None:
                        if not nextNode.isVisited and minNode.minDist != MAX_VALUE and \
                                minNode.minDist + minNode.weight[j] < nextNode.minDist:
                            nextNode.minDist = minNode.minDist + minNode.weight[j]
                            nextNode.preResult = id_min
                            nodeValue.append(nextNode)

                            if nextNode.id == pid_end:
                                result = str(pid_end) + ">"
                                temp = graph.getNode(pid_end)
                                while temp.id != pid_start:
                                    temp = graph.getNode(temp.preResult)
                                    result = result + str(temp.id) + ">"

                                return result
    except:
        return -1


def run(point_start, point_end):
    start = Node.Point(point_start[0], point_start[1])
    end = Node.Point(point_end[0], point_end[1])

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

    try:
        node_result = dijkstra(graph, node_start, node_end)
        nodes = node_result.split('>')
        nodes.remove('')
        numNodes = len(nodes)

        seg_start, line_start = db.query_split_select(start, node_start, int(nodes[numNodes-2]))
        seg_end, line_end = db.query_split_select(end, node_end, int(nodes[1]))
        list_dataGeojson = db.exportGeoJSON(nodes)

        list_dataGeojson.extend(seg_start)
        list_dataGeojson.extend(seg_end)

        # Dữ liệu trả về là danh sách dạng GeoJSON tuple
        # Duyệt từng hàng, chuyển dữ liệu từng đoạn về dạng json, lưu lại thành 1 danh sách trả về client
        # Phía client nhận được có nhiệm vụ phân rã final_GeoJSON này ra để thành lập format GeoJSON cuối cùng phục vụ
        # cho hiển thị
        for row in list_dataGeojson:
            final_GeoJSON.append(json.loads(row[0]))

        final_GeoJSON.append(json.loads(line_start[0]))
        final_GeoJSON.append(json.loads(line_end[0]))

        return final_GeoJSON

    except:
        return -1
