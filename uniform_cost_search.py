from priority_queue import priority_queue

class Search:
	def __init__(self,nodes,edges,weights):
		self.nodes = nodes
		self.g = [float("inf")]*len(nodes)
		self.parents = [[]]*len(nodes)
		self.edges = edges
		self.weights = weights

	def get_successors(self,x,y):
		node = [x,y]
		idx = self.nodes.index(node)
		return self.edges[idx]

	def get_final_path(self):
		final_path = [self.nodes[1]]
		while True:
			idx = self.nodes.index(final_path[-1])
			previous_node = self.parents[idx]
			if previous_node == self.nodes[0]:
				final_path.append(previous_node)
				break
			final_path.append(previous_node)
		return final_path

	def perform_search(self):
		self.g[0] = 0 # Since 0 is the start state
		closed_list = []
		pq = priority_queue()
		pq.insert(self.nodes[0][0],self.nodes[0][1],self.g[0])

		while not pq.isEmpty():
			temp = pq.pop()

			if [temp.x,temp.y] == self.nodes[1]:
				print "Goal state reached!"
				final_path = list(reversed(self.get_final_path()))
				return final_path, self.g[1]

			closed_list.append([temp.x,temp.y])

			temp_index = self.nodes.index([temp.x,temp.y])

			successors = self.get_successors(temp.x,temp.y)

			for node in successors:
				if node not in closed_list:
					xTemp = node[0]
					yTemp = node[1]

					heapIndex = pq.elementInHeap(xTemp,yTemp)

					element_index = self.nodes.index([xTemp,yTemp])

					distance_index = self.edges[temp_index].index([xTemp,yTemp])

					gTemp = self.g[temp_index] + self.weights[temp_index][distance_index]

					if gTemp < self.g[element_index]:
						self.parents[element_index] = self.nodes[temp_index]
						self.g[element_index] = gTemp

					if heapIndex != -1:
						pq.remove(heapIndex)

					pq.insert(xTemp, yTemp,self.g[element_index])