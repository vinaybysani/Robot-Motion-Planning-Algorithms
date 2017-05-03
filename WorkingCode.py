import ast, math, operator
import matplotlib.pyplot as plt
import math

# Refs
# http://paulbourke.net/geometry/polygonmesh/
# Implementation : https://www.cs.cmu.edu/~motionplanning/lecture/Chap6-CellDecomp_howie.pdf


class configuration_space:
    def __init__(self, FILE_NAME):
        self.polygons = []
        self.edges = []
        self.vertices = []
        self.top_border = []
        self.bottom_border = []
        self.decomposition_lines = []
        self.regions = []
        self.centroids = [] #centroid of regions
        self.decomposition_line_mid_point = []
        self.adjacency_graph = []
        self.vertice_decompLines_map = {}
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

                    self.decomposition_lines.append([temp[0],temp[3]])
                    self.decomposition_lines.append([temp[1],temp[2]])
                elif line_ctr in range(2, num_lines):
                    self.polygons.append(list(ast.literal_eval(l)))
                else:
                    temp = list(ast.literal_eval(l))
                    self.start_state = temp[0]
                    self.goal_state = temp[1]

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

class VerticalCellDecomposition:
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

    def construct_cells(self):
        polygon_points = [item for sublist in self.cspace.polygons for item in sublist]
        polygon_points.sort(key=lambda tup: tup[0])
        cspace.plot_config_space(showPlot=False)
        plt.plot([polygon_points[0][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        plt.plot([polygon_points[-1][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        for i in range(1, len(polygon_points) - 1):
            pass
        plt.show()


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

    def check_point_lies_on_polygon(self,x,y,polygon):
        vertices = []
        for vertex in polygon:
            vertices.append(vertex)

        edges = []
        for i in range(0, len(vertices)):
            # Edges
            if (i != len(vertices) - 1):
                edges.append([vertices[i], vertices[i + 1]])
            else:
                edges.append([vertices[i], vertices[0]])

        # distance between point1, point2
        def distance(p1, p2):
            return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

        poi = [x,y]
        for edge in edges:
            p1 = edge[0]
            p2 = edge[1]
            if (abs((distance(p1, p2) - (distance(p1, poi) + distance(poi, p2)))) < 0.1):
                return True
        return False

    def decomposition_lines(self,vertex,verticalLine,poiList,top):
        for edge in cspace.edges:
            if (vertex not in edge):  # exclude edges containing the self vertex
                poi = self.line_intersection(verticalLine, edge)
                if (poi is not None):
                    poiList.append(poi)
        # print("v-", vertex, "poi-", poiList)

        # Find nearest point of intersection
        nearestPoi = poiList[0]
        for i in range(1, len(poiList)):
            if(top):
                if (poiList[i][1] < nearestPoi[1]):
                    nearestPoi = poiList[i]
            else:
                if (poiList[i][1] > nearestPoi[1]):
                    nearestPoi = poiList[i]

        decomp_line = True
        # Check if "nearest poi" falls on same polygon => ignore the vertical line
        for polygon in cspace.polygons:
            if (vertex in polygon):
                if (self.check_point_lies_on_polygon(nearestPoi[0], nearestPoi[1],
                                                     polygon)):  # returs true if "nearest poi" is on same polygon
                    # print("Not possible")
                    decomp_line = False

        if (decomp_line):
            cspace.decomposition_lines.append([vertex, nearestPoi])

            # create vertice_decompLines_map {vertex : poiList}
            if vertex in cspace.vertice_decompLines_map: # mapping already present
                cspace.vertice_decompLines_map[vertex] = [cspace.vertice_decompLines_map[vertex][0], [vertex, nearestPoi]]
            else:
                cspace.vertice_decompLines_map[vertex] = [[vertex, nearestPoi]]

    # Iterate over all edges for each vertex
    def vertical_lines(self):
        for vertex in cspace.vertices:
            # TopLine
            top = True
            poiList = [(vertex[0], cspace.top_border[0][1])]  # considering the intersection point on border
            verticalLine = [vertex, (vertex[0], cspace.top_border[0][1])]
            self.decomposition_lines(vertex,verticalLine,poiList,top)

            # BottomLine
            top = False
            poiList = [(vertex[0], cspace.bottom_border[0][1])]  # considering the intersection point on border
            verticalLine = [vertex, (vertex[0], cspace.bottom_border[0][1])]
            self.decomposition_lines(vertex, verticalLine, poiList,top)

            # print(cspace.decomposition_lines)

    def decomposition_line_mid_point(self):
        for line in cspace.decomposition_lines:
            p1 = line[0] # point1
            p2 = line[1] # point 2
            cspace.decomposition_line_mid_point.append([p1[0], (p1[1]+p2[1])/2.0])

    # up = True for up, False for down
    def find_region_line(self, str, i, vertex, otherVertex):
        fullY = cspace.top_border[0][1]
        zeroY = cspace.bottom_border[0][1]


        if(str is "middle"):
            for nextV in cspace.vertices[i:]:  # nextVertex
                for k in range(0, len(cspace.vertice_decompLines_map[nextV])):
                    otherVertexNextV = cspace.vertice_decompLines_map[nextV][k][1]
                    # print nextV,"ot",otherVertexNextV
                    if (otherVertexNextV[1] not in (fullY, zeroY)):  # middle line, not intersecting with top/bottom border
                        if ((vertex[1] <= nextV[1] <= otherVertex[1]) or
                                (vertex[1] <= otherVertexNextV[1] <= otherVertex[1]) or
                                (nextV[1] <= vertex[1] <= otherVertexNextV[1]) or
                                (nextV[1] <= otherVertex[1] <= otherVertexNextV[1]) or
                                (vertex[1] >= nextV[1] >= otherVertex[1]) or
                                (vertex[1] >= otherVertexNextV[1] >= otherVertex[1]) or
                                (nextV[1] >= vertex[1] >= otherVertexNextV[1]) or
                                (nextV[1] >= otherVertex[1] >= otherVertexNextV[1])):
                            return [nextV, otherVertexNextV]


        # if Up, check with 'up Yval', else down
        if(str is "up"):
            yVal = fullY
        elif(str is "down"):
            yVal = zeroY

        if((str is "up") or (str is "down")):
            # iterate over next vertices
            for nextV in cspace.vertices[i:]:

                # iterate over its decomposition lines
                for j in range(0,len(cspace.vertice_decompLines_map[nextV])):
                    otherVertex = cspace.vertice_decompLines_map[nextV][j][1]
                    if (otherVertex[1] == yVal):
                        return [nextV, otherVertex]

        return []


    def region_centroid(self):
        for region in cspace.regions:
            x = 0
            y = 0
            for point in region:
                x += point[0]
                y += point[1]
            x = x/4.0
            y = y/4.0
            cspace.centroids.append((x,y))


    def region_disection(self):
            fullY = cspace.top_border[0][1]
            zeroY = cspace.bottom_border[0][1]

            # sort vertices based on first value in tuple(x-coordinate)
            cspace.vertices = sorted(cspace.vertices, key=lambda x: x[0])

            fVertex = cspace.vertices[0] # first vertex
            lVertex = cspace.vertices[-1] # last vertex
            fv1 = cspace.vertice_decompLines_map[fVertex][0][1]
            fv2 = cspace.vertice_decompLines_map[fVertex][1][1]
            lv1 = cspace.vertice_decompLines_map[lVertex][0][1]
            lv2 = cspace.vertice_decompLines_map[lVertex][1][1]
            firstCell = [cspace.bottom_border[0], cspace.top_border[1], fv1, fv2]
            lastCell =  [cspace.top_border[0], cspace.bottom_border[1], lv1, lv2]
            cspace.regions.append(firstCell)
            cspace.regions.append(lastCell)

            # Iterate over vertices
            for i in range(0, len(cspace.vertices)-1):
                vertex = cspace.vertices[i]

                # iterate over its decomposition lines
                for j in range(0,len(cspace.vertice_decompLines_map[vertex])):
                    otherVertex = cspace.vertice_decompLines_map[vertex][j][1]

                    # check if both vertices are having both up and down
                    nextV = cspace.vertices[i+1]  # nextVertex
                    if(len(cspace.vertice_decompLines_map[nextV])>1):
                        otherVertexNextV = cspace.vertice_decompLines_map[nextV][j][1]
                    #
                        if(len(cspace.vertice_decompLines_map[vertex]) == 2 and len(cspace.vertice_decompLines_map[nextV]) == 2):
                            ov1 = cspace.vertice_decompLines_map[vertex][0][1]
                            ov2 = cspace.vertice_decompLines_map[vertex][1][1]
                            ov3 = cspace.vertice_decompLines_map[nextV][0][1]
                            ov4 = cspace.vertice_decompLines_map[nextV][1][1]

                            if((ov1[1] in (fullY, zeroY)) and
                                   (ov2[1] in (fullY, zeroY)) and
                                        (ov3[1] in (fullY, zeroY)) and
                                            (ov4[1] in (fullY, zeroY))):
                                cspace.regions.append([ov1, ov2, ov3, ov4])
                                continue


                    if(otherVertex[1] == fullY): # upper line
                        cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+self.find_region_line("up", i+1, vertex, otherVertex))

                    elif(otherVertex[1] == zeroY): # lower line
                        cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+self.find_region_line("down", i+1, vertex, otherVertex))

                    else: # middle
                        lst = self.find_region_line("middle", i + 1, vertex, otherVertex)
                        if(len(lst) > 0):
                            cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+lst)
                            # TODO, do not remove the comment below
                            # print(cspace.vertice_decompLines_map[vertex][j]+lst)


    # distance between two points
    def dist_btw_two_points(self,p1,p2):
        distance = math.sqrt( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 )
        return  distance

    def adjacency_graph(self):

        # TODO : bruteforce solution to remove midpoint to left and right border
        cspace.decomposition_line_mid_point = cspace.decomposition_line_mid_point[2:]

        # join start-point to its region's centroid
        point = cspace.start_state
        for point in (cspace.start_state, cspace.goal_state):
            for centroid in cspace.centroids:
                brk = False
                graph_line = [centroid, point]
                # check intersection with any of (edges, decomposition lines)

                for line in cspace.edges+cspace.decomposition_lines:
                    if(self.line_intersection(graph_line, line) is not None):
                        brk = True
                        break

                if(brk):
                    # cspace.adjacency_graph.append(graph_line)
                    continue

                cspace.adjacency_graph.append(graph_line)
                break

        print point

        for centroid in cspace.centroids:
            for mid_point in cspace.decomposition_line_mid_point:
                skip = False
                graph_line = [centroid, mid_point]
                # check if line joining centroid and mid_point intersects with any of (edges, decomposition lines)

                # check with edges
                for edge in cspace.edges:
                    if(self.line_intersection(graph_line, edge) is not None):
                        skip = True
                        break

                if(skip):
                    continue

                # check with decomposition lines
                for decomposition_line in cspace.decomposition_lines:
                    insersection_point = self.line_intersection(graph_line, decomposition_line)
                    if((insersection_point is not None) and (self.dist_btw_two_points(insersection_point, mid_point) != 0)):
                        skip = True
                        break

                if(skip):
                    continue

                cspace.adjacency_graph.append(graph_line)



if __name__ == "__main__":
    cspace = configuration_space("input.txt")
    vcd = VerticalCellDecomposition(cspace)
    vcd.generate_edges_vertices()
    vcd.vertical_lines()
    vcd.decomposition_line_mid_point()
    vcd.region_disection()
    vcd.region_centroid()
    vcd.adjacency_graph()

    cspace.vcd_plot()