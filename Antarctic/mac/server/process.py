import os
import shutil
import threading
import time

import PolarNavigatorServer.Antarctic.mac.server.modisProcessing.main_processing


class check_process(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval
        range_file = open('range.txt')
        self.cu_range = range_file.readline()
        range_file.close()

    def run(self):
        self.process()

    def process(self):
        while True:

            # src = os.getcwd() + '/modisdownload/Data/Modis_data/'
            # dst = os.getcwd() + '/modisProcessing/MODIS/hdf/'
            src = os.getcwd() +  '/modisProcessing/SAR/tiff/download/'
            dst = os.getcwd() +  '/modisProcessing/SAR/tiff/'
            # print('~~~~~~~~~~~~')
            for dripath, dirnames, filenames in os.walk(src):
                print('dripath',dripath)
                print('dirnames', dirnames)
                print('filename', filenames)
                for filename in filenames:
                    print('filename', filename)
                    sar_folder_name = filename.split('.')[0]
                    src_file = src + sar_folder_name + '/' + sar_folder_name + '.tif'
                    dst_file = dst + sar_folder_name + '.tif'
                    print('src_file', src_file)
                    print('dst_file', dst_file)
                    if filename.startswith('S1') and filename.endswith('.tar.gz') and not os.path.exists(dst_file):

                        # exit()
                        # try:
                            if os.path.exists(dst_file):
                                continue
                            else:
                                from read_sarupdate2 import un_gz, un_tar
                                un_gz(src + filename)
                                un_tar(src + filename)
                                print('filename', filename)
                                from shutil import move
                                move(src_file, dst_file)
                                # shutil.move(sarname, dst)
                            shutil.rmtree(src + sar_folder_name)
                            os.remove(src + filename)
                        # except Exception as e:
                        #     print(e)
                        #     continue

            filelist = []
            for dirpath, dirnames, filenames in os.walk(dst):
                # print('dripath', dripath)
                # print('dirnames', dirnames)
                # print('filename', filenames)
                for filename in filenames:
                    # if filename.startswith('MOD') and filename.endswith('.hdf'):
                    #     filelist.append('.'.join(filename.split('.')[0:-1]))
                    sar_folder_name = filename.split('.')[0]
                    # src_file = src + sar_folder_name + '/' + sar_folder_name + '.tif'
                    # dst_file = dst + sar_folder_name + '.tif'

                    if filename.startswith('S1') and filename.endswith('.tif'):
                        # filelist.append('.'.join(filename.split('.')[0:-1]))
                        filelist.append(sar_folder_name)
            filelist.sort()
            # print('filelist', filelist)

            range_file = open('range.txt')
            value = range_file.readline()
            range_file.close()
            print value
            values = value.split(' ')
            print(values)
            EastBoundingCoord = float(values[1])
            WestBoundingCoord = float(values[0])
            SouthBoundingCoord = float(values[3])
            NorthBoundingCoord = float(values[2])

            # from Antarctic.mac.server.modisProcessing.transfer import transfer
            from modisProcessing.transfer import transfer
            ulx, uly, lrx, lry = transfer(WestBoundingCoord, EastBoundingCoord, NorthBoundingCoord, SouthBoundingCoord)

            iscrop = True

            for filename in filelist:
                # print('before 1 filename', filename)
                sar_folder_name = filename.split('.')[0]
                src_file = src + sar_folder_name + '/' + sar_folder_name + '.tif'
                dst_file = dst + sar_folder_name + '.tif'
                if 1:

                    # exit()
                    # try:
                    #     if os.path.exists(dst_file):
                    #         continue
                    #     else:
                    #         from read_sarupdate2 import un_gz, un_tar
                    #         un_gz(dst + filename)
                    #         un_tar(dst + filename)
                    #         print('before update filename', filename)
                    #         from shutil import move
                    #         move(src_file, dst_file)

                    newname, iscrop, crop_name = PolarNavigatorServer.Antarctic.mac.server.modisProcessing.main_processing.updateRaster(
                                filename, ulx, uly, lrx, lry)
                            # shutil.move(sarname, dst)
                        # shutil.rmtree(src + sar_folder_name)


                    # except Exception as e:
                    #     print(e)
                    #     continue


            # for filename in filelist:
            #     src_file = src + filename + ".hdf"
            #     dst_file = dst + filename + ".hdf"
            #     if os.path.exists(dst_file):
            #         continue
            #     else:
            #         from shutil import move
            #         move(src_file, dst_file)
            #         # os.rename(src_file, dst_file)
            #
            #         print('preprocess file "%s"......' % filename)
            #         newname, iscrop, crop_name = PolarNavigatorServer.Antarctic.mac.server.modisProcessing.main_processing.updateRaster(filename, ulx, uly, lrx, lry)

            zero_mark = False
            if len(filelist) != 0:
                # clear old files
                # import clearfile
                # clearfile.clear_raster()
                # clearfile.clear_files()
                pass
            else:
                zero_mark = True
            # print('self.cu_range', self.cu_range)
            # print('value', value)
            # exit()
            # modis file update
            if (not zero_mark) or (self.cu_range != value):
                fileset = set()
                for dripath, dirnames, filenames in os.walk('modisProcessing/SAR/tiff/arcmapWorkspace/'):
                # for dripath, dirnames, filenames in os.walk('modisProcessing/MODIS/tiff/arcmapWorkspace/'):
                    for filename in filenames:
                        if filename.endswith('.tif'):
                            fileset.add(int(filename.split('.')[0].split('_')[0]))
                fileset = sorted(fileset, reverse=True)
                print fileset

                if fileset != []:
                    if zero_mark and value != self.cu_range:
                        newfilename = str(fileset[0]) + '_CURRENT_RASTER_250'
                        from modisProcessing import RasterManagement
                        iscrop, crop_name = RasterManagement.cropandmask(ulx, uly, lrx, lry, newfilename)

                    if iscrop:
                        if os.path.exists('test/'):
                            shutil.rmtree('test/')
                        os.mkdir('test/')
                        for dripath, dirnames, filenames in os.walk('modisProcessing/SAR/tiff/arcmapWorkspace/'):
                            for filename in filenames:
                                if crop_name in filename:
                                    print filename
                                    shutil.copy('modisProcessing/SAR/tiff/arcmapWorkspace/' + filename, 'test/' + filename)

                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.lonlat', 'test/' + newfilename + '.lonlat')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.prob', 'test/' + newfilename + '.prob')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.jpg', 'test/' + newfilename + '.jpg')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.cost', 'test/' + newfilename + '.cost')
                        # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.ice', 'test/' + newfilename + '.ice')

                        import sendemail
                        sendemail.send_file_zipped('test', ['PolarRecieveZip@lamda.nju.edu.cn'], 'PolarEmail1234', 'PolarSendZip@lamda.nju.edu.cn', fileset[0])

                        # for root, dirs, files in os.walk('modisProcessing/SAR/tiff/arcmapWorkspace',
                        #         topdown=False):
                        #     for name in files:
                        #         os.remove(os.path.join(root, name))
                        #     for name in dirs:
                        #         os.rmdir(os.path.join(root, name))
                        # for root, dirs, files in os.walk('modisProcessing/SAR/Ice', topdown=False):
                        #     for name in files:
                        #         os.remove(os.path.join(root, name))
                        #     for name in dirs:
                        #         os.rmdir(os.path.join(root, name))
                        # for root, dirs, files in os.walk('modisProcessing/SAR/Proba',topdown=False):
                        #     for name in files:
                        #         os.remove(os.path.join(root, name))
                        #     for name in dirs:
                        #         os.rmdir(os.path.join(root, name))
            else:
                print 'no modis file updated'

            self.cu_range = value

            time.sleep(self.interval)

if __name__ == '__main__':
    process_interval = 180
    p = check_process(process_interval)
    p.start()


