# encoding:utf-8

import os, shutil
import PreprocessingManagement
import Get_Proba
import RasterManagement
from transfer import transfer


def updateRaster(filename, ulx, uly, lrx, lry):
    # print('----------------------------------------------updateRaster')
    newfilename = preprocessing(filename)
    # print('newfilename', newfilename)
    Get_Proba.predict(newfilename+'.tif')
    newnewfilename, iscrop, crop_name = postprocessing(newfilename, ulx, uly, lrx, lry)
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '.tif', 'modispath/data/' + newnewfilename + '.tif')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.lonlat', 'test/' + newnewfilename + '.lonlat')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.prob', 'test/' + newnewfilename + '.prob')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.jpg', 'test/' + newnewfilename + '.jpg')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.cost', 'test/' + newnewfilename + '.cost')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.ice', 'test/' + newnewfilename + '.ice')
    return newnewfilename, iscrop, crop_name

def preprocessing(filename):
    # print('----------------------------------------------preprocessing')
    # PreprocessingManagement.hdf2tiff(filename)
    # newfilename1 = PreprocessingManagement.reprojectingTiff(filename + '_band1')
    # newfilename2 = PreprocessingManagement.reprojectingTiff(filename + '_band2')
    # PreprocessingManagement.enhancingImage(newfilename1)
    # PreprocessingManagement.enhancingImage(newfilename2)
    newfilename1 = PreprocessingManagement.reprojectingTiff(filename)
    # newfilename2 = PreprocessingManagement.reprojectingTiff(filename + '_band2')
    PreprocessingManagement.enhancingImage(newfilename1)
    # PreprocessingManagement.enhancingImage(newfilename2)
    # print('preprocessing', newfilename1)
    # return '.'.join(newfilename1.split('.')[0:-1])
    return newfilename1


def postprocessing(filename, ulx, uly, lrx, lry):
    newfilename = RasterManagement.add2CurrentRaster(filename+'.tif')
    RasterManagement.getLonLat(newfilename)
    RasterManagement.getProb(newfilename)
    # RasterManagement.putpixel(newfilename)
    iscrop, crop_name = RasterManagement.cropandmask(ulx, uly, lrx, lry, newfilename)
    print newfilename
    return newfilename, iscrop, crop_name


if __name__=="__main__":
    # import  scipy.io as sio
    # folder = 'SAR/tiff/arcmapWorkspace/'
    # exp = sio.loadmat(folder + 'example.mat')
    # print('load successfully')
    # exit()
    # EastBoundingCoord = -150.0
    # WestBoundingCoord = -140.0
    # SouthBoundingCoord = -80.0
    # NorthBoundingCoord = -70.0

    # EastBoundingCoord = 80
    # WestBoundingCoord = 90
    # SouthBoundingCoord = -75
    # NorthBoundingCoord = -65

    # tar_east = 80
    # tar_west = 90
    # tar_south = -75
    # tar_north = -65


    # ross
    # EastBoundingCoord = 160
    # WestBoundingCoord = 170
    # SouthBoundingCoord = -75
    # NorthBoundingCoord = -70

    #plize
    EastBoundingCoord = 70
    WestBoundingCoord = 76
    SouthBoundingCoord = -65
    NorthBoundingCoord = -70

    ulx, uly, lrx, lry = transfer(WestBoundingCoord, EastBoundingCoord, NorthBoundingCoord, SouthBoundingCoord)
    # folder = 'modisProcessing/MODIS/hdf'
    folder = 'SAR/tiff'
    filelist = []
    for dripath, dirnames, filenames in os.walk(folder):
        # print('filenames', filenames)

        for filename in filenames:
            if filename.startswith('S1') and filename.endswith('.tif'):
                filelist.append('.'.join(filename.split('.')[0:-1]))
    print filelist
    # for filename in filelist:
    #     print('--------------------------------------', filename)
    #     updateRaster(filename, ulx, uly, lrx, lry)
