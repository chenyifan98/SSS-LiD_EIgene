# ============================================================================
# 360-Degree 3D Display Image Generation Script
# 360度3D显示图像生成脚本
# ============================================================================

import numpy as np
import os
import math
import torch
import torch.nn.functional as F
import Func_TiffStackDir
from Func_GeneMap_360hz1080pV0927_corr import GeneMap as GeneMap


# ============================================================================
# Image Shift Function / 图像平移函数
# ============================================================================
def FloatRoll2(angledata, shift):
    """
    Perform sub-pixel image shift using affine transformation
    使用仿射变换进行亚像素图像位移
    """
    B = angledata.shape[0]
    H = angledata.shape[2]
    W = angledata.shape[3]
    shift_x = shift[0]/W*2
    shift_y = shift[1]/H*2
    transform_matrix = torch.tensor([
        [1, 0, shift_x],
        [0, 1, shift_y]]).unsqueeze(0).repeat(B,1,1).float()

    grid = F.affine_grid(transform_matrix,
                         angledata.shape,
                         align_corners=True).to(angledata.device)

    output = F.grid_sample(angledata,
                           grid,
                           mode='bilinear',
                           align_corners=True)

    return output


# ============================================================================
# Multi-view Fusion Function / 多视图融合函数
# ============================================================================
def Angle2Screen_byMap_corr(angledata, Map):
    """
    Fuse multi-view images into single display image with optical correction
    使用透镜映射和光学校正将多视图图像融合为单张显示图像
    """
    
    angledata = angledata.permute([0, 2, 3, 1])
    Map = 1-Map
    angledataSize = angledata.size()
    Num_views = angledataSize[0]
    Map_i = angledata*0
    rate = 1
    bright = 1
    n_rgb = [1.5-0.01,1.5,1.5+0.01]
    Map_angle = Map*1.0
    mag_angle = 100
    mag_shift = 1000

    # ========================================================================
    # RGB Channel Optical Correction / RGB通道光学校正
    # ========================================================================
    for i in range(0,3):
        n = n_rgb[i]
        angle_1 = torch.linspace(0, 90, mag_angle*90+1)/180*np.pi
        angle_2 = torch.asin(torch.sin(angle_1)/n)
        angle_3 = torch.asin(torch.sin(angle_2)/n)
        shift_2 = torch.tan(angle_2)*1
        shift_3 = torch.tan(angle_3)*2.2
        shift_0 = (shift_2+shift_3)/(1.32*3/2)*mag_shift

        shift_0_r = -shift_0.flip(dims=[0])
        shift_00 = -torch.cat((shift_0_r, shift_0[1:]), dim=0).clip(-1000, 1000) / 2000 *22.5
        for j in range(0, angledata.size(0)):
            temp = angledata[j, :, :, i].unsqueeze(0).unsqueeze(0)
            angledata[j, :, :, i] = FloatRoll2(temp, [float(shift_00[j*mag_angle]),0])

        temp = torch.minimum(shift_0, torch.tensor(mag_shift+1)).ceil().int()
        angle_list_s = torch.linspace(0,0,mag_shift+1)
        for j in range(0,temp.shape[0]):
            if temp[j] >= angle_list_s.size(0):
                continue
            angle_list_s[temp[j]] = j*1.0/mag_angle

        angle_list_r = -angle_list_s.flip(dims=[0])
        angle_list = torch.cat((angle_list_r, angle_list_s[1:]), dim=0).view(1, 1, -1, 1)+90

        grid = ((Map[i,:,:]-0.5)*2).flatten().view(1, 1, -1, 1)
        grid = torch.cat([torch.zeros_like(grid), grid], dim=-1)
        tmp = torch.nn.functional.grid_sample(angle_list, grid, mode='bilinear', align_corners=True)

        Map_angle[i,:,:] = tmp.reshape_as(Map_angle[i,:,:])

    # ========================================================================
    # Weighted Blending / 加权混合
    # ========================================================================
    for i in range(0, Num_views):
        tmp = (bright-(Map_angle-(i)).abs())*rate
        tmp2 = torch.max(tmp, torch.zeros_like(tmp)).permute([1,2,0])
        Map_i[i, :, :, :] = tmp2

    disp = torch.sum(Map_i * angledata, [0])
    return disp


