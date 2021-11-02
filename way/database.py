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
def getCoordinateID(pointid):
    query = "SELECT ST_X(pt), ST_Y(pt) from (SELECT geom AS pt from {nutgiaothong} WHERE pointid={pointid}) AS layerP"\
        .format(nutgiaothong=nutgiaothong, pointid=pointid)
    return getData(query)


def getCoordinate():
    query = "SELECT pointID, ST_X(geom), ST_Y(geom) FROM {nutgiaothong}".format(nutgiaothong=nutgiaothong)
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
    query_segClosest = "SELECT ST_Distance(pt, geom) AS distance, fromID, toID " \
                         f"FROM (SELECT ST_GeomFromText({pointClick_str}, {srid}) As pt, geom, fromID, toID FROM {doanduong}) as ttt " \
                         "ORDER BY distance ASC limit 1"
    segClosest = getData(query_segClosest)[0]
    pointIDClosest = [segClosest[1], segClosest[2]]

    query_segClosest = "SELECT ST_Distance(pt, geom) AS distance, pointID " \
                       f"FROM (SELECT ST_GeomFromText({pointClick_str}, {srid}) As pt, geom, pointID FROM {nutgiaothong} " \
                       f"WHERE pointID={pointIDClosest[0]} OR pointID={pointIDClosest[1]}) as ttt " \
                       "ORDER BY distance ASC limit 1"

    # Lấy về pointid của điểm tương ứng trong layer nutgiaothong
    # query_idpointClosest = f"SELECT pointID FROM {nutgiaothong} WHERE geom = '{pointClosest}'"
    pointID = getData(query_segClosest)

    return pointID[0][1]


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


def exportGeoJSON(segs):
    numSegs = len(segs)
    cod = ""
    for item in range(numSegs - 1):
        cod = cod + "SegmentId=" + str(segs[item]) + " OR "
    cod = cod + "SegmentId=" + str(segs[numSegs-1])

    query_geojson = f"SELECT ST_AsGeoJSON(s.*) FROM " \
                    f"(SELECT dd.tenduong as f2, ST_Length(dd.geom) as f3, dd.geom FROM {doanduong} AS dd " \
                        f"WHERE {cod}) AS s"

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
            f"lines as (select 1 as id, geom, tenduong from {doanduong} where (fromID='{_node}' AND toID='{_nodeNext}') OR (fromID='{_nodeNext}' AND toID='{_node}') LIMIT 1), " \
            f"temp_table1 AS (SELECT a.id,ST_ClosestPoint(ST_Union(b.geom), a.geom)::geometry AS geom " \
            f"FROM points a, lines b GROUP BY a.geom,a.id), " \
            f"temp_table2 AS (SELECT 1 AS id, ST_Union(MyST_AsMultiPoint(geom))::geometry AS geom FROM lines), " \
            f"temp_table3 AS (SELECT b.id, ST_snap(ST_Union(b.geom),a.geom, ST_Distance(a.geom,b.geom)*1.01)::geometry AS geom " \
            f"FROM temp_table2 a, temp_table1 b " \
            f"GROUP BY a.geom, b.geom, b.id), " \
            f"temp_table4 AS (SELECT (ST_Dump(ST_split(st_segmentize(a.geom,1),ST_Union(b.geom)))).geom::geometry AS geom, a.tenduong FROM lines a, temp_table3 b " \
            f"GROUP BY a.geom, a.tenduong) " \
            f"SELECT ST_AsGeoJSON((t4.geom, t4.tenduong, ST_Length(t4.geom))), ST_AsText(ST_StartPoint(geom)), ST_AsText(ST_EndPoint(geom)) FROM temp_table4 AS t4;"

    query_coorPoint = f"SELECT ST_AsText(geom) FROM (SELECT geom FROM {nutgiaothong} WHERE pointID={_nodeNext}) as qr"

    data = getData(query)
    coorP = getData(query_coorPoint)

    final = []

    # data là đoạn đã cắt làm 2
    # kiểm tra trong 2 đoạn, để xem đoạn nào cần dùng
    # đồng thời trả về điểm gần nhất (closest)
    for item in data:
        if item[1] == coorP[0][0]:
            query_line = f"SELECT ST_AsGeoJSON((s.geom, 'noname', ST_Length(s.geom))) FROM " \
                        f"(SELECT ST_MakeLine(ST_GeomFromText('POINT({_click.X} {_click.Y})'), ST_GeomFromText('{item[2]}')) AS geom) AS s"
            line_made = getData(query_line)
            return [tuple([item[0]])], line_made[0]
        elif item[2] == coorP[0][0]:
            query_line = f"SELECT ST_AsGeoJSON((s.geom, 'noname', ST_Length(s.geom))) FROM " \
                        f"(SELECT ST_MakeLine(ST_GeomFromText('POINT({_click.X} {_click.Y})'), ST_GeomFromText('{item[1]}')) AS geom) AS s"
            line_made = getData(query_line)
            return [tuple([item[0]])], line_made[0]
        else:
            final.append(tuple([item[0]]))
    return final, None
