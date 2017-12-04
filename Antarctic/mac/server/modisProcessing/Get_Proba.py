from PIL import Image
import os.path
import numpy as np
import time
from os import path
import pickle
from sklearn import svm
import math
import gdal
from gdalconst import GA_ReadOnly

'''
input imgname need:
     XXXXXband1.tif
while band2 in the file folder the same time

'''

def rankcount(rank, crop_size):
    crank = [0] * crop_size
    for i in rank:
        crank[int(i)] += 1
    crank.append(np.mean(rank))
    crank.append(np.std(rank))
    return crank

def softmax(scores):
    exp_scores = np.exp(scores)
    probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)  # [N x K]

def find_nonzero(array, i, j, bound):
    size1 = array.shape[0]
    size2 = array.shape[1]
    index = 0
    sum = []
    while i + index < array.shape[0] and index < bound:
        value = array[i + index][j][2]
        # print('[%d,%d]:%f' % (i + index, j, value))
        if not np.isnan(value)  and value < 1:
            sum.append(value)
            # print('[%d,%d]:%f' %(i,j,value))

        index += 1
    if len(sum) > 0:
        return np.mean(sum)
    index = 0
    sum = []
    while j + index < array.shape[1] and index < bound:
        value = array[i][j  + index][2]
        # print('[%d,%d]:%f' % (i, j + index, value))
        if not np.isnan(value) and value < 1:
            # print('[%d,%d]:%f' % (i, j, value))
            sum.append(value)

        index += 1
    if len(sum) > 0:
        return np.mean(sum)
    index = 0
    sum = []
    while i - index > 0 and index < bound:
        value = array[i - index][j][2]
        # print('[%d,%d]:%f' % (i - index, j, value))
        if not np.isnan(value) and value < 1:
            # print('[%d,%d]:%f' % (i, j, value))
            sum.append(value)

        index += 1
    if len(sum) > 0:
        return np.mean(sum)
    index = 0
    sum = []
    while j - index < array.shape[1] and index < bound:
        value = array[i][j - index][2]
        # print('[%d,%d]:%f' % (i, j - index, value))
        if not np.isnan(value ) and  value < 1:
            # print('[%d,%d]:%f' % (i, j, value))
            sum.append(value)

        index += 1
    if len(sum) > 0:
        return np.mean(sum)

