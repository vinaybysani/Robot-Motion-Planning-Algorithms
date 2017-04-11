def distance(pt1,pt2):
	return ((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**0.5

def inside_polygon(x,y,polygon):
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

