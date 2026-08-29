import scipy

info_dict = {}
full_fname="path_001.mat"
scipy.io.loadmat(full_fname, info_dict)
print(info_dict['cell_pos'])
