import scipy
import matplotlib.pyplot as plt
import sys,string

argc=len(sys.argv)
print('argv=',sys.argv)
# print('argv[0]=',sys.argv[0])

if argc < 4:
    print(f'Usage: {sys.argv[0]} <speed> <persistence> <bias>')
    sys.exit(-1)

speed_str = sys.argv[1]
persistence_str = sys.argv[2]
bias_str = sys.argv[3]
print('bias_str=',bias_str)


info_dict = {}
xy = []
# full_fname="paths_all.mat"
full_fname="path_1cell.mat"
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
# lt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)
plt.plot(xy[istart:iend,0], xy[istart:iend,1],'black',linewidth=1.0)


#========= NOT USED for 1 cell 
for idx in range(1,len(ix0)-1):
    istart = ix0[idx] + 1
    iend = ix0[idx+1]
    if istart == iend:
        break
    print(f"plot from {istart} to {iend} --> del={iend-istart}")
    # plt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)
    plt.plot(xy[istart:iend,0], xy[istart:iend,1],'black', linestyle='dashed', linewidth=3.0)
    plt.plot(xy[istart:iend,0], xy[istart:iend,1],'black', marker='o',linestyle='dashed', linewidth=1)
# plt.ylim((-100,100))
# istart = iend
# iend = xy.shape[0]
# print(f"plot from {istart} to {iend} --> del={iend-istart}")
# plt.plot(xy[istart:iend,0], xy[istart:iend,1],'gray',linewidth=0.5)
plt.xlim([0, 1000])
plt.ylim([-100, 100])
# plt.ylim([-80, 80])
max_idx = xy.shape[0]
end_time = xy[max_idx-2,0]
print("end time = ",end_time)
# plt.title(f'PhysiCell migration: speed,persistence,bias= 2, 0, {bias_str}; T={end_time:.2f}')
# plt.title(f'PhysiCell migration: speed,persistence,bias= 2, 1, {bias_str}; T={end_time:.2f}')
plt.title(f'PhysiCell migration: speed,persistence,bias= {speed_str}, {persistence_str}, {bias_str}')
plt.show()