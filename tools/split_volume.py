import pydicom as pdc
import glob
import numpy as np
import nibabel as nib
import os
from skimage.transform import resize

'''
path = "J:/Dataset/CHAOS_Train_Sets/Train_Sets/CT/*"
folder_list = glob.glob(path)

for folder_path in folder_list:
    files_list = glob.glob(folder_path + '/DICOM_anon/*.dcm')

    print(folder_path)
    print(len(files_list))

    imgs = []
    for file_path in files_list:
        dcm = pdc.dcmread(file_path)
        img = dcm.pixel_array
        imgs.append(img)

    imgs_arr = np.array(imgs)
    print(imgs_arr.shape)
    imgs_arr = imgs_arr.transpose(2, 1, 0)
    print(imgs_arr.shape)

    print(imgs_arr.min())
    print(imgs_arr.max())

    imgs_arr = 255. * (imgs_arr - imgs_arr.min()) / (imgs_arr.max() - imgs_arr.min())
    imgs_arr = imgs_arr.astype(np.uint8)

    print(imgs_arr.min())
    print(imgs_arr.max())

    imgs_arr = resize(imgs_arr, (1, 128, 128, 128))
    print(imgs_arr.shape)
    folder_path_name = os.path.basename(folder_path)

    nii_save = nib.Nifti1Image(imgs_arr, None)
    nib.save(nii_save, 'J:/Dataset/CHAOS_nibabel_norm_res_128/test/' + folder_path_name + '.nii.gz')
'''

path = "J:/Dataset/CHAOS_nibabel_norm/*"
files_list = glob.glob(path)
s_z = 16

for file_path in files_list:
    data_idx = int(os.path.splitext(os.path.splitext(os.path.basename(file_path))[0])[0])
    # data_idx = int(os.path.splitext(os.path.splitext(os.path.basename(file_path))[0])[0].split('_')[1])

    img = nib.load(file_path)
    img_data = img.get_fdata()
    # print(img_data.shape)

    img_data = resize(img_data, [128, 128, 126])
    # print(img_data.shape)

    img_z = img_data.shape[2]
    z_num = int(img_z / s_z)
    # z_num = z_num + 1 # 2 padding
    # print(img_z)
    # print(z_num)

    output_base_path = "J:/Dataset/CHAOS_nibabel_norm_res_128_s_64_pd_2"
    prev_idx = 0
    for i in range (0, z_num):

        if data_idx > 200:
            break

        output_path = output_base_path + '/' + str(i)
        if not os.path.isdir(output_path):
            os.mkdir(output_path)

        cur_idx = prev_idx + s_z

        # img_part = img_data[:, :, (s_z*i):(s_z*(i+1))]
        # img_part = img_data[:, :, int(s_z*i/2):int(s_z*(i+2)/2)]
        img_part = img_data[:, :, prev_idx:cur_idx]
        # print(img_part.shape)

        img_part_nib = nib.Nifti1Image(img_part, None)
        nib.save(img_part_nib, output_base_path + '/' + str(i) + '/' + str(data_idx) + '_' + str(i).zfill(4) + '_s_16.nii.gz')

        # print(i)
        # print(int(s_z*i/2))
        # print(int(s_z*(i+2)/2))
        # print(img_part.shape)

        print(prev_idx)
        print(cur_idx)

        prev_idx = cur_idx - 2

    # exit(0)
    print(str(data_idx) + ' finished')

'''
path = "J:/Dataset/CHAOS_nibabel_norm_res_128/*"
after_path = "J:/Dataset/CHAOS_nibabel_norm_res_128_s_16_c"
files_path = glob.glob(path)

for file in files_path:
    print(file)
    head, file_name = os.path.split(file)
    _, idx = os.path.split(head)
    print(file_name)
    print(idx)

    output_path = after_path + '/' + str(idx)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    img = nib.load(file)
    img_data = img.get_fdata()

    img_resize = resize(img_data, [128, 128, 16])
    img_resize_nib = nib.Nifti1Image(img_resize, None)
    nib.save(img_resize_nib, after_path + '/' + idx + '/' + file_name)
'''
'''
path = "J:/Dataset/HCP_1200_norm_res_128_s_16/*/*"
files_list = glob.glob(path)
for file in files_list:

    img = nib.load(file)
    img_data = img.get_fdata()
    # print(img_data.shape)

    head, file_name = os.path.split(file)
    _, idx = os.path.split(head)

    # print(idx + '/' + file_name)
    print(idx + '/' + file_name + ' ' + str(int(idx) + 1))
    '''
'''
path = "J:/Program/PVDM_modify/output/first_stage_main_CHAOS_42/generated_120000.nii.gz"
img = nib.load(path)
img_data = img.get_fdata()
print(img_data.shape)
'''



