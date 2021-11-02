from . import database as db
import sys

MAX_LENGTH = db.sumLength() * 10


class Node:
    def __init__(self):
        self.id = 0
        self.weight = []
        self.next = []
        self.seg = []
        self.preSeg = -1
        self.preResult = -1
        self.minDist = MAX_LENGTH
        self.isVisited = False

        # Các tham số dùng cho AStar
        self.isOpen = False
        self.isClose = False
        self.h = -1
        self.f = MAX_LENGTH


class Point:
    def __init__(self, _x, _y):
        self.X = _x
        self.Y = _y
