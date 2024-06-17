import scipy
import matplotlib.pyplot as plt

info_dict = {}
xy = []
full_fname="paths_all.mat"
scipy.io.loadmat(full_fname, info_dict)
# print(info_dict['cell_pos'])
    # xy = info_dict['cell_pos']
xy = info_dict['cell_pos']
print("xy.shape = ",xy.shape)  # (315, 2) for 3 brief plots; each not necessarily same length
    # plt.plot(xy[:,0],xy[:,1],'gray',linewidth=0.5)
ix0 = [0]
print(ix0)
for idx in range(1, xy.shape[0]):
    # xn = xy[idx,0] 
    # xn_m1 = xy[idx-1, 0]
    # if xn < xn_m1:
    if xy[idx,0] == -99.0:
        # print(f'{xn} < {xn_m1}')
        print(f'--- found -99 terminator token')
        ix0.append(idx)

print("ix0= ",ix0)
istart = 0
iend = ix0[1]
print(f"plot from {istart} to {iend} --> del={iend-istart}")
plt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)

for idx in range(1,len(ix0)-1):
    istart = ix0[idx] + 1
    iend = ix0[idx+1]
    if istart == iend:
        break
    print(f"plot from {istart} to {iend} --> del={iend-istart}")
    plt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)
# plt.ylim((-100,100))
# istart = iend
# iend = xy.shape[0]
# print(f"plot from {istart} to {iend} --> del={iend-istart}")
# plt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)
plt.xlim([0, 1000])
# plt.ylim([-100, 100])
plt.ylim([-50, 50])
plt.title("PhysiCell migration bias = 0.8")
plt.show()