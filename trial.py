import numpy as np
import os
import pickle
from datetime import datetime as dt, timedelta
from read_data import readFile
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from sklearn.neighbors import KDTree

def distance(p1, p2):
	return np.sqrt(np.sum(np.square(p1-p2),axis=-1))

def createR(q_r, q_t):
	R = np.eye(4, dtype=q_r.dtype)
	sq_q_r = np.square(q_r)
	R[0,0] = sq_q_r[0,0] + sq_q_r[1,0] - sq_q_r[2,0] - sq_q_r[3,0]
	R[1,1] = sq_q_r[0,0] + sq_q_r[2,0] - sq_q_r[1,0] - sq_q_r[3,0]
	R[2,2] = sq_q_r[0,0] + sq_q_r[3,0] - sq_q_r[1,0] - sq_q_r[2,0]
	del sq_q_r

	R[0,1] = 2*(q_r[1,0]*q_r[2,0] + q_r[0,0]*q_r[3,0])
	R[1,0] = 2*(q_r[1,0]*q_r[2,0] - q_r[0,0]*q_r[3,0])

	R[0,2] = 2*(q_r[1,0]*q_r[3,0] - q_r[0,0]*q_r[2,0])
	R[0,2] = 2*(q_r[1,0]*q_r[3,0] + q_r[0,0]*q_r[2,0])

	R[1,2] = 2*(q_r[2,0]*q_r[3,0] - q_r[0,0]*q_r[1,0])
	R[2,1] = 2*(q_r[2,0]*q_r[3,0] + q_r[0,0]*q_r[1,0])

	R[:3,3] = q_t[:,0]

	return R

def Q(p, x):
	u_p1 = np.mean(p[:,:3],axis=0)#.reshape((3,1))
	u_p2 = np.mean(x[:,:3],axis=0)#.reshape((3,1))

	# print(com_p1.shape, com_p2.T.shape)
	u_p1p2 = u_p1.dot(u_p2.T)
	points1 = p[:,:3]#.reshape((p.shape[0],3,1))
	# print(p[:10])
	# print(points1[:10])
	points2 = x[:,:3]#.reshape((x.shape[0],3,1))
	p1 = points1 - u_p1
	p2 = points2 - u_p2

	p1p2 = p1.T.dot(p2)
	u,s,v = np.linalg.svd(p1p2)

	R = v.T.dot(u.T)

	if np.linalg.det(R) < 0:
		v[2,:] *= -1
		R = v.T.dot(u.T)

	u_p1 = u_p1.reshape((3,1))
	u_p2 = u_p2.reshape((3,1))
	t = u_p2 - R.dot(u_p1)
	# print(t.shapes)

	X = np.eye(4,dtype=p.dtype)

	X[:3,:3] = R[:,:]
	X[:3,3] = t[:,0]
	R = X[:,:]
	# p1p2 = np.zeros((points1.shape[0],3,3),dtype=points1.dtype)
	# for i in range(points1.shape[0]):
	# 	p1p2[i,:,:] = points1[i].dot(points2[i].T)[:,:]

	# # print(p1p2[:10])
	# sigma_p1p2 = np.mean(p1p2, axis=0) - u_p1p2
	# del p1p2
	# del points1
	# del points2

	# A = sigma_p1p2 - sigma_p1p2.T
	# # print(A.shape)

	# delta = np.array([[A[1,2]],[A[2,0]],[A[0,1]]],dtype=A.dtype)

	# Q_sigma_p1p2 = np.zeros((4,4),dtype=A.dtype)

	# Q_sigma_p1p2[0,0] = np.trace(sigma_p1p2)
	# Q_sigma_p1p2[1:,0] = delta[:,0]
	# Q_sigma_p1p2[0,1:] = delta.T[0,:]
	# temp = sigma_p1p2 + sigma_p1p2.T - (np.trace(sigma_p1p2)*np.eye(3))
	# Q_sigma_p1p2[1:,1:] = temp[:,:]

	# u,s,v = np.linalg.svd(Q_sigma_p1p2)
	# # print(u.shape)
	# # print(s.shape)
	# # print(v.shape)
	# # print(np.argmax(s))
	# ind = np.argmax(s)

	# q_r = v[ind,:]
	# q_r = q_r.reshape((q_r.shape[0],1))
	# # print(np.sum(np.square(q_r)))
	# # print(q_r.shape)

	# R = createR(q_r, np.zeros((3,1)))

	# # sq_q_r = np.square(q_r)
	# # R[0,0] = sq_q_r[0] + sq_q_r[1] - sq_q_r[2] - sq_q_r[3]
	# # R[1,1] = sq_q_r[0] + sq_q_r[2] - sq_q_r[1] - sq_q_r[3]
	# # R[2,2] = sq_q_r[0] + sq_q_r[3] - sq_q_r[1] - sq_q_r[2]

	# # R[0,1] = 2*(q_r[1]*q_r[2] + q_r[0]*q_r[3])
	# # R[1,0] = 2*(q_r[1]*q_r[2] - q_r[0]*q_r[3])

	# # R[0,2] = 2*(q_r[1]*q_r[3] - q_r[0]*q_r[2])
	# # R[0,2] = 2*(q_r[1]*q_r[3] + q_r[0]*q_r[2])

	# # R[1,2] = 2*(q_r[2]*q_r[3] - q_r[0]*q_r[1])
	# # R[2,1] = 2*(q_r[2]*q_r[3] + q_r[0]*q_r[1])

	# q_t = u_p2 - R[:3,:3].dot(u_p1)

	# # q = np.hstack((R,q_t))
	# # print(R)
	# # print(q_t)
	# # q_t[0,0] += 0.0000017
	# # print(q)
	# R[0,3] = q_t[0,0]
	# R[1,3] = q_t[1,0]
	# R[2,3] = q_t[2,0]
	# rotated_p1 = R.dot(p[:,:3].T)
	# rotated_p1 = p[:,:3].T
	# print(rotated_p1.T[:5])
	# final_p1 = rotated_p1 + q_t*np.ones(rotated_p1.shape)
	# final_p1 = X.dot(p.T)
	# # print(q_t*np.ones(rotated_p1.shape)[:,:5])
	# # print(final_p1.shape)
	# final_p1 = final_p1.T

	# ms = np.square(distance(x[:,:3],final_p1[:,:3]))
	# ms = np.mean(ms, axis = 0)
	return R, R[:3,:3], R[:3,3] 

