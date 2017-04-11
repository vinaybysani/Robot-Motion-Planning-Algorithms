import ast, math, operator
import matplotlib.pyplot as plt

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
        self.decomposition_line_mid_point = []
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

        for i in range(len(self.polygons)):
            self.plot_polygon(self.polygons[i])

        for line in cspace.decomposition_lines:
            x = [line[0][0],line[1][0]]
            y = [line[0][1],line[1][1]]
            plt.plot(x,y,'b')
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

    def region_disection(self):
        print cspace.decomposition_lines
    #     # self.sort_points_based_on_x()

    def decomposition_line_mid_point(self):
        print cspace.decomposition_lines
        for line in cspace.decomposition_lines:
            p1 = line[0] # point1
            p2 = line[1] # point 2
            cspace.decomposition_line_mid_point.append([p1[0], (p1[1]+p2[1])/2.0])
        print cspace.decomposition_line_mid_point

if __name__ == "__main__":
    cspace = configuration_space("input.txt")
    # print(cspace.polygons)
    # print(cspace.start_state)
    # print(cspace.boundary)
    vcd = VerticalCellDecomposition(cspace)
    vcd.generate_edges_vertices()
    vcd.vertical_lines()
    vcd.decomposition_line_mid_point()
    # vcd.region_disection()
    # vcd.sort_points_base d_on_x()



    cspace.vcd_plot()
    # vcd.construct_cells()
    # vcd.line_intersection([(33,40)(67,55)],[(33,40)(33,200)])


    # vcd.check_point_lies_on_polygon(01, 0.1,[[0,0],[1,0],[1,1],[0,1]])
