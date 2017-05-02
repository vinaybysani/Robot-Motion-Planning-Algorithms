import ast, math, operator
import matplotlib.pyplot as plt
import math

from configuration_space import configuration_space, Roadmap
from collections import defaultdict
from utils import *

class VerticalCellDecomposition:
    def __init__(self,cspace):
        self.cspace = cspace

        self.polygon_vertices = [item for sublist in cspace.polygons for item in sublist]

        self.polygon_edges = []

        for polygon in cspace.polygons:
            for i in range(len(polygon)):
                self.polygon_edges.append([polygon[i%len(polygon)],polygon[(i+1)%len(polygon)]])

        self.decomposition_lines = []
        self.decomposition_lines_midpts = []
        self.decomposition_lines_map = defaultdict(list)

    def construct_decomposition_lines(self,vertex,verticalLine,pointList,top):
        for edge in self.polygon_edges:
            if (vertex not in edge):  # exclude edges containing the self vertex
                point = line_intersection(verticalLine, edge)
                if point is not None: # If they intersect...
                    pointList.append(point)

        # Find nearest point of intersection
        nearest_point = pointList[0]
        for i in range(1, len(pointList)):
            if top and pointList[i][1] < nearest_point[1]:
                nearest_point = pointList[i]
            elif pointList[i][1] > nearest_point[1]:
                nearest_point = pointList[i]

        # Check if the nearest point falls on same polygon. If so, ignore the vertical line
        for polygon in cspace.polygons:
            if vertex in polygon:
                if not on_polygon(nearest_point[0], nearest_point[1], polygon): 
                    self.decomposition_lines.append([vertex, nearest_point])

                    # create vertice_decompLines_map {vertex : pointList}
                    self.decomposition_lines_map[vertex].append([vertex,nearest_point])

    # Iterate over all edges for each vertex
    def vertical_lines(self):
        for vertex in self.polygon_vertices:
            # TopLine
            top = True
            pointList = [(vertex[0], cspace.boundary[2][1])]
            verticalLine = [vertex, (vertex[0], cspace.boundary[2][1])]
            self.construct_decomposition_lines(vertex,verticalLine,pointList,top)

            # BottomLine
            top = False
            pointList = [(vertex[0], cspace.boundary[0][1])]  # considering the intersection point on border
            verticalLine = [vertex, (vertex[0], cspace.boundary[0][1])]
            self.construct_decomposition_lines(vertex, verticalLine, pointList,top)

        for line in self.decomposition_lines:
            self.decomposition_lines_midpts.append([line[0][0],(line[0][1]+line[1][1])/2.0])

    def region_disection(self):
        maxY = cspace.boundary[2][1]
        minY = cspace.boundary[0][1]

        # sort vertices based on first value in tuple(x-coordinate)
        self.polygon_vertices = sorted(self.polygon_vertices, key=lambda x: x[0])

        
        # fVertex = self.polygon_vertices[0] # first vertex
        # lVertex = self.polygon_vertices[-1] # last vertex
        # fv1 = cspace.vertice_decompLines_map[fVertex][0][1]
        # fv2 = cspace.vertice_decompLines_map[fVertex][1][1]
        # lv1 = cspace.vertice_decompLines_map[lVertex][0][1]
        # lv2 = cspace.vertice_decompLines_map[lVertex][1][1]
        # firstCell = [cspace.bottom_border[0], cspace.boundary[2][1][1], fv1, fv2]
        # lastCell =  [cspace.boundary[2][1][0], cspace.bottom_border[1], lv1, lv2]
        # cspace.regions.append(firstCell)
        # cspace.regions.append(lastCell)

        # # Iterate over vertices
        # for i in range(len(self.polygon_vertices)-1):
        #     vertex = self.polygon_vertices[i]

        #     # iterate over its decomposition lines
        #     for j in range(0,len(cspace.vertice_decompLines_map[vertex])):
        #         otherVertex = cspace.vertice_decompLines_map[vertex][j][1]

        #         # check if both vertices are having both up and down
        #         nextV = self.polygon_vertices[i+1]  # nextVertex
        #         if(len(cspace.vertice_decompLines_map[nextV])>1):
        #             otherVertexNextV = cspace.vertice_decompLines_map[nextV][j][1]
        #         #
        #             if(len(cspace.vertice_decompLines_map[vertex]) == 2 and len(cspace.vertice_decompLines_map[nextV]) == 2):
        #                 ov1 = cspace.vertice_decompLines_map[vertex][0][1]
        #                 ov2 = cspace.vertice_decompLines_map[vertex][1][1]
        #                 ov3 = cspace.vertice_decompLines_map[nextV][0][1]
        #                 ov4 = cspace.vertice_decompLines_map[nextV][1][1]

        #                 if((ov1[1] in (maxY, minY)) and
        #                        (ov2[1] in (maxY, minY)) and
        #                             (ov3[1] in (maxY, minY)) and
        #                                 (ov4[1] in (maxY, minY))):
        #                     cspace.regions.append([ov1, ov2, ov3, ov4])
        #                     continue


        #         if(otherVertex[1] == maxY): # upper line
        #             cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+self.find_region_line("up", i+1, vertex, otherVertex))

        #         elif(otherVertex[1] == minY): # lower line
        #             cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+self.find_region_line("down", i+1, vertex, otherVertex))

        #         else: # middle
        #             lst = self.find_region_line("middle", i + 1, vertex, otherVertex)
        #             if(len(lst) > 0):
        #                 cspace.regions.append(cspace.vertice_decompLines_map[vertex][j]+lst)
        #                 # TODO, do not remove the comment below
        #                 # print(cspace.vertice_decompLines_map[vertex][j]+lst)

    def construct_cells(self):
        self.polygon_vertices.sort(key=lambda tup: tup[0])
        cspace.plot_config_space(showPlot=False)
        plt.plot([self.polygon_vertices[0][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        plt.plot([self.polygon_vertices[-1][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        for i in range(1, len(self.polygon_vertices) - 1):
            pass
        plt.show()        

    # up = True for up, False for down
    def find_region_line(self, str, i, vertex, otherVertex):
        maxY = cspace.boundary[2][1][0][1]
        minY = cspace.boundary[0][1]


        if(str is "middle"):
            for nextV in self.polygon_vertices[i:]:  # nextVertex
                for k in range(0, len(cspace.vertice_decompLines_map[nextV])):
                    otherVertexNextV = cspace.vertice_decompLines_map[nextV][k][1]
                    # print nextV,"ot",otherVertexNextV
                    if (otherVertexNextV[1] not in (maxY, minY)):  # middle line, not intersecting with top/bottom border
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
            yVal = maxY
        elif(str is "down"):
            yVal = minY

        if((str is "up") or (str is "down")):
            # iterate over next vertices
            for nextV in self.polygon_vertices[i:]:

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

                for line in self.polygon_edges+self.decomposition_lines:
                    if(line_intersection(graph_line, line) is not None):
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
                for edge in self.polygon_edges:
                    if(line_intersection(graph_line, edge) is not None):
                        skip = True
                        break

                if(skip):
                    continue

                # check with decomposition lines
                for decomposition_line in self.decomposition_lines:
                    insersection_point = line_intersection(graph_line, decomposition_line)
                    if((insersection_point is not None) and (distance(insersection_point, mid_point) != 0)):
                        skip = True
                        break

                if(skip):
                    continue

                cspace.adjacency_graph.append(graph_line)



if __name__ == "__main__":
    cspace = configuration_space("input.txt")
    vcd = VerticalCellDecomposition(cspace)
    vcd.vertical_lines()
    vcd.region_disection()
    # vcd.region_centroid()
    # vcd.adjacency_graph()

    # cspace.vcd_plot()
