import os
import shutil
res = 250
# os.remove('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/A20171127_054204.-1644943_-870312_%d.tif' %res)
# os.remove('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/A20171127_054309.-1667404_-1302352_%d.tif' %res)

# shutil.rmtree('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/arcmapWorkspace')
# os.mkdir('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/arcmapWorkspace')
for root, dirs, files in os.walk('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/arcmapWorkspace', topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
for root, dirs, files in os.walk('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Ice', topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
for root, dirs, files in os.walk('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Proba', topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
# shutil.rmtree('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Ice')
# os.mkdir('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Ice')
# shutil.rmtree('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Proba')
# os.mkdir('F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/Proba')
shutil.copy('C:/Users/fany/Desktop/S1A_EW_GRDM_1SDH_20171127T054204_7D23_S_1.tif','F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/' )
shutil.copy('C:/Users/fany/Desktop/S1A_EW_GRDM_1SDH_20171127T054309_9C24_S_1.tif', 'F:/LAMDA/SOUTH2/PolarNavigatorServer/Antarctic/mac/server/modisProcessing/SAR/tiff/')