def predict(imgname, picpath='modisProcessing/SAR/tiff'):
    f2 = open('modisProcessing/Model//model_svm_linear_2_class_win', 'rb')
    clf2 = pickle.load(f2)
    f = open('modisProcessing/Model/model_svm_linear_south_more_thick', 'rb')
    clf = pickle.load(f)
    img_list = 2
    iname = imgname[0:len(imgname) - 4]

    dataset = gdal.Open(path.join(picpath, imgname), GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    img = Image.fromarray(array)
    print(img.size)
    img_size = img.size
    crop_size = 20
    box_size = crop_size * 1.5
    startpx = 10
    endpx = math.floor(img_size[0] / crop_size) * crop_size
    startpy = 10
    endpy = math.floor(img_size[1] / crop_size) * crop_size + 1
    angs = [0, 15, 30, 45, 60, 75, 90]
    rmatrix = np.zeros((int(math.floor(endpx / crop_size)), int(math.floor(endpy / crop_size)), img_list * 9))
    predict_array = np.empty((int(math.floor(endpy / crop_size)), int(math.floor(endpx / crop_size)), 3),dtype =np.float32)
    mask_array = np.zeros([int(math.floor(endpy / crop_size)), int(math.floor(endpx / crop_size))],dtype = 'bool')

    # endpx = math.ceil(img_size[0] / crop_size) * crop_size
    # startpy = 10
    # endpy = math.ceil(img_size[1] / crop_size) * crop_size
    # angs = [0, 15, 30, 45, 60, 75, 90]
    # rmatrix = np.zeros((int(math.ceil(endpx / crop_size)), int(math.ceil(endpy / crop_size)), img_list * 9))
    # predict_array = np.empty((int(math.ceil(endpy / crop_size)), int(math.ceil(endpx / crop_size)), 3),
    #                          dtype=np.float32)
    # mask_array = np.zeros([int(math.ceil(endpy / crop_size)), int(math.ceil(endpx / crop_size))], dtype='bool')

    predict_array[:] = np.NAN
    csx = int(box_size/2 - crop_size / 2)
    csy = int(box_size/2 - crop_size / 2)
    cex = csx + crop_size
    cey = csy + crop_size
    cbox = (csx, csy, cex, cey)
    imgname_list = []
    pic = imgname[0:len(imgname) - 4]
    w_picname = os.path.join(picpath, pic + '.tif')
    imgname_list.append(w_picname)
    pic_split = pic.split('band1')
    # w_picname2 = os.path.join(picpath, pic_split[0] + 'band2.tif')
    # imgname_list.append(w_picname2)
    print imgname_list
    imgs = []
    flag = 1
    for imgnam in imgname_list:

        imgs.append(Image.fromarray(array).convert('L'))
        if flag == 1:
            imgarray = np.array(imgs[0])
            print(imgarray.shape)
            maskarray = np.empty(imgarray.shape, bool)
            flag = 0
            maskarray[imgarray == imgarray[0][0]] = False
            maskarray[imgarray < imgarray[0][0]] = True
            del imgarray
            for i in range(maskarray.shape[0]):
                row = maskarray[i]
                if True in row.tolist():
                    start1 = row.tolist().index(True)
                    truestart = int((math.ceil(start1/20) + 2) * 20)
                    maskarray[i][0:truestart] = False
    i_index = 0
    for i in range(int(startpx), int(endpx), crop_size):
        j_index = 0
        for j in range(int(startpy), int(endpy), crop_size):
            # t11 = time.time();
            # if 1:
            # if maskarray[j][i] and j + 40 < endpy and i + 40 < endpx and maskarray[j + 40][i + 40] and maskarray[j + 40][i] and maskarray[j][i + 40] < endpy:
            # if maskarray[j][i] and j + 40 < endpy and i + 40 < endpx and maskarray[j + 40][i + 40] and \
            #             maskarray[j + 40][i] and maskarray[j][i + 40]:
            if maskarray[j][i] :
                feature = []
                for ni in range(len(imgname_list)):
                    img = imgs[ni]
                    box = (int(i - box_size / 2), int(j - box_size / 2), int(i + box_size / 2), int(j + box_size / 2))
                    img_box = img.crop(box)
                    a = 0
                    for ang in angs:
                        rimg = img_box.rotate(ang)
                        cropimg = rimg.crop(cbox)
                        if a == 0:
                            aimg = np.array(cropimg)
                            gray = np.mean(aimg)
                            color_gray = np.std(aimg)
                        U, s, V = np.linalg.svd(cropimg)
                        s90 = 0
                        c90 = 0
                        sums = sum(s)
                        for ss in s:
                            s90 += ss
                            c90 += 1
                            if s90 >= sums * 0.95:
                                break
                        feature.append(c90)
                        a += 1
                    feature.append(gray)
                    feature.append(color_gray)
                    # X_test = []
                    # print('feature', feature)
                    # for fi in range(0, len(feature) - 1, 9):
                    #     l = feature[fi: fi + 9]
                    #     ll = np.zeros(7)
                    #     for ini in range(7):
                    #         ll[ini] = int(l[ini])
                    #     crank = rankcount(ll, 20)
                    #     crank.append(float(l[7]))
                    #     crank.append(float(l[8]))
                    #     X_test.extend(crank)

                    # print('X_test', X_test)
                    # exit()
                # y_predicted = clf.predict_proba([X_test])
                ifposative = 1
                if feature[7] < 80:
                    ifposative = -1
                ice_prob = (ifposative  / np.mean(feature[0:7]) + 1) / 2.0
                # ice_prob = ifposative
                y_predicted = [0, 0 ,ice_prob ]
                predict_array[j_index][i_index] = y_predicted
                # print('y_predicted', y_predicted)
                # exit()
                # try:
                #     rmatrix[(i - startpx) / crop_size, (j - startpy) / crop_size] = feature
                # except Exception as e:
                #     print(j_index, (j - startpy) / crop_size, y_predicted[0], predict_array.shape)
                # try:
                #     predict_array[j_index][i_index] = y_predicted[0]
                # except Exception as e:
                #     print(j_index, i_index, y_predicted[0], predict_array.shape)
                if predict_array[j_index][i_index][2] > 0.33:
                    # print(clf2.predict([X_test]))	                    		  
                    # mask_array[j_index][i_index] = clf2.predict([X_test])[0]
                    mask_array[j_index][i_index] = 1
            # else:
            #     predict_array[j_index][i_index] = np.NAN
            j_index += 1
        i_index += 1
    predict_array_2 = np.copy(predict_array)
    # print('-------------------before----------------------------')
    # print('predict_array[0][0]', predict_array[0][0])
    # for i in range(10):
    #     indexi = predict_array.shape[0] - 2
    #     indexj = predict_array.shape[1] - i - 1
    #     print('predict_array[%d][%d]' %(indexi,indexj), predict_array[indexi][indexj] )
    for i in range(predict_array.shape[0]):
        for j in range(predict_array.shape[1]):
            if np.isnan(predict_array[i][j][2]) :
                predict_array_2[i][j][2] = find_nonzero(predict_array, i, j, 4)
                # if not np.isnan(predict_array_2[i][j][2]):
                #     print('before 1111111111111111:(%d,%d):(%f)' % (i, j, predict_array_2[i][j][2]))
    #         if predict_array[i][j][2] == 1 or np.isnan(predict_array[i][j][2]) :
    #             print('before 1111111111111111:(%d,%d):(%f)' % (i, j, predict_array_2[i][j][2]))
                # predict_array_2[i][j][2] = find_nonzero(predict_array_2, i, j , 3)
                # if np.isnan(predict_array_2[i][j][2]):
                #     predict_array_2[i][j][2] = find_nonzero(predict_array_2, i, j, 15)
                #     if(predict_array_2[i][j][2] > 0.5):
                #         predict_array_2[i][j][2] = 0.55
                #     else:
                #         predict_array_2[i][j][2] = 0.42
                # predict_array_2[i][j][2] = 1.0
                # print('after 1111111111111111:(%d,%d):(%f)' % (i, j, predict_array_2[i][j][2]))
                # if i > 0 and predict_array[i - 1][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i - 1][j][2]
                # elif i > 1 and predict_array[i - 2][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i - 2][j][2]
                # elif i > 2 and predict_array[i - 3][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i - 3][j][2]
                # elif i > 3 and predict_array[i - 4][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i - 4][j][2]
                # if j > 0 and predict_array[i][j- 1][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 1][2]
                # elif j > 1 and predict_array[i][j- 2][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 2][2]
                # elif j > 2 and predict_array[i][j - 3][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 3][2]
                # elif j > 3 and predict_array[i][j - 4][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 4][2]
                # elif j > 4 and predict_array[i][j - 5][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 4][2]
                # elif j > 5 and predict_array[i][j - 6][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j - 6][2]
                # if i <  predict_array.shape[0] - 1 and predict_array[i + 1][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i + 1][j][2]
                # elif i <  predict_array.shape[0] - 2 and predict_array[i + 2][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i + 2][j][2]
                # elif i < predict_array.shape[0] - 3 and predict_array[i + 3][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i + 3][j][2]
                # elif i < predict_array.shape[0] - 4 and predict_array[i + 3][j][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i + 4][j][2]
                # if j < predict_array.shape[1] - 1 and predict_array[i][j + 1][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j + 1][2]
                # elif j < predict_array.shape[1] - 2 and predict_array[i][j + 2][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j + 2][2]
                # elif j < predict_array.shape[1] - 3 and predict_array[i][j + 3][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j + 3][2]
                # elif j < predict_array.shape[1] - 4 and predict_array[i][j + 4][2] < 1:
                #     predict_array_2[i][j][2] = predict_array[i][j + 4][2]

    # print('-------------------after----------------------------')
    # print('predict_array[0][0]', predict_array[0][0])
    # for i in range(10):
    #     indexi = predict_array.shape[0]  - 2
    #     indexj = predict_array.shape[1] - i - 1
    #     print('predict_array[%d][%d]' %(indexi,indexj), predict_array_2[indexi][indexj])-
    # print('predict_array[0][0]', predict_array[predict_array.shape[0] - 1][predict_array.shape[1] - 1])

    suffix = '.' + str(startpx - 10) + '_' + str(int(endpx)) + '_' + str(startpy - 10) + '_' + str(int(endpy))
    proname = iname + suffix + '.txt'
    maskname = iname + suffix + '.txt'
    # print('proname',proname)
    if not os.path.exists('modisProcessing/SAR/Proba'):
        os.mkdir('modisProcessing/SAR/Proba')
    if not os.path.exists('modisProcessing/SAR/Ice'):
        os.mkdir('modisProcessing/SAR/Ice')
    pro_matrixf = open(os.path.join('modisProcessing/SAR/Proba',proname), 'wb')
    mask_matrixf = open(os.path.join('modisProcessing/SAR/Ice',maskname), 'wb')
    pickle.dump(predict_array_2, pro_matrixf, protocol=2)
    pickle.dump(mask_array, mask_matrixf, protocol=2)


if __name__ == '__main__':
    imgname='MOD02QKM.A2014002.0050.006.2014218172404_band1_8bit.tif'
    t1=time.time()
    predict(imgname)
    t2=time.time()
    print (t2-t1)

