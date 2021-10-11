import psycopg2
import json

nutgiaothong = "nutgiaothong2"
doanduong = "doanduong2"


def connect():
    # connect_string = "dbname=TuSearchWay user=postgres password=linh01664400660 " \
    #                  "host=database-1-instance-1.csmnpeeyzsba.ap-east-1.rds.amazonaws.com port=5432"
    connect_string = "dbname=BTL user=postgres password=admin"
    conn = psycopg2.connect(connect_string)

    return conn


def getData(query):
    curs = connect().cursor()
    curs.execute(query)
    data = curs.fetchall()
    curs.close()

    return data


def executeQuery(query):
    conn = connect()
    curs = conn.cursor()
    curs.execute(query)

    curs.close()
    conn.commit()


# Return table attribute of layer
def getLayer(name):
    query = "SELECT * FROM {name}".format(name=name)
    return getData(query)


# Return layer column
def getLayerColumn(name, argsColumns):
    query = "SELECT {argsColumns} FROM {name}".format(argsColumns=argsColumns, name=name)
    return getData(query)


# Return coordinate of point
def getCoordinate(fid):
    query = "SELECT ST_X(pt), ST_Y(pt) from (SELECT geom AS pt from {nutgiaothong} WHERE gid={fid}) AS layerP".format(
        nutgiaothong=nutgiaothong, fid=fid)
    return getData(query)


# Return number of vertices on nutgiaothong
def numVertices():
    query = "SELECT COUNT(*) FROM {nutgiaothong}".format(nutgiaothong=nutgiaothong)
    return getData(query)


# Trả về id của nút gần điểm click nhất
def getIdPointClosest(pointClick):
    # Lấy hệ tạo độ
    query_SRID = "SELECT ST_SRID(geom) from (SELECT geom FROM {nutgiaothong}) AS nutgt".format(nutgiaothong=nutgiaothong)
    srid = getData(query_SRID)[0][0]

    # Tính khoảng cách từ điểm click đến tất cả các nút và chọn khoảng cách nhỏ nhất
    # từ đó lấy được đối tượng điểm gần nhất
    pointClick_str = f"'POINT({pointClick.X} {pointClick.Y})'"
    query_pointClosest = "SELECT ST_Distance(pt, geom) AS distance, geom " \
                         f"FROM (SELECT ST_GeomFromText({pointClick_str}, {srid}) As pt, geom FROM {nutgiaothong}) as ttt " \
                         "ORDER BY distance ASC limit 1"
    pointClosest = getData(query_pointClosest)[0][1]

    # Lấy về id của điểm tương ứng trong layer nutgiaothong
    # fromID và toID trong layer doanduong tham chiếu đến FID của nút trong nutgiaothong
    # vì vậy lấy được giá trị objectID rồi phải trừ đi 1
    query_idpointClosest = f"SELECT pointID FROM {nutgiaothong} WHERE geom = '{pointClosest}'"
    pointID = getData(query_idpointClosest)

    return pointID[0][0]


# Trả về tập các đoạn đường tạo từ danh sách điểm nút kết quả
def resultSegment(result):
    segments = []
    nodes = result.split('>')
    numNodes = len(nodes) - 1
    for i in range(numNodes - 1):
        point1 = nodes[i]
        point2 = nodes[i + 1]
        query_segment = f"SELECT objectID FROM {doanduong} WHERE (FromID = '{point1}' AND ToID = '{point2}') " \
                        f"OR (FromID = '{point2}' AND ToID = '{point1}') ORDER BY length ASC"
        seg = getData(query_segment)[0]
        segments.append(seg)

    return segments


# Trả về tổng chiều dài tất cả các đoạn đường
def sumLength():
    query = "SELECT SUM(ST_LENGTH(geom)) FROM {doanduong} as seg".format(doanduong=doanduong)
    data = getData(query)[0][0]

    return data


# Create table result node
def nodeTable(nodes):
    # Tạo bảng lưu giá trị các node kết quả
    query_create = "CREATE TABLE IF NOT EXISTS resultNode(" \
                   "fromID BIGINT," \
                   "toID BIGINT" \
                   ")"
    executeQuery(query_create)

    # Check nếu bảng đã có giá trị thì xoá đi
    query_delete = "DELETE FROM resultNode"
    executeQuery(query_delete)

    query_values = ""

    # Bỏ node_end vì cạnh này đã được tính riêng
    nodes.remove(nodes[0])

    numNodes = len(nodes) - 1
    for i in range(numNodes - 1):
        if i == numNodes - 2:
            query_values = query_values + f"({int(nodes[i])}, {int(nodes[i + 1])}), "
            query_values = query_values + f"({int(nodes[i + 1])}, {int(nodes[i])})"
        else:
            query_values = query_values + f"({int(nodes[i])}, {int(nodes[i + 1])}), "
            query_values = query_values + f"({int(nodes[i + 1])}, {int(nodes[i])}), "

    query_insert = "INSERT INTO resultNode(fromID, toID) VALUES" + query_values
    executeQuery(query_insert)


