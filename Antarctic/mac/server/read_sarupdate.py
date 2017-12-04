#coding:utf-8
import xml.dom.minidom
import urllib2
import time
from osgeo import osr
import math
import gzip
import os
import tarfile

def un_gz(file_name):
    """ungz zip file"""
    f_name = file_name.replace(".gz", "")
    # 获取文件的名称，去掉
    g_file = gzip.GzipFile(file_name)
    # 创建gzip对象
    open(f_name, "w+").write(g_file.read())
    # gzip对象用read()打开后，写入open()建立的文件中。
    g_file.close()
    # 关闭gzip对象


def un_tar(file_name):
    tar = tarfile.open(file_name)
    names = tar.getnames()
    dirname = file_name.split('.')[0]
    if os.path.isdir(dirname):
        pass
    else:
        os.mkdir(dirname)
    #由于解压后是许多文件，预先建立同名文件夹
    for name in names:
        tar.extract(name, dirname)
    tar.close()
    os.remove(dirname + '.tif .tar')


class Rangell():
    def __init__(self, EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord):
        self.EastBoundingCoord = EastBoundingCoord
        self.WestBoundingCoord = WestBoundingCoord
        self.SouthBoundingCoord = SouthBoundingCoord
        self.NorthBoundingCoord = NorthBoundingCoord
    def tran_bound_to_list(self):
        return  [  [self.EastBoundingCoord, self.SouthBoundingCoord],
                    [self.EastBoundingCoord, self.NorthBoundingCoord],
                    [self.WestBoundingCoord, self.SouthBoundingCoord],
                    [self.WestBoundingCoord, self.NorthBoundingCoord]
                 ]

class Rangexy():
    def __init__(self, maxx, minx, miny, maxy):
        self.maxx = maxx
        self.minx = minx
        self.miny = miny
        self.maxy = maxy
    def tran_bound_to_list(self):
        return[[self.maxx, self.miny],
               [self.maxx, self.maxy],
               [self.minx, self.miny],
               [self.minx, self.maxy]
        ]

def tranlltoxy(longtitude, lantitude):
    wgs84_wkt = """
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.257223563,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.01745329251994328,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4326"]]"""
    wgs84SpatialRef = osr.SpatialReference()
    wgs84SpatialRef.ImportFromWkt(wgs84_wkt)

    antarctic_wkt = """
        PROJCS["PS",
        GEOGCS["unknown",
            DATUM["unknown",
                SPHEROID["unnamed",6378137,298.2571643544928]],
            PRIMEM["Greenwich",0],
            UNIT["degree",0.0174532925199433]],
        PROJECTION["Polar_Stereographic"],
        PARAMETER["latitude_of_origin",-90],
        PARAMETER["central_meridian",0],
        PARAMETER["scale_factor",1],
        PARAMETER["false_easting",0],
        PARAMETER["false_northing",0],
        UNIT["metre",1,
            AUTHORITY["EPSG","9001"]]]"""
    antarcticSpatialRef = osr.SpatialReference()
    antarcticSpatialRef.ImportFromWkt(antarctic_wkt)

    tx1 = osr.CoordinateTransformation(wgs84SpatialRef, antarcticSpatialRef)
    (x1, y1, tmp) = tx1.TransformPoint(longtitude, lantitude)
    return x1, y1

def getxy_frame(ll_list):
    xlist = []
    ylist = []
    for ll in ll_list:
        x, y = tranlltoxy(ll[0], ll[1])
        xlist.append(x)
        ylist.append(y)
    minx = min(xlist)
    miny = min(ylist)
    maxx = max(xlist)
    maxy = max(ylist)
    xy_range = Rangexy(maxx, minx, miny, maxy)
    return xy_range

def if_point_in_range(x, y, tar_xy_range):
    if x < tar_xy_range.maxx and x > tar_xy_range.minx and y < tar_xy_range.maxy and y > tar_xy_range.miny:
        return True
    else:
        return False


def if_cover(tar_xy_range, the_xy_range):
    mask = False
    the_xy_list = the_xy_range.tran_bound_to_list()
    for xy in the_xy_list:
        mask = mask or if_point_in_range(xy[0], xy[1], tar_xy_range)
    return mask

print('time.asctime(time.localtime(time.time())',time.asctime(time.localtime(time.time())))
ttime = time.asctime(time.localtime(time.time())).split(' ')
date = ttime[4] + ttime[1] + ttime[2]
update_folder = 'modisProcessing/SAR/Update/'
download_folder = 'modisProcessing/SAR/tiff/download/'
updatesar_name = update_folder + 'sarfiles_update_'+ date + '.xml'