def closest_point(p1, tree, p2):
	
	ind = tree.query(p1, return_distance = False)
	ind = ind.reshape((ind.shape[0]))
	# print(_[:10])
	p = p2[ind,:]
	del ind
	return p

def ICP(p1, p2):
	iters = 1000
	p0 = p1[:,:]
	R0 = None
	X0 = np.eye(4, dtype=np.float32)
	tree = KDTree(p2)
	p0 = X0.dot(p0.T)
	p0 = p0.T
	t = None
	m_err = np.mean(distance(p2,p0),axis=0)
	print('Initial Error: {}'.format(m_err))
	for i in range(iters):
		Y = closest_point(p0, tree, p2)
		X0, R0, t = Q(p0, Y)
		p0 = X0.dot(p0.T) #+ t0*np.ones(p0.T.shape)
		p0 = p0.T
		ms = distance(Y[:,:3], p0[:,:3])
		ms = np.mean(ms,axis=0)
		diff = m_err - ms
		if abs(diff) < 1e-10:
			print('Previous error: {}\nCurrent Error: {}\nDifference: {}'.format(m_err, ms, diff))
			break
		m_err = ms
		if i%10 == 0:
			print('Mean square error at iteration {}: {}'.format(i, ms))
	# X0, R0, t = Q(p0, p2)
	# # R0 = createR(q[:4,:],q[4:,:])
	# p0 = X0.dot(p0.T) # + t0*np.ones(p0.T.shape)
	# p0 = p0.T
	# m_err = np.mean(distance(p2[:,:3],p0[:,:3]),axis=0)
	# print('Mean square error at iteration {}: {}'.format(0, m_err))
	return m_err, X0, R0, t, p0

