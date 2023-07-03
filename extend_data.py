#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023/6/2 10:30
# @Author: Xunjun
# 扩展目标检测框的左右方向
import json
import os
import random

import cv2
from tqdm import tqdm


def addjust_points(zero_point, json_data, image_label, image_name):
    """
    :param zero_point: 坐标系的新零点。
    :param json_data: 原始坐标的json文件
    :param image_label: 排除的label标签
    :param json_name: 保存的json_name名字
    :return data: 返回修改后的json文件
    """
    json_data["imageData"] = None
    json_data["imagePath"] = f"{image_name}"
    # json转换之后的宽高也是需要进行改变。
    # "imageHeight": 4624,
    # "imageWidth": 3468
    # zero_point = [Ymin, Xmin, Ymax, Xmax]
    json_data["imageHeight"] = zero_point[2] - zero_point[0]
    json_data["imageWidth"] = zero_point[3] - zero_point[1]
    # 对应的其他位置的坐标也需要进行调整
    label_index_sum = 0
    for i in range(len(json_data["shapes"])):
    # for i, index2 in enumerate(json_data["shapes"]):
        label_index = i - label_index_sum
        index2 = json_data["shapes"][label_index]
        label = index2["label"]
        if label in image_label:
            # pop()直接删除i位置上的元素。
            json_data["shapes"].pop(label_index)  # 这里删除后，i就发生了变化，需要同步变化了。
            label_index_sum += 1
            # json_data = filter(lambda x: x['ename']!=label, json_data)
        else:
            if json_data["shapes"][label_index]["label"] == "phone":
                json_data["shapes"][label_index]["label"] = "other"

            for j in range(len(index2["points"])):
                json_data["shapes"][label_index]["points"][j][0] -= zero_point[1]
                if json_data["shapes"][label_index]["points"][j][0] < 0:
                    json_data["shapes"][label_index]["points"][j][0] = 0
                json_data["shapes"][label_index]["points"][j][1] -= zero_point[0]
                if json_data["shapes"][label_index]["points"][j][1] < 0:
                    json_data["shapes"][label_index]["points"][j][1] = 0
                # print("0k")

        data = json.dumps(json_data, indent=1, ensure_ascii=False)

    return data


def extend_data(image_path, json_path, image_label='wordpad', image_num=4):
    """
    :param image_path: 输入图片的路径
    :param json_path: 输入json的路径
    :param image_label: 以哪个框为标准来进行处理
    :param image_num: 一幅图片生成几幅增强图片
    :return: newImageData, zero_points ： 增强后的图片和新的坐标原点位置。
    """
    image_data = cv2.imread(image_path)
    size = image_data.shape
    h = size[1]  # 宽度
    w = size[0]  # 高度

    newImageData = []
    zero_points = []

    with open(json_path, 'rb+') as fp:
        imageJsonData = json.load(fp)

        # image_copy_json = imageJsonData
        # 多标签考虑， 具有分合标签的情况
        for index in imageJsonData["shapes"]:
            label = index["label"]
            if label not in image_label:
                continue
            else:
                points = index["points"]    # 两个点的坐标
                # 获取四个点的坐标， 同时调整各个点的值
                # 原始图片的标签需要添加进去
                Xmax = int(max(points[0][0], points[1][0]))
                Ymax = int(max(points[0][1], points[1][1]))
                Xmin = int(min(points[0][0], points[1][0]))
                Ymin = int(min(points[0][1], points[1][1]))

                zero_point = [Ymin, Xmin, Ymax, Xmax]

                newImageData.append(image_data[Ymin:Ymax, Xmin:Xmax])
                zero_points.append(zero_point)

                for i in range(image_num):
                    # 不能越界
                    Xmin = int(min(points[0][0], points[1][0])) + random.choice((-1, 1)) * int(random.random() * h/50)
                    if Xmin > h:
                        Xmin = h
                    elif Xmin < 0:
                        Xmin = 0
                    else:
                        Xmin = Xmin

                    Ymin = int(min(points[0][1], points[1][1])) + random.choice((-1, 1)) * int(random.random() * w/50)
                    if Ymin > w:
                        Ymin = w
                    elif Ymin < 0:
                        Ymin = 0
                    else:
                        Ymin = Ymin

                    Xmax = int(max(points[0][0], points[1][0])) + random.choice((-1, 1)) * int(random.random() * h/50)
                    if Xmax > h:
                        Xmax = h
                    elif Xmax < 0:
                        Xmax = 0
                    else:
                        Xmax = Xmax

                    Ymax = int(max(points[0][1], points[1][1])) + random.choice((-1, 1)) * int(random.random() * w/50)
                    if Ymax > w:
                        Ymax = w
                    elif Ymax < 0:
                        Ymax = 0
                    else:
                        Ymax = Ymax

                    zero_point = [Ymin, Xmin, Ymax, Xmax]

                    newImageData.append(image_data[Ymin:Ymax, Xmin:Xmax])
                    zero_points.append(zero_point)
    fp.close()
    return newImageData, zero_points


if __name__=="__main__":
    file_path = r'F:\workfile\230602-15\save_wordpad\wordpad_labelme\train'
    save_path = r'F:\workfile\230602-15\save_wordpad\wordpad_word_detection_train\train'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_lists = os.listdir(file_path)
    image_label = ['wordpad']
    for file_index in tqdm(file_lists):
        image_path = os.path.join(file_path, file_index)
        # print(file_index)
        if image_path[-4:] != 'json':
            json_path = os.path.join(file_path, file_index[:-3] + 'json')
            newImageData, zero_points = extend_data(image_path, json_path, image_label, image_num=4)
            if newImageData is None:
                continue
            for i, image_data in enumerate(newImageData):
                new_image_name = os.path.join(save_path, (file_index[:-4] + "_" + str(i + 1) + '.jpg'))
                new_json_name = os.path.join(save_path, (file_index[:-4] + "_" + str(i + 1) + '.json'))
                zero_point = zero_points[i]

                # 读取新的json文件，并且保存
                with open(json_path, 'rb+') as fp:
                    image_copy_json = json.load(fp)
                    data = addjust_points(zero_point, image_copy_json, image_label, image_name=(file_index[:-4] + "_" + str(i + 1) + '.jpg'))

                    with open(new_json_name, 'w', encoding='utf-8', newline='\n') as f3:
                        f3.write(data)
                cv2.imwrite(new_image_name, image_data)
        else:
            continue
    # print("ok")


#   "imagePath": "IMG_20230503_1134521.jpg",
#   "imageData": null,
#   "imageHeight": 2381,
#   "imageWidth": 1343
