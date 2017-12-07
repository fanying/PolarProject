import numpy as np
from PIL import Image



mask = lonlat = np.load('mask.npy')
s1 = mask.shape[0]
s2 = mask.shape[1]

for i in range(s1):
    for j in range(s2):
        if mask[i][j] == 128:
            mask[i][j] = 0

mask2 = np.zeros([s1, s2], dtype=np.uint8)
for i in range(s1):
    for j in range(s2):
        if j > 1 and mask[i][j] != mask[i][j-1] and j < s2 - 1:
            mask2[i][j] = 255
            mask2[i][j + 1] = 255


np.save('mask2.npy', mask2)
maskimg = Image.fromarray(mask2)
maskimg.save('mask2.jpg')
