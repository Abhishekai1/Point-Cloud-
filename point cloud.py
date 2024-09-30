import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

DATANAME = "C:\\Users\\Amresh Yadav\\Desktop\\E2E\\ITC_outdoor.ply"
pcd = o3d.io.read_point_cloud(DATANAME)

pcd_center = pcd.get_center()
pcd.translate(-pcd_center)

o3d.visualization.draw_geometries([pcd])

# Sample the point cloud
sampled_pcd = pcd.uniform_down_sample(every_k_points=10)
o3d.visualization.draw_geometries([sampled_pcd], window_name = "Random Sampling")

nn = 16
std_multiplier = 10

filtered_pcd, filtered_idx = pcd.remove_statistical_outlier(nn, std_multiplier)

outliers = pcd.select_by_index(filtered_idx, invert=True)
outliers.paint_uniform_color([1, 0, 0])
o3d.visualization.draw_geometries([filtered_pcd, outliers])

voxel_size = 0.05
pcd_downsampled = filtered_pcd.voxel_down_sample(voxel_size = voxel_size)

nn_distance = np.mean(pcd.compute_nearest_neighbor_distance())

radius_normals=nn_distance*4
pcd_downsampled.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normals, max_nn=16), fast_normal_computation=True)

pcd_downsampled.paint_uniform_color([0.6, 0.6, 0.6])
o3d.visualization.draw_geometries([pcd_downsampled,outliers])

distance_threshold = 0.1
ransac_n = 3
num_iterations = 1000

plane_model, inliers = pcd.segment_plane(distance_threshold=distance_threshold,ransac_n=3,num_iterations=1000)
[a, b, c, d] = plane_model
print(" Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

inlier_cloud = pcd.select_by_index(inliers)
outlier_cloud = pcd.select_by_index(inliers, invert=True)

#Paint the clouds
inlier_cloud.paint_uniform_color([1.0, 0, 0])
outlier_cloud.paint_uniform_color([0.6, 0.6, 0.6])

#Visualize the inliers and outliers
o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

segment_models={}
segments={}

max_plane_idx=10

rest=pcd
for i in range(max_plane_idx):
    colors = plt.get_cmap("tab20")(i)
    segment_models[i], inliers = rest.segment_plane(
    distance_threshold=0.1,ransac_n=3,num_iterations=1000)
    segments[i]=rest.select_by_index(inliers)
    segments[i].paint_uniform_color(list(colors[:3]))
    rest = rest.select_by_index(inliers, invert=True)
    print("pass",i,"/",max_plane_idx,"done.")
    
o3d.visualization.draw_geometries([segments[i] for i in range(max_plane_idx)]+[rest])

epsilon = 0.15
min_cluster_points = 5

labels = np.array(segments[i].cluster_dbscan(eps=epsilon, min_points=min_cluster_points))

candidates=[len(np.where(labels==j)[0]) for j in np.unique(labels)]

best_candidate=int(np.unique(labels)[np.where(candidates== np.max(candidates))[0]])

rest = rest.select_by_index(inliers, invert=True) + segments[i].select_by_index(list(np.where(labels!=best_candidate)[0]))
segments[i]=segments[i].select_by_index(list(np.where(labels== best_candidate)[0]))

colors = plt.get_cmap("tab20")(i)
segments[i].paint_uniform_color(list(colors[:3]))

o3d.visualization.draw_geometries([rest])

labels = np.array(pcd.cluster_dbscan(eps=0.1, min_points=10))

max_label = labels.max()
colors = plt.get_cmap("tab20")(labels / (max_label 
if max_label > 0 else 1))
colors[labels < 0] = 0
rest.colors = o3d.utility.Vector3dVector(colors[:, :3])
o3d .visualization.draw_geometries([rest])

voxel_size=0.5


min_bound = pcd.get_min_bound()
max_bound = pcd.get_max_bound()


pcd_ransac=o3d.geometry.PointCloud()
for i in segments:
 pcd_ransac += segments[i]
 
 voxel_grid_structural = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd_ransac, voxel_size=voxel_size)
 
 rest.paint_uniform_color([0.1, 0.1, 0.8])
voxel_grid_clutter = o3d.geometry.VoxelGrid.create_from_point_cloud(rest, voxel_size=voxel_size)

o3d.visualization.draw_geometries([voxel_grid_clutter,voxel_grid_structural])
