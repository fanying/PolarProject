import gdal
from gdalconst import GA_Update
from osgeo import osr
import numpy as np
import math
import os, shutil
import cv2
import ConfigParser

RESOLUTION = 120


def reprojectingTiff(filename, folder = 'modisProcessing/SAR/tiff/'):
    print filename
    print(folder+filename+'.tif')
    dataset = gdal.Open(folder+filename+'.tif', GA_Update)
    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    # transfer 16bit image to 8bit
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    # array /= 256
    # print('array[0][0]:', array[0][0])
    # print('max', np.max(np.array(array)) )
    # muls = 65536 / np.max(np.array(array)) + 1
    # # print('muls', muls)
    # # exit()
    # if muls > 255:
    #     muls = 255
    # array = array * muls / 256

    mask1 = array <= 1
    muls = 65536.0 / np.max(np.array(array))

    # print('-------------------------------------muls--------------------------------------------------', muls)
    # print('np.max(np.array(array))', np.max(np.array(array)))
    # muls = 200
    mask2 = array < muls
    array = array * muls / 256
    # array[mask2] = 1
    array[mask1] = 0
    array[array == 256] = 255
    # print('array[0][0]:', array[0][0])
    # print('array.shape', array.shape)
    # print('max(array)', np.max(array))
    # array.dtype = 'uint8'
    # for i in range(y_size):
    #     index = array[i] == 0
    #     array[i][index] = 1
    #     index = None

    band.WriteArray(array)
    band = None
    array = None

    # get projection of the origin image
    projection = dataset.GetProjection()
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(projection)
    print spatialRef

    # set the destinate (appointed) projection
    centerLat = -90.0
    centerLong = 0.0
    scale = 1.0
    falseEasting = 0
    falseNorthing = 0
    desSpatialRef = osr.SpatialReference()
    desSpatialRef.ImportFromWkt(projection)
    desSpatialRef.SetPS(centerLat, centerLong, scale, falseEasting, falseNorthing)
    print desSpatialRef

    # transfer coordinates and obtain the new geo (extent of the reprojected image)
    tx = osr.CoordinateTransformation (spatialRef, desSpatialRef)
    geo_t = dataset.GetGeoTransform()
    # print('reprojectingTiff', geo_t)
    # resolution = 160
    (ulx, uly, ulz) = tx.TransformPoint(geo_t[0], geo_t[3])
    (urx, ury, urz) = tx.TransformPoint(geo_t[0]+geo_t[1]*x_size+geo_t[2]*y_size, geo_t[3])
    (lrx, lry, lrz) = tx.TransformPoint(geo_t[0]+geo_t[1]*x_size+geo_t[2]*y_size, geo_t[3]+geo_t[4]*x_size+geo_t[5]*y_size)
    (llx, lly, llz) = tx.TransformPoint(geo_t[0], geo_t[3]+geo_t[4]*x_size+geo_t[5]*y_size)
    min_x = min([ulx, urx, lrx, llx])
    max_x = max([ulx, urx, lrx, llx])
    min_y = min([uly, ury, lry, lly])
    max_y = max([uly, ury, lry, lly])

    # reproject the image to the new projection
    drv = gdal.GetDriverByName('MEM')
    dest = drv.Create('', int((max_x - min_x)/RESOLUTION)+1, int((min_y - max_y)/-RESOLUTION)+1, 1, gdal.GDT_Byte)
    new_geo = (min_x, RESOLUTION, 0.0, max_y, 0.0, -RESOLUTION)
    print new_geo
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(desSpatialRef.ExportToWkt())
    gdal.ReprojectImage(dataset, dest, projection, desSpatialRef.ExportToWkt(), gdal.GRA_NearestNeighbour)
    dataset = None
    os.remove(folder+filename+'.tif')

    band = dest.GetRasterBand(1)
    array = band.ReadAsArray()
    # print('array[0][0]:', array[0][0])
    x_size = dest.RasterXSize
    y_size = dest.RasterYSize
    # print('array[0][0]:',array[0][0])
    for i in range(y_size):
        index = array[i] == 0
        array[i][index] = 255
        index = None
    # print('array[0][0]:', array[0][0])
    # print('min(array):', np.min(array))
    # exit()
    band.WriteArray(array)

    top = -1
    for i in range(y_size):
        if np.all(array[i,:] == 255):
            if i > top:
                top = i
        else:
            break
    bottom = y_size
    for i in range(y_size)[::-1]:
        if np.all(array[i,:] == 255):
            if i < bottom:
                bottom = i
        else:
           break
    left = -1
    for i in range(x_size):
        if np.all(array[:,i] == 255):
            if i > left:
                left = i
        else:
            break
    right = x_size
    for i in range(x_size)[::-1]:
        if np.all(array[:,i] == 255):
            if i < right:
                right = i
        else:
            break
    array = None
    band = None

    new_drv = gdal.GetDriverByName('GTiff')
    # print('----------------------------------filename',filename)
    ll = filename.split('_')
    tt = ll[4].split('T')
    filetime = ll[0][2] + tt[0] + '_' + tt[1]
    # newfilename = '_'.join(filename.split('.')[1:3]) + '.'+str(int(math.ceil(new_geo[0]+(left+1)*new_geo[1]))) + '_' + \
    #               str(int(math.floor(new_geo[3]+(top+1)*new_geo[5]))) + '_250.'
    newfilename = filetime + '.' + str(
        int(math.ceil(new_geo[0] + (left + 1) * new_geo[1]))) + '_' + \
                  str(int(math.floor(new_geo[3] + (top + 1) * new_geo[5]))) + '_' +str(RESOLUTION)
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~newfilename",newfilename)
    new_dest = new_drv.Create(folder+newfilename+'.tif', right-left-1, bottom-top-1, 1, gdal.GDT_Byte)
    new_new_geo = (new_geo[0]+(left+1)*new_geo[1], new_geo[1], new_geo[2], new_geo[3]+(top+1)*new_geo[5], new_geo[4], new_geo[5])
    print new_new_geo
    new_dest.SetGeoTransform(new_new_geo)
    new_dest.SetProjection(dest.GetProjection())
    gdal.ReprojectImage(dest, new_dest, dest.GetProjection(), new_dest.GetProjection(), gdal.GRA_NearestNeighbour)
    new_dest = None

    return newfilename


def enhancingImage(filename, folder = 'modisProcessing/SAR/tiff/'):
    print filename

    dataset = gdal.Open(folder+filename+'.tif', GA_Update)
    band = dataset.GetRasterBand(1)
    picarray = band.ReadAsArray()
    # print picarray

    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    # picarray = homofilter(picarray, x_size, y_size)
    picarray = cv2.equalizeHist(picarray)
    mask = picarray == 0
    picarray[mask] = 1
    # picarray = unifyGrayCenter(picarray)

    band.WriteArray(picarray)


def homofilter(orig_array, x_size, y_size):
    print orig_array.shape
    mask = orig_array == 255
    orig_array = orig_array.astype(np.float32)/255.0
    opt_x_size = cv2.getOptimalDFTSize(x_size)
    opt_y_size = cv2.getOptimalDFTSize(y_size)
    # opt_x_size = x_size
    # opt_y_size = y_size
    if opt_x_size % 2 != 0:
        opt_x_size +=1
    if opt_y_size % 2 != 0:
        opt_y_size +=1
    if opt_x_size - x_size > 0:
        orig_array = np.hstack((orig_array, np.ones((y_size, opt_x_size - x_size))))
    if opt_y_size - y_size > 0:
        orig_array = np.vstack((orig_array, np.ones((opt_y_size - y_size, opt_x_size))))
    print orig_array.shape

    print 'log ...'
    log_array = np.log(orig_array+0.0001)
    print log_array
    orig_array = None

    print 'dct ...'
    dct_array = cv2.dct(log_array)
    print dct_array
    log_array = None

    print 'filter ...'
    gammaH = 2
    gammaL = 0.3
    C = 1.0
    d0 = float((opt_y_size/2)**2 + (opt_x_size/2)**2)
    colvec = (np.arange(opt_y_size).reshape(opt_y_size, 1))**2
    rowvec = (np.arange(opt_x_size).reshape(1, opt_x_size))**2
    print (colvec+rowvec)/d0
    H = (gammaH - gammaL)*(1 - np.exp(-C*(colvec+rowvec)/d0)) + gammaL
    # H = np.ones(dct_array.shape)
    # H[colvec+rowvec<d0] = 0.0
    print H
    filtered_dct_array = dct_array*H
    print filtered_dct_array
    dct_array = None

    print 'idct ...'
    idct_array = cv2.idct(filtered_dct_array)
    print idct_array
    filtered_dct_array = None
	
    print 'exp ...'
    exp_array = np.uint8((np.floor(np.exp(idct_array)*255.0)))
    print exp_array
    array = np.copy(exp_array[0:y_size, 0:x_size])
    print array.shape

    array[mask] = 255
    return array


def unifyGrayCenter(picarray):
    mean=106.0
    picarray2 = picarray
    picarray2[picarray2 == 255] = 0
    suma = picarray2.sum(axis = 1)
    suma = suma.astype(np.uint64)
    sumb = suma.sum()
    count = np.count_nonzero(picarray2)
    picarray2 = None
    the_mean = sumb / float(count)
    coef = np.float32(mean/the_mean)
    print(coef)
    picarray = picarray * coef
    picarray[picarray > 255] = 255
    picarray[picarray == 255] = 250
    picarray[picarray == 0] = 255
    print picarray.dtype
    picarray = picarray.astype(np.uint8)

    return picarray