# Return geojson segment result
def exportGeoJSON(nodes):
    nodeTable(nodes)
    query_geojson = "SELECT ST_AsGeoJSON(geom) FROM " \
                    f"(SELECT geom FROM {doanduong} AS dd " \
                    "INNER JOIN " \
                    "resultnode AS rn " \
                    "ON dd.fromid = rn.fromid AND dd.toid = rn.toid) AS s"

    data = getData(query_geojson)

    return data


# Hàm tạo query thực hiện cắt đoạn đường tại điểm gần điểm click nhất
# Vì điểm đầu và điểm cuối là 2 nút của đoạn đường kết quả nên nó sẽ không chứa đoạn từ điểm Closest đến 2 nút đó
# Input:
#         _click: toạ độ điểm click (dạng Point (p.X, p.Y))
#         _node: node gần điểm click nhất (giá trị fid của node trong bảng nutgiaothong)
#         _nodeNext: node ngay cạnh _node trên đường kết quả
# Trong phần này có sử dụng 1 hàm đã được tạo trước đó
# Source:
#           CREATE OR REPLACE FUNCTION MyST_AsMultiPoint(geometry) RETURNS geometry AS
#                   'SELECT ST_Union((d).geom) FROM ST_DumpPoints($1) AS d;'
#                       LANGUAGE sql IMMUTABLE STRICT COST 10;
def query_split_select(_click, _node, _nodeNext):
    #
    query = "WITH " \
            f"points as (select 1 as id, ST_GeomFromText('POINT({_click.X} {_click.Y})', 32648)::geometry as geom), " \
            f"lines as (select 1 as id, geom from {doanduong} where (fromID='{_node}' AND toID='{_nodeNext}') OR (fromID='{_nodeNext}' AND toID='{_node}') LIMIT 1), " \
            f"temp_table1 AS (SELECT a.id,ST_ClosestPoint(ST_Union(b.geom), a.geom)::geometry AS geom " \
            f"FROM points a, lines b GROUP BY a.geom,a.id), " \
            f"temp_table2 AS (SELECT 1 AS id, ST_Union(MyST_AsMultiPoint(geom))::geometry AS geom FROM lines), " \
            f"temp_table3 AS (SELECT b.id, ST_snap(ST_Union(b.geom),a.geom, ST_Distance(a.geom,b.geom)*1.01)::geometry AS geom " \
            f"FROM temp_table2 a, temp_table1 b " \
            f"GROUP BY a.geom, b.geom, b.id), " \
            f"temp_table4 AS (SELECT (ST_Dump(ST_split(st_segmentize(a.geom,1),ST_Union(b.geom)))).geom::geometry AS geom FROM lines a, temp_table3 b " \
            f"GROUP BY a.geom) " \
            f"SELECT ST_AsGeoJSON(geom), ST_AsText(ST_StartPoint(geom)), ST_AsText(ST_EndPoint(geom)) FROM temp_table4;"

    query_coorPoint = f"SELECT ST_AsText(geom) FROM (SELECT geom FROM {nutgiaothong} WHERE pointID={_nodeNext}) as qr"

    data = getData(query)
    coorP = getData(query_coorPoint)

    final = []

    # data là đoạn đã cắt làm 2
    # kiểm tra trong 2 đoạn, để xem đoạn nào cần dùng
    # đồng thời trả về điểm gần nhất (closest)
    for item in data:
        if item[1] == coorP[0][0]:
            query_line = f"SELECT ST_AsGeoJSON(ST_MakeLine(ST_GeomFromText('POINT({_click.X} {_click.Y})'), ST_GeomFromText('{item[2]}')))"
            line_made = getData(query_line)
            return [tuple([item[0]])], line_made[0]
        elif item[2] == coorP[0][0]:
            query_line = f"SELECT ST_AsGeoJSON(ST_MakeLine(ST_GeomFromText('POINT({_click.X} {_click.Y})'), ST_GeomFromText('{item[1]}')))"
            line_made = getData(query_line)
            return [tuple([item[0]])], line_made[0]
        else:
            final.append(tuple([item[0]]))
    return final, None
