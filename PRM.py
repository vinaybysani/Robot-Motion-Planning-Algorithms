from configuration_space import configuration_space, Roadmap
from utils import *
from collections import defaultdict
from uniform_cost_search import Search
import random
import matplotlib.pyplot as plt 
import sys

class PRM:
    def __init__(self,cspace,num_samples):
        self.cspace = cspace
        self.num_samples = num_samples
        self.roadmap = Roadmap()

    def perform_sampling(self,showPlot=True):
        self.roadmap.vertices_dict[0] = list(cspace.start_state)
        self.roadmap.vertices_dict[1] = list(cspace.goal_state)
        
        i = 0
        
        self.cspace.plot_config_space(False)
        
        while i < self.num_samples:
            sample = True
            x = random.randint(self.cspace.boundary[0][0],self.cspace.boundary[1][0])
            y = random.randint(self.cspace.boundary[0][1],self.cspace.boundary[2][1])
            for polygon in self.cspace.polygons:
                if inside_polygon(x,y,polygon) or on_polygon(x,y,polygon):
                    sample = False
            if sample:
                if [x,y] not in self.roadmap.vertices_dict.values():
                    i += 1
                    plt.plot(x,y,marker='o',color='black',markersize=1)
                    self.roadmap.vertices_dict[i+1] = [x,y]  
                    
        if showPlot:
            plt.show()

    def get_knn(self,k=5):
        distances = defaultdict(list)
        for i in self.roadmap.vertices_dict.keys():
            for j in self.roadmap.vertices_dict.keys():
                distances[i].append(distance(self.roadmap.vertices_dict[i],self.roadmap.vertices_dict[j]))
        
        for i in range(len(self.roadmap.vertices_dict.keys())):
            sorted_distances = sorted(distances[i])[1:k+1]
            self.roadmap.adjacency_dict[i] = [distances[i].index(item) for item in sorted_distances]
            self.roadmap.edge_weights[i] = sorted_distances
            
    def search(self):
        ucs = Search(self.roadmap)
        final_path, path_cost = ucs.perform_search()

        if final_path is None:
        	print "Path could not be found!"
        	sys.exit()

        print "Euclidean distance between start and goal: ",distance(self.roadmap.vertices_dict[0],self.roadmap.vertices_dict[1])
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
