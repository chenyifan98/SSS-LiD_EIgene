
# Image I/O Utility Module / 图像I/O工具模块

import numpy as np
import tifffile
from PIL import Image


# Load PNG images from directory / 从目录加载PNG图像
def PNGDirLoad3Bias(PhantomSize, addr_dir, bias):
    """Load PNG images with bias offset / 加载带偏移量的PNG图像"""
    Image_stack_ = np.zeros(PhantomSize)
    for imageNum in range(PhantomSize[0]):
        addr = addr_dir + str(imageNum + 1 + bias).zfill(3) + '.png'
        Image_stack_[imageNum, :, :, :] = np.array(Image.open(addr))[:, :, 0:3]
    return Image_stack_


# Save color image as TIFF / 将彩色图像保存为TIFF
def TiffColorSave(Phantom, addr_):
    """Save color image / 保存彩色图像"""
    Phantom = np.squeeze(Phantom.cpu().detach().numpy()).astype('uint8')
    addr = addr_ + '_' + str(0).zfill(4) + '.tif'
    tifffile.imwrite(addr, Phantom.squeeze())