# ============================================================================
# Main Execution / 主程序
# ============================================================================
if __name__ == '__main__':
    device = torch.device("cuda:0")

    # ========================================================================
    # Configuration Parameters / 配置参数
    # ========================================================================
    SavePath = './VF40201_ImgDisp_ALL/'
    OBJDIV = 1  
    Flag_LumNorm = 1
    Flag_RED = 0

    # ========================================================================
    # Image Parameters / 图像参数
    # ========================================================================
    Angle_Num = 181

    ImageSize = [1080, 1920, 3]
    LightFeildSize = [Angle_Num, ImageSize[0], ImageSize[1], ImageSize[2]]

    # ========================================================================
    # Motion Parameters / 运动参数
    # ========================================================================
    steplength = 7.5 * 2 / 6
    step = 1 * steplength * np.array([-1, 0])
    shiftstepnum = 1
    fps = 1
    shifttime = int(shiftstepnum/fps)
    allstepnum = 360
    stepdirection_1 = (np.linspace(0, allstepnum-1, allstepnum) > allstepnum*1/4)*2-1
    stepdirection_2 = (np.linspace(0, allstepnum - 1, allstepnum) <= allstepnum*3/4) * 2 - 1
    stepdirection_ = stepdirection_1*stepdirection_2
    stepdirection = np.tile(stepdirection_, shifttime)
    framenumlist = np.linspace(0, shiftstepnum - 1, shiftstepnum).repeat(allstepnum/fps)

    # ========================================================================
    # Frame Settings / 帧数设置
    # ========================================================================
    FrameRate = 360
    FrameNum = framenumlist.shape[0] * 2
    # FrameNum = 360

    # ========================================================================
    # Create Output Directory / 创建输出目录
    # ========================================================================
    if not os.path.exists(SavePath): 
        os.mkdir(SavePath)

    # ========================================================================
    # Main Loop: Generate Display Images / 主循环：生成显示图像
    # ========================================================================
    dirinname = '../ViewpointData/PlantTestUSAF/Results_V9/'

    for iframe in range(0, FrameNum, 1):
        print(f'\nGenerating Img_Disp for frame {iframe}...')
        
        # Frame Index Calculation / 帧索引计算
        iframeiter = iframe % stepdirection.shape[0]
        frameindex = framenumlist[iframeiter]
        
        # Direction and Shift Calculation / 方向和位移计算
        framestep = step * stepdirection[iframeiter]
        Yshift = ((stepdirection[0:(iframeiter+1)].sum()) * step)
        
        # ====================================================================
        # Load Multi-view Image Data / 加载多视图图像数据
        # ====================================================================
        addr = dirinname + 'Endres' + str(int(frameindex+1)).zfill(4)
        Img_Obj = Func_TiffStackDir.PNGDirLoad3Bias(LightFeildSize, addr, 0).astype('float32')
        Img_Obj = torch.from_numpy(Img_Obj.squeeze()).permute([0, 3, 1, 2])
        Img_Obj = Img_Obj / OBJDIV

        # ====================================================================
        # Inter-angle brightness correction / 角度间亮度矫正
        # ====================================================================
        if Flag_LumNorm:
            k = [1,0.96,0.86,0.78,0.64, 0.58,0.5,0.5]
            # k是91个点中均匀采样的7个点（每15个点采一个）
            k_indices = np.array([0, 15, 30, 45, 60, 68, 75, 90])
            all_indices = np.arange(91)
            k_corr_np = np.interp(all_indices, k_indices, k)
            k_corr = torch.from_numpy(k_corr_np).float()
            k2_corr = torch.cat([k_corr.flip(0), k_corr[1:]])  # 第一个k_corr反转
            k3_corr = torch.maximum(k2_corr * 2, torch.tensor(1.0))  # max(k2*3, 1)
            Img_Obj = Img_Obj / k3_corr.view(-1, 1, 1, 1)


        if Flag_RED:
            Img_Obj[:, 1:3, :, :] = 0

        # ====================================================================
        # Load Lens Map / 加载透镜映射
        # ====================================================================
        Img_Map = GeneMap(0).astype('float32')
        Img_Map = torch.from_numpy(Img_Map.squeeze())
        Img_Map = Img_Map.permute([2, 0, 1])

        # ====================================================================
        # Generate Display Image / 生成显示图像
        # ====================================================================
        Img_Obj_shift = FloatRoll2(Img_Obj.float(), -Yshift)
        Img_Disp = Angle2Screen_byMap_corr(Img_Obj_shift, Img_Map)
        Img_Disp = Img_Disp.permute([2, 0, 1]).to(device)
        Img_Disp.data.clamp_(0, 255)

        # ====================================================================
        # Save Result Image / 保存结果图像
        # ====================================================================
        SavePath_ = SavePath + 'ALL_Img_Disp/'
        if not os.path.exists(SavePath_): 
            os.mkdir(SavePath_)
        temp = Img_Disp.permute([1, 2, 0])
        SavePath__ = SavePath_ + 'F' + str(iframe).zfill(4)
        Func_TiffStackDir.TiffColorSave(temp, SavePath__)

        print(f'  iframe: {iframe}, iframeiter: {iframeiter}, frameindex: {frameindex}')
        print(f'  Yshift: {Yshift}')
        print(f'  Img_Disp shape: {Img_Disp.shape}')
        print(f'  Img_Disp value range: [{Img_Disp.min():.2f}, {Img_Disp.max():.2f}]')
        print(f'  Saved to: {SavePath__}')

    print(f'\n\nAll {FrameNum} frames generated successfully!')
