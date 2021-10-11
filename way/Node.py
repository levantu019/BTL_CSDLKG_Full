from . import database as db
import sys

MAX_LENGTH = db.sumLength() * 10


class Node:
    def __init__(self):
        self.id = 0
        self.weight = []
        self.next = []
        self.preResult = -1
        self.minDist = MAX_LENGTH
        self.isVisited = False
        # Trên lớp giao thông sẽ xuất hiện 1 số các đoạn có cùng 2 node (tạo đừng vong kín),
        # True để sử dụng đoạn đó, False để coi như khoá lại không sử dụng trong tìm đường
        # Bìa toán này sẽ đặt True cho đoạn ngắn nhất, các đoạn còn lại là False
        self.status = []


class Point:
    def __init__(self, _x, _y):
        self.X = _x
        self.Y = _y