# tar_east = -170
# tar_west = -130
# tar_south = -80
# tar_north = -73

tar_east = -162
tar_west = -138
tar_south = -79
tar_north = -75

tar_list = Rangell(tar_east, tar_west, tar_south, tar_north).tran_bound_to_list()
tar_xy_range = getxy_frame(tar_list)
print('maxx, minx, miny, maxy:', tar_xy_range.maxx, tar_xy_range.minx, tar_xy_range.miny, tar_xy_range.maxy)
# exit()
# updateurl = 'http://www.polarview.aq/kml/sarfiles_update?ago=1&amp;hemi=S'
# f_xml = urllib2.urlopen(updateurl)
# data = f_xml.read()
#
# with open(updatesar_name, "wb") as code:
#     code.write(data)



dom = xml.dom.minidom.parse(updatesar_name)
tifnames = dom.getElementsByTagName('name')
coordinates = dom.getElementsByTagName('coordinates')
print('coordinates', coordinates[0].firstChild.data)
print('coordinates', coordinates[1].firstChild.data)
print('coordinates', len(coordinates))
print('tifnames', len(tifnames))
count = 0
incount = 0
for index, coor in enumerate(coordinates):
    # ifcoor.firstChild.data)

    ll = coor.firstChild.data.split(' ')
    # print(index, len(ll))
    # exit()
    if len(ll) > 2 and index != len(coordinates) - 1 and len(coordinates[index + 1].firstChild.data.split(',')) == 2:

        linearRing_points = []
        for pair in ll:
            pp = pair.split(',')
            linearRing_points.append([float(pp[0]), float(pp[1])])
        # print('linearRing_points', linearRing_points)
        # print('points',coordinates[index + 1].firstChild.data)
        the_xy_range = getxy_frame(linearRing_points)
        # print('the_xy_range', the_xy_range)
        if if_cover(tar_xy_range, the_xy_range) or if_cover(the_xy_range, tar_xy_range):
            # print('points', coordinates[index + 1].firstChild.data)
            # print('in cover:', index, coor.firstChild.data)
            tifname = tifnames[count * 2]
            incount += 1
            # print(download_folder + tifname.firstChild.data + '.tar.gz')
            # # exit()
            # # if ~os.path.exists(download_folder + tifname.firstChild.data +'.tar.gz'):
            # pwd = os.getcwd()
            # if os.path.exists(download_folder + tifname.firstChild.data + ' .tar.gz'):
            #     print('exit')
            # else:
            #     print('not exit')
            #     print(download_folder + tifname.firstChild.data + '.tar.gz')
            # exit()
            if not os.path.exists(download_folder + tifname.firstChild.data + ' .tar.gz'):
                print('start download ', tifname.firstChild.data, ' :', time.asctime(time.localtime(time.time())))

                sarurl = 'http://www.polarview.aq/images/104_S1geotiff/' + tifname.firstChild.data +'.tar.gz'
                f = urllib2.urlopen(sarurl)
                data = f.read()
                with open(download_folder + tifname.firstChild.data +' .tar.gz', "wb") as code:
                    code.write(data)
                print('download successfully ', tifname.firstChild.data, ' :', time.asctime(time.localtime(time.time())))

        count += 1
print('count', count)
print('incount', incount)
# print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
#
# for index,tifname in enumerate(tifnames):
#     print(index,tifname.firstChild.data)
    # if index % 2 == 0:
    #     print('start download ',tifname.firstChild.data, ' :', time.asctime(time.localtime(time.time())))
    #     url = 'http://www.polarview.aq/images/104_S1geotiff/' + tifname.firstChild.data +'.tar.gz'
    #     f = urllib2.urlopen(url)
    #     data = f.read()
    #     with open(tifname.firstChild.data +'.tar.gz', "wb") as code:
    #         code.write(data)
    #     print('download successfully ', tifname.firstChild.data, ' :', time.asctime(time.localtime(time.time())))
    #     exit()



# filelist = []
# for dripath, dirnames, filenames in os.walk(download_folder):
#     for filename in filenames:
#         if filename.startswith('S1') and filename.endswith('.tar.gz'):
#             # filelist.append('.'.join(filename.split('.')[0:-1]))
#             un_gz(filename)
#             un_tar(filename)
#             shutil.move("oldpos", "newpos")