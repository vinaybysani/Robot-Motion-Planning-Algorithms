from sympy import *
import ast, math, operator
import matplotlib.pyplot as plt
import math
import utils

class configuration_space:
    def __init__(self, FILE_NAME):
        self.polygons = []
        self.edges = []
        self.vertices = []
        self.top_border = []
        self.bottom_border = []
        self.left_border = []
        self.right_border = []
        self.decomposition_lines = []
        self.regions = []
        self.centroids = [] #centroid of regions
        self.decomposition_line_mid_point = []
        self.adjacency_graph = []
        self.vertice_decompLines_map = {}
        self.closedList = []
        line_ctr = 0
        with open(FILE_NAME) as f:
            num_lines = sum(1 for l in f)
        with open(FILE_NAME) as f:
            for l in f:
                line_ctr += 1
                if line_ctr == 1:
                    self.boundary = list(ast.literal_eval(l))
                    temp = list(ast.literal_eval(l))
                    self.bottom_border = [temp[0],temp[1]]
                    self.top_border = [temp[2],temp[3]]
                    self.left_border = [temp[0], temp[3]]
                    self.right_border = [temp[1], temp[2]]
                    self.decomposition_lines.append([temp[0],temp[3]])
                    self.decomposition_lines.append([temp[1],temp[2]])
                elif line_ctr in range(2, num_lines):
                    self.polygons.append(list(ast.literal_eval(l)))
                else:
                    temp = list(ast.literal_eval(l))
                    self.start_state = temp[0]
                    self.goal_state = temp[1]
    def sprm_plot(self, showPlot=True):
        axes = plt.gca()
        axes.set_xlim([self.boundary[0][0], self.boundary[1][0]])
        axes.set_ylim([self.boundary[0][1], self.boundary[2][1]])
        plt.plot(self.start_state[0], self.start_state[1], marker='o', color='red')
        plt.plot(self.goal_state[0], self.goal_state[1], marker='o', color='green')

        # plot polygons
        for i in range(len(self.polygons)):
            self.plot_polygon(self.polygons[i])

        # plot adjacency graph
        for line in cspace.adjacency_graph:
            x = [line[0][0],line[1][0]]
            y = [line[0][1],line[1][1]]
            plt.plot(x,y,'y')

        plt.show()

    def plot_polygon(self, coords):
        for i in range(len(coords)):
            plt.plot(coords[i][0], coords[i][1], marker='o', color='black')
        plt.plot([elem[0] for elem in [coords[0], coords[-1]]], [elem[1] for elem in [coords[0], coords[-1]]],
                 color='black')
        for i in range(1, len(coords)):
            plt.plot([elem[0] for elem in coords[i - 1:i + 1]], [elem[1] for elem in coords[i - 1:i + 1]],
                     color='black')

    def plot_config_space(self, showPlot=True):
        axes = plt.gca()
        axes.set_xlim([self.boundary[0][0], self.boundary[1][0]])
        axes.set_ylim([self.boundary[0][1], self.boundary[2][1]])
        plt.plot(self.start_state[0], self.start_state[1], marker='o', color='red')
        plt.plot(self.goal_state[0], self.goal_state[1], marker='o', color='green')
        for i in range(len(self.polygons)):
            self.plot_polygon(self.polygons[i])
        if showPlot:
            plt.show()

    def vcd_plot(self, showPlot=True):
        axes = plt.gca()
        axes.set_xlim([self.boundary[0][0], self.boundary[1][0]])
        axes.set_ylim([self.boundary[0][1], self.boundary[2][1]])
        plt.plot(self.start_state[0], self.start_state[1], marker='o', color='red')
        plt.plot(self.goal_state[0], self.goal_state[1], marker='o', color='green')

        # plot vcd line mid points
        for point in cspace.decomposition_line_mid_point:
            plt.plot(point[0], point[1], marker='o', color='black')

        # plot region centrpids
        for point in cspace.centroids:
            plt.plot(point[0], point[1], marker='o', color='black')

        # plot polygons
        for i in range(len(self.polygons)):
            self.plot_polygon(self.polygons[i])

        # plot decomposition lines
        for line in cspace.decomposition_lines:
            x = [line[0][0],line[1][0]]
            y = [line[0][1],line[1][1]]
            plt.plot(x,y,'b')

        # plot adjacency graph
        for line in cspace.adjacency_graph:
            x = [line[0][0],line[1][0]]
            y = [line[0][1],line[1][1]]
            plt.plot(x,y,'y')

        plt.show()

class SPRM():
    def __init__(self, cspace):
        self.cspace = cspace

    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])  # Typo was here

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        # distance between point1, point2
        def distance(p1, p2):
            return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        poi = [x, y]

        # check if point falls between two points in line
        for l in [line1, line2]:
            p1 = l[0]
            p2 = l[1]

            if (abs((distance(p1, p2) - (distance(p1, poi) + distance(poi, p2)))) > 0.1):
                return None
        return x, y

    def generate_edges_vertices(self):
        for polygon in cspace.polygons:
            for i in range(0,len(polygon)):
                # Vertices
                cspace.vertices.append(polygon[i])
                # Edges
                if(i != len(polygon)-1):
                    cspace.edges.append([polygon[i], polygon[i+1]])
                else:
                    cspace.edges.append([polygon[i], polygon[0]])

    def elongationLinePoi(self, line1, line2):
        l1 = Line(Point(line1[0]), Point(line1[1]))
        l2 = Line(Point(line2[0]), Point(line2[1]))
        poi = intersection(l1 ,l2)
        if(len(poi) == 0): # no poi
            return None
        retVal = (poi[0][0], poi[0][1])
        return retVal

    def getPolygonGivenVertice(self, vertice):
        for polygon in cspace.polygons:
            if(vertice in polygon):
                return polygon

    def getMidPoint(self, vertice1, vertice2):
        return (vertice1[0]+vertice2[0])/2.0,(vertice1[1]+vertice2[1])/2.0,

    # distance between point1, point2
    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def adjacency_graph(self):
        # iterate over all vertices
        for vertice1 in cspace.vertices+[cspace.start_state, cspace.goal_state]:
            for vertice2 in cspace.vertices+[cspace.start_state, cspace.goal_state]:

                if(([vertice1,vertice2] in cspace.adjacency_graph) or ([vertice2,vertice1] in cspace.adjacency_graph)): # ignore if already present
                    continue


                # to reduce redundant checks
                if ((vertice1, vertice2) not in cspace.closedList):
                    cspace.closedList.append((vertice1, vertice2))
                    cspace.closedList.append((vertice2, vertice1))
                else:
                    continue

                if(vertice1 != vertice2): # if both vertices are not same,create a line

                    #get vertice1 and vertice2's respective polygons for future computation
                    polygon1 = self.getPolygonGivenVertice(vertice1)
                    polygon2 = self.getPolygonGivenVertice(vertice2)

                    # condition if either of polygon1 or polygon2 is None(happens with start state and goal state)
                    polygonList = []
                    if (polygon1 is not None):
                        polygonList += polygon1
                    if (polygon2 is not None):
                        polygonList += polygon2

                    # check if both points join outside the polygon and not the inside
                    if(len(polygonList)>0 and polygon1 == polygon2):
                        midPoint = self.getMidPoint(vertice1, vertice2)
                        if(not utils.on_polygon(midPoint[0], midPoint[1], polygon1)):
                            if(utils.inside_polygon(midPoint[0], midPoint[1], polygon1)):
                                continue


                    line = [vertice1, vertice2]

                    # check if line intersects any other line, if so, ignore the line
                    continueCheck = False
                    for e in cspace.edges:

                        # ignore edges having either of vertices(of line)
                        if(set(line).intersection(e)):
                            continue

                        poiCheck = self.line_intersection(line, e)
                        if(poiCheck is not None):
                            continueCheck = True
                            break

                    if(continueCheck):
                        continue


                    # check for intersection

                    # generate elongation for the above line, until it hits either of top line or bottom line, find those poi wrt top line and bottom line

                    poi1 = self.elongationLinePoi(line, cspace.top_border)
                    if(poi1 is None):
                        poi1 = self.elongationLinePoi(line, cspace.left_border)
                        poi2 = self.elongationLinePoi(line, cspace.right_border)
                    else:
                        poi2 = self.elongationLinePoi(line, cspace.bottom_border)
                    eLine = [poi1,poi2] #elongated line



                    add = True
                    # now check for intersection wrt other edges(except the edges with vertice1 or vertice2
                    for edge in cspace.edges:
                        if((vertice1 not in edge) and (vertice2 not in edge)):
                            tempPoi = self.line_intersection(eLine, edge)
                            if(tempPoi is not None):# if no poi with the edge

                                if(polygon1 is not None and polygon2 is not None):
                                    if(edge[0] in polygonList): # and also if the poi is not on either of vertice1,vertice2 polygons #TODO
                                        add = False
                                        break
                                else:
                                    if(polygon1 is None or polygon2 is None): # if any of vertice is start and goal state
                                        if(edge[0] in polygonList):
                                            if(polygon1 is None):
                                                midP = self.getMidPoint(vertice2, tempPoi)
                                                if(utils.inside_polygon(midP[0], midP[1], polygon2)):
                                                    add = False
                                            else: # polygon2 is None, implies vertex2 is of start/goal state
                                                midP = self.getMidPoint(vertice1, tempPoi)
                                                if (utils.inside_polygon(midP[0], midP[1], polygon1)):
                                                    add = False






                    if(add):
                        cspace.adjacency_graph.append(line)


if __name__ == "__main__":
    cspace = configuration_space("input.txt")
    sprm = SPRM(cspace)
    sprm.generate_edges_vertices()
    sprm.adjacency_graph()
    cspace.sprm_plot()
