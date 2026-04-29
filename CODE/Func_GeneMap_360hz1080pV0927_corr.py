import numpy as np
import os
from time import time
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import math
import scipy.io as io
import torch
import torch.nn.functional as F
import copy
import Func_TiffStackDir
try:
    from tensorboardX import SummaryWriter
except ModuleNotFoundError:
    class SummaryWriter:
        def __init__(self, *args, **kwargs):
            pass

        def add_scalar(self, *args, **kwargs):
            pass

        def add_image(self, *args, **kwargs):
            pass

        def add_histogram(self, *args, **kwargs):
            pass

        def close(self):
            pass
# import pytorch_ssim

def GeneMap(shift):

    # location (x_, y_) 目标像素位置
    # angledata (a, x, y, 3) 该通道原始数据
    # index (3) 该通道位置输出值


    # a 角度（0，1）
    # x 横向（1, 1526）
    # y 纵向（1, 2048）

    # 参数配置
    screenW = 1920
    screenH = 1080

    subpixelSize = np.array(1 / 3)    # 红绿蓝像素位移mm
    subpixel_idx = np.array([0, 1, 2])    # 红绿蓝像素排列
    # subpixel_idx = [2, 1, 0]    # 红绿蓝像素排列

    #############################################
    pitch = (7.5 + 0.02) * 3
    center = 0.4+0.5+0.015
    slope = -(-1 / 6 - 0.006)+0.001
    #############################################

    X_mesh = np.linspace(1, screenW, screenW)
    Y_mesh = np.linspace(1, screenH, screenH)
    Z_mesh = (subpixelSize * [1, 1, 1]) * subpixel_idx
    [X_mesh, Y_mesh, Z_mesh] = np.meshgrid(X_mesh, Y_mesh, Z_mesh)

    viewLerp = (Y_mesh*slope + Z_mesh + (shift+X_mesh)) / pitch - center

    modViewLerp = [1, 1, 1] - np.mod(viewLerp, 1)

    Map = np.minimum(np.maximum(modViewLerp, 0.00001), 0.99999)

    return Map

if __name__ == '__main__':
    shift = 0
    Map = GeneMap(shift)
    SavePath_ = './temp_map_360hz1080p3spV0927_corr'
    Func_TiffStackDir.Tiff255ColorSave(torch.from_numpy(Map), SavePath_)
