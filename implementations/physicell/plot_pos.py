import scipy
import matplotlib.pyplot as plt

info_dict = {}
xy = []
full_fname="path_001.mat"
for idx in range(0,6):
    full_fname= f'path_{idx:03d}.mat'
    print(full_fname)
    scipy.io.loadmat(full_fname, info_dict)
# print(info_dict['cell_pos'])
    # xy = info_dict['cell_pos']
    xy.append(info_dict['cell_pos'])
# print("xy.shape")
    # plt.plot(xy[:,0],xy[:,1],'gray',linewidth=0.5)
    plt.plot(xy[idx][:,0], xy[idx][:,1],'gray',linewidth=0.5)
plt.ylim((-100,100))
plt.show()