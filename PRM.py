from configuration_space import configuration_space
from utils import distance, inside_polygon
from uniform_cost_search import Search
import random
import matplotlib.pyplot as plt 

class PRM:
	def __init__(self,cspace,num_samples):
		self.cspace = cspace
		self.num_samples = num_samples

	def perform_sampling(self,showPlot=True):
		self.sampled_points = [list(cspace.start_state),list(cspace.goal_state)]
		i = 0
		self.cspace.plot_config_space(False)
		while i < self.num_samples:
			sample = True
			x = random.randint(self.cspace.boundary[0][0],self.cspace.boundary[1][0])
			y = random.randint(self.cspace.boundary[0][1],self.cspace.boundary[2][1])
			for polygon in self.cspace.polygons:
				if inside_polygon(x,y,polygon):
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
				distances_i.append(distance(self.sampled_points[i],self.sampled_points[j]))
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

		print "Euclidean distance between start and goal: ",distance(self.sampled_points[0],self.sampled_points[1])
		print "Path cost found by PRM: ",path_cost

		for i in range(1,len(final_path)):
			plt.plot([elem[0] for elem in final_path[i-1:i+1]],[elem[1] for elem in final_path[i-1:i+1]],color='brown')

		plt.show()


if __name__ == "__main__":
	cspace = configuration_space("input.txt")
	# cspace.plot_config_space()
	prm = PRM(cspace,1000)
	prm.perform_sampling(False)
	prm.get_knn()
	prm.search()
