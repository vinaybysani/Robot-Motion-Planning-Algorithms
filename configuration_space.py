import ast
import matplotlib.pyplot as plt

class configuration_space:
	def __init__(self,FILE_NAME):
		self.polygons = []
		line_ctr = 0
		with open(FILE_NAME) as f:
			num_lines = sum(1 for l in f)
		with open(FILE_NAME) as f:
			for l in f:
				line_ctr += 1
				if line_ctr == 1:
					self.boundary = list(ast.literal_eval(l))
				elif line_ctr in range(2,num_lines):
					self.polygons.append(list(ast.literal_eval(l)))
				else:
					temp = list(ast.literal_eval(l))
					self.start_state = temp[0]
					self.goal_state = temp[1]

	def plot_polygon(self,coords):
		for i in range(len(coords)):
			plt.plot(coords[i][0],coords[i][1],marker='o',color='black')
		plt.plot([elem[0] for elem in [coords[0],coords[-1]]],[elem[1] for elem in [coords[0],coords[-1]]],color='black')
		for i in range(1,len(coords)):
			plt.plot([elem[0] for elem in coords[i-1:i+1]],[elem[1] for elem in coords[i-1:i+1]],color='black')

	def plot_config_space(self,showPlot=True):
		axes = plt.gca()
		axes.set_xlim([self.boundary[0][0],self.boundary[1][0]])
		axes.set_ylim([self.boundary[0][1],self.boundary[2][1]])
		plt.plot(self.start_state[0],self.start_state[1],marker='o',color='red')
		plt.plot(self.goal_state[0],self.goal_state[1],marker='o',color='green')
		for i in range(len(self.polygons)):
			self.plot_polygon(self.polygons[i])
		if showPlot:
			plt.show()

class VerticalCellDecomposition:
	def __init__(self,cspace):
		self.cspace = cspace

	def construct_cells(self):
		polygon_points = [item for sublist in self.cspace.polygons for item in sublist]
		polygon_points.sort(key = lambda tup: tup[0])
		cspace.plot_config_space(showPlot=False)
		plt.plot([polygon_points[0][0]]*2,[self.cspace.boundary[0][1],self.cspace.boundary[2][1]],color='blue')
		plt.plot([polygon_points[-1][0]]*2,[self.cspace.boundary[0][1],self.cspace.boundary[2][1]],color='blue')
		for i in range(1,len(polygon_points)-1):
			pass
		plt.show()

class PRM:
	def __init__(self,cspace,num_samples):
		self.cspace = cspace
		self.num_samples = num_samples

	def inside_polygon(self,x,y,polygon):
		# Using ideas derived from: http://paulbourke.net/geometry/polygonmesh/
		num_vertices = len(polygon)

		inside = False

		p1x,p1y = polygon[0]
		for i in range(num_vertices+1):
			p2x,p2y = polygon[i % num_vertices]
			if y > min(p1y,p2y):
				if y <= max(p1y,p2y):
					if x <= max(p1x,p2x):
						if p1y != p2y:
							xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x,p1y = p2x,p2y

		return inside

	def distance(self,pt1,pt2):
		return ((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**0.5

	def perform_sampling(self,showPlot=True):
		self.sampled_points = [list(cspace.start_state),list(cspace.goal_state)]
		i = 0
		self.cspace.plot_config_space(False)
		while i < self.num_samples:
			sample = True
			x = random.randint(self.cspace.boundary[0][0],self.cspace.boundary[1][0])
			y = random.randint(self.cspace.boundary[0][1],self.cspace.boundary[2][1])
			for polygon in self.cspace.polygons:
				if self.inside_polygon(x,y,polygon):
					# To check if the point lies on the polygon, store the polygon using the endpoints of its line
					# segments. Then, if dist(A,p) + dist(p,B) = dist(A,B), we can conclusively state that the point
					# lies on the line segment.
					sample = False
			if sample:
				if [x,y] not in self.sampled_points:
					i += 1
					plt.plot(x,y,marker='o',color='black')
					self.sampled_points.append([x,y])
		if showPlot:
			plt.show()

	def get_knn(self,k=5):
		distances = []
		for i in range(self.num_samples):
			distances_i = []
			for j in range(self.num_samples):
				distances_i.append(self.distance(self.sampled_points[i],self.sampled_points[j]))
			distances.append(distances_i)
		
		self.adjacency_list = []
		self.weights = []

		for i in range(self.num_samples):
			indices = [distances[i].index(item) for item in sorted(distances[i])[1:k+1]]
			self.adjacency_list.append([self.sampled_points[j] for j in indices])
			self.weights.append([distances[i][j] for j in indices])

	def search(self):
		ucs = Search(self.sampled_points,self.adjacency_list,self.weights)
		final_path, path_cost = ucs.perform_search()

		print "Euclidean distance between start and goal: ",self.distance(self.sampled_points[0],self.sampled_points[1])
		print "Path cost found by PRM: ",path_cost

		for i in range(1,len(final_path)):
			plt.plot([elem[0] for elem in final_path[i-1:i+1]],[elem[1] for elem in final_path[i-1:i+1]],color='brown')

		plt.show()


if __name__ == "__main__":
	cspace = configuration_space("input.txt")
	# cspace.plot_config_space()
	vcd = VerticalCellDecomposition(cspace)
	# vcd.construct_cells()
	prm = PRM(cspace,1000)
	prm.perform_sampling(False)
	prm.get_knn()
	prm.search()
