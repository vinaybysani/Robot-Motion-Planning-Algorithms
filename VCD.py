import ast, math, operator
import matplotlib.pyplot as plt
import math

from configuration_space import configuration_space, Roadmap
from collections import defaultdict
from uniform_cost_search import Search
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
        self.regions = []

        self.roadmap = Roadmap()

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

    # up = True for up, False for down
    def find_region_line(self, line_type, i, vertex, current_vertex):
        maxY = cspace.boundary[2][1]
        minY = cspace.boundary[0][1]

        if line_type is "middle":
            for next_vertex in self.polygon_vertices[i:]:  # next_vertexertex
                for k in range(len(self.decomposition_lines_map[next_vertex])):
                    temp_vertex = self.decomposition_lines_map[next_vertex][k][1]
                    if (temp_vertex[1] not in (maxY, minY)):  # middle line, not intersecting with top/bottom border
                        if ((vertex[1] <= next_vertex[1] <= current_vertex[1]) or
                                (vertex[1] <= temp_vertex[1] <= current_vertex[1]) or
                                (next_vertex[1] <= vertex[1] <= temp_vertex[1]) or
                                (next_vertex[1] <= current_vertex[1] <= temp_vertex[1]) or
                                (vertex[1] >= next_vertex[1] >= current_vertex[1]) or
                                (vertex[1] >= temp_vertex[1] >= current_vertex[1]) or
                                (next_vertex[1] >= vertex[1] >= temp_vertex[1]) or
                                (next_vertex[1] >= current_vertex[1] >= temp_vertex[1])):
                            return [next_vertex, temp_vertex]


        # if Up, check with 'up Yval', else down
        elif line_type is "up":
            yVal = maxY

        elif line_type is "down":
            yVal = minY

        if line_type is "up" or line_type is "down":
            for next_vertex in self.polygon_vertices[i:]:
                # iterate over its decomposition lines
                for j in range(len(self.decomposition_lines_map[next_vertex])):
                    current_vertex = self.decomposition_lines_map[next_vertex][j][1]
                    if (current_vertex[1] == yVal):
                        return [next_vertex, current_vertex]

        return []

    def region_disection(self):
        maxY = cspace.boundary[2][1]
        minY = cspace.boundary[0][1]

        self.polygon_vertices = sorted(self.polygon_vertices, key=lambda x: x[0])

        firstCell = [cspace.boundary[0],cspace.boundary[3],self.decomposition_lines_map[self.polygon_vertices[0]][0][1],\
             self.decomposition_lines_map[self.polygon_vertices[0]][1][1]]
        lastCell =  [cspace.boundary[2],cspace.boundary[1],self.decomposition_lines_map[self.polygon_vertices[-1]][0][1],\
             self.decomposition_lines_map[self.polygon_vertices[-1]][1][1]]

        self.regions.append(firstCell)
        self.regions.append(lastCell)

        # Iterate over vertices
        for i,vertex in enumerate(self.polygon_vertices[:-1]): 
            # iterate over its decomposition lines
            for j in range(len(self.decomposition_lines_map[vertex])):
                # check if both vertices are having both up and down
                current_vertex = self.decomposition_lines_map[vertex][j][1]
                next_vertex = self.polygon_vertices[i+1]

                if(len(self.decomposition_lines_map[vertex])==2) and (len(self.decomposition_lines_map[next_vertex])==2):
                    ov = [self.decomposition_lines_map[vertex][0][1],self.decomposition_lines_map[vertex][1][1],\
                        self.decomposition_lines_map[next_vertex][0][1],self.decomposition_lines_map[next_vertex][1][1]]

                    if((ov[0][1] in (maxY, minY)) and (ov[1][1] in (maxY, minY)) and (ov[2][1] in (maxY, minY)) and \
                                    (ov[3][1] in (maxY, minY))):
                        self.regions.append(ov)
                        continue

                if(current_vertex[1] == maxY): # upper line
                    self.regions.append(self.decomposition_lines_map[vertex][j]+self.find_region_line("up", i+1, vertex, current_vertex))

                elif(current_vertex[1] == minY): # lower line
                    self.regions.append(self.decomposition_lines_map[vertex][j]+self.find_region_line("down", i+1, vertex, current_vertex))

                else: # middle
                    lst = self.find_region_line("middle", i + 1, vertex, current_vertex)
                    if(len(lst) > 0):
                        self.regions.append(self.decomposition_lines_map[vertex][j]+lst)
                        # TODO, do not remove the comment below
                        # print(self.decomposition_lines_map[vertex][j]+lst)

        self.roadmap.vertices_dict[0] = list(self.cspace.start_state)
        self.roadmap.vertices_dict[1] = list(self.cspace.goal_state)

        for i,region in enumerate(self.regions):
            c_x = 0
            c_y = 0

            for point in region:
                c_x += point[0]/float(len(region))
                c_y += point[1]/float(len(region))

            self.roadmap.vertices_dict[i+2] = [c_x,c_y]

    def construct_cells(self):
        self.polygon_vertices.sort(key=lambda tup: tup[0])
        cspace.plot_config_space(showPlot=False)
        plt.plot([self.polygon_vertices[0][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        plt.plot([self.polygon_vertices[-1][0]] * 2, [self.cspace.boundary[0][1], self.cspace.boundary[2][1]], color='blue')
        for i in range(1, len(self.polygon_vertices) - 1):
            pass
        plt.show()        

    def adjacency_graph(self):
        self.decomposition_lines_midpts = self.decomposition_lines_midpts[2:]


        for i,point in enumerate([self.cspace.start_state, self.cspace.goal_state]):
            for j,centroid in enumerate(self.roadmap.vertices_dict.values()[2:]):
                skip = False
                graph_line = [centroid, point]
                # check intersection with any of (edges, decomposition lines)

                for line in self.polygon_edges+self.decomposition_lines:
                    if(line_intersection(graph_line, line) is not None):
                        skip = True
                        break

                if skip:
                    continue

                self.roadmap.adjacency_dict[i].append(j+2)
                self.roadmap.edge_weights[i].append(distance(point,centroid))
                break

        for i,centroid in enumerate(self.roadmap.vertices_dict.values()[2:]):
            for j,point in enumerate(self.decomposition_lines_midpts):
                skip = False
                graph_line = [centroid, point]
                # check if line joining centroid and point intersects with any of (edges, decomposition lines)

                # check with edges
                for edge in self.polygon_edges:
                    if(line_intersection(graph_line, edge) is not None):
                        skip = True
                        break

                if skip:
                    continue

                # check with decomposition lines`
                for decomposition_line in self.decomposition_lines:
                    insersection_point = line_intersection(graph_line, decomposition_line)
                    if((insersection_point is not None) and (distance(insersection_point, point) != 0)):
                        skip = True
                        break

                if(skip):
                    continue

                if point not in self.roadmap.vertices_dict.values():
                    self.roadmap.vertices_dict[len(self.roadmap.vertices_dict.keys())] = point

                self.roadmap.adjacency_dict[i+2].append(self.roadmap.vertices_dict.values().index(point))
                self.roadmap.edge_weights[i+2].append(distance(point,centroid))

if __name__ == "__main__":
    cspace = configuration_space("input.txt")
    vcd = VerticalCellDecomposition(cspace)
    vcd.vertical_lines()
    vcd.region_disection()
    vcd.adjacency_graph()

    print vcd.roadmap.vertices_dict
    print vcd.roadmap.adjacency_dict
    ucs = Search(vcd.roadmap)
    sr = ucs.perform_search()
    print sr
    # cspace.vcd_plot()