if __name__ == '__main__':
	dir = 'point_cloud_registration'
	filenames = ['pointcloud1.fuse', 'pointcloud2.fuse']
	names = ['pointcloud1','pointcloud2']
	pointcloud1 = readFile('{}/{}'.format(dir, filenames[0]), names[0])
	pointcloud2 = readFile('{}/{}'.format(dir, filenames[1]), names[1])
	
	print(pointcloud1.shape)
	print(pointcloud2.shape)

	# ind = np.where(np.equal(pointcloud1[:,3],pointcloud2[:,3]))[0]

	'''

	Increasing the Lat Long values by a scale of 1000 too increase the mean square error

	'''
	minLat = min(np.min(pointcloud1[:,0]),np.min(pointcloud2[:,0]))
	minLong = min(np.min(pointcloud1[:,1]), np.min(pointcloud2[:,1]))
	pointcloud1 = np.hstack((pointcloud1[:,:3], np.ones((pointcloud1.shape[0],1),dtype=pointcloud1.dtype)))
	pointcloud2 = np.hstack((pointcloud2[:,:3], np.ones((pointcloud2.shape[0],1),dtype=pointcloud2.dtype)))
	# print(pointcloud1.shape)
	# exit()
	scaleLat = 0
	diffLat = np.max(pointcloud1[:,0]) - minLat
	while int(diffLat%10) == 0:
		diffLat *= 10
		scaleLat += 1
	scaleLat += 1
	# print(diffLat, diffLat%10)
	scaleLong = 0
	diffLong = np.max(pointcloud1[:,1]) - minLong
	while int(diffLong%10) == 0:
		diffLong *= 10
		scaleLong += 1
	scaleLong += 1

	cs_Mat = np.eye(4,dtype=pointcloud1.dtype)
	cs_Mat[0,0] *= 10**scaleLat
	cs_Mat[1,1] *= 10**scaleLong
	cs_Mat[0,3] = -minLat*(10**scaleLat)
	cs_Mat[1,3] = -minLong*(10**scaleLong)
	rev_cs_Mat = np.linalg.inv(cs_Mat)
	print('Coordinate system conversion matrix:')
	print(cs_Mat)
	print('Matrix to get back original coordinates:')
	print(rev_cs_Mat)
	# pointcloud1[:,0] -= minLat
	# pointcloud2[:,0] -= minLat
	# pointcloud1[:,1] -= minLong
	# pointcloud2[:,1] -= minLong
	# pointcloud1[:,:2] = pointcloud1[:,:2]*100000
	# pointcloud2[:,:2] = pointcloud2[:,:2]*100000
	# print(pointcloud1[:2,:])

	pc1 = cs_Mat.dot(pointcloud1.T)
	pc1 = pc1.T
	pc2 = cs_Mat.dot(pointcloud2.T)
	pc2 = pc2.T

	# with open('p2_1.xyz','w') as file:
	# 	for i in range(temp.shape[0]):
	# 		file.write('{} {} {}\n'.format(temp[i,0],temp[i,1],temp[i,2]))

	# temp = rev_cs_Mat.dot(pointcloud1.T)
	# temp = temp.T

	# with open('p1_1.xyz','w') as file:
	# 	for i in range(temp.shape[0]):
	# 		file.write('{} {} {}\n'.format(temp[i,0],temp[i,1],temp[i,2]))

	# del temp

	ms = None
	print()
	cur = dt.now()
	ms, X, R, t, final_p1 = ICP(pc1[:,:], pc2[:,:])
	new_cur = dt.now()
	delt = new_cur - cur
	print('Time Taken: {}'.format(str(delt)))

	print('Mean square error: {}'.format(ms))
	print('Rotation Matrix:')
	print(R)
	print('Translation Matrix:')
	print(t)

	print('\nComplete Transformation Matrix:')
	mat = rev_cs_Mat.dot(X.dot(cs_Mat))
	print(mat)
	# print(pointcloud2[:5])
	# print(final_p1[:5])

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	npoints = 10000

	X = pointcloud1[:npoints,0]
	Y = pointcloud1[:npoints,1]
	Z = pointcloud1[:npoints,2]

	ax.scatter(X,Y,Z, color='b', marker='o', label='Point Cloud 1')
	# ax.plot_wireframe(X,Y,Z, color='b')

	X = pointcloud2[:npoints,0]
	Y = pointcloud2[:npoints,1]
	Z = pointcloud2[:npoints,2]

	# ax.plot_wireframe(X,Y,Z, color='r')
	ax.scatter(X,Y,Z, color='r', marker='o',label='Point Cloud 2')

	ax.set_xlabel('Latitude')
	ax.set_ylabel('Longitude')
	ax.set_zlabel('Altitude')
	
	# final_p1 = mat.dot(pointcloud1.T)
	final_p1 = rev_cs_Mat.dot(final_p1.T)
	final_p1 = final_p1.T
	# with open('p1_fin_perfect.xyz','w') as file:
	# 	for i in range(final_p1.shape[0]):
	# 		file.write('{} {} {}\n'.format(final_p1[i,0],final_p1[i,1],final_p1[i,2]))

	X = final_p1[:npoints,0]
	Y = final_p1[:npoints,1]
	Z = final_p1[:npoints,2]

	# ax.plot_wireframe(X,Y,Z, color='g')
	ax.scatter(X,Y,Z, color='g', marker='o', label='Registered Point Cloud')
	ax.legend()
	ax.set_title('Point Cloud Registration | Visualizing {} points'.format(npoints))

	plt.show()