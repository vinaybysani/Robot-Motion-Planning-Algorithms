import ast, math, operator
import matplotlib.pyplot as plt

from utils.configuration_space import Roadmap
from collections import defaultdict
from utils.uniform_cost_search import Search
from utils.graph_utils import *

class ShortestPathRoadmap:
	def __init__(self,cspace):
		self.cspace = cspace

		self.polygon_vertices = [item for sublist in cspace.polygons for item in sublist]

		self.polygon_edges = []

		for polygon in cspace.polygons:
		    for i in range(len(polygon)):
		        self.polygon_edges.append([polygon[i%len(polygon)],polygon[(i+1)%len(polygon)]])

		self.roadmap = Roadmap()

		for i,point in enumerate(self.polygon_vertices + [self.cspace.start_state,self.cspace.goal_state]):
			self.roadmap.vertices_dict[i] = point

	def get_polygon(self,point):
		for polygon in self.cspace.polygons:
			if point in polygon:
				return polygon

	def construct_graph(self):
		for i,pt1 in self.roadmap.vertices_dict.iteritems():
			for j,pt2 in self.roadmap.vertices_dict.iteritems():
				if pt1 != pt2:
					polygon1 = self.get_polygon(pt1)
					polygon2 = self.get_polygon(pt2)

					if polygon1 == polygon2 and polygon2 is not None and polygon1 is not None:
						midpt = [(pt1[0]+pt2[0])/2.0,(pt1[1]+pt2[1])/2.0,]
						if not on_polygon(midpt[0],midpt[1],polygon1) and inside_polygon(midpt[0],midpt[1],polygon1):
							continue

					line = [pt1,pt2]

					check = False
					for edge in self.polygon_edges:
						if set(line).intersection(edge):
							continue
						if line_intersection(line,edge) is not None:
							check = True
							break

					if check:
						continue

					intersection1 = line_intersection(line,[self.cspace.boundary[2],self.cspace.boundary[3]])
					if intersection1 is None:
						intersection1 = line_intersection(line,[self.cspace.boundary[0],self.cspace.boundary[3]])
						intersection2 = line_intersection(line,[self.cspace.boundary[1],self.cspace.boundary[2]])
					else:
						intersection2 = line_intersection(line,[self.cspace.boundary[0],self.cspace.boundary[1]])
					elongated_line = [intersection1,intersection2]

					add_edge = True

					for edge in self.polygon_edges:
						if pt1 not in edge and pt2 not in edge:
							temp_point = line_intersection(elongated_line,edge)
							if temp_point is not None:
								if polygon1 is not None and polygon2 is not None:
									if edge[0] in self.cspace.polygons:
										add_edge = False
										break

								else:
									if edge[0] in self.cspace.polygons:
										if polygon1 is None:
											midpt = [(pt2[0]+temp_point[0])/2.0,(pt2[1]+temp_point[1])/2.0]
											add_edge = not inside_polygon(midpt[0],midpt[1],polygon2)
										else:
											midpt = [(pt1[0]+temp_point[0])/2.0,(pt1[1]+temp_point[1])/2.0]
											add_edge = not inside_polygon(midpt[0],midpt[1],polygon1)






