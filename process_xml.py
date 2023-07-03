#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023/2/16 14:55
# @Author: Xunjun
# 对xml文件进行一些常规的处理
import os
import shutil
import xml.etree.ElementTree as ET
from tqdm import tqdm

def xml_reader(filename):
    """ Parse a PASCAL VOC xml file """
    tree = ET.parse(filename)
    root = tree.getroot()
    size = tree.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)
    objects = []
    for obj in tree.findall('object'):
        obj_struct = {}
        obj_struct['name'] = obj.find('name').text  # 类别名称
        bbox = obj.find('bndbox')
        obj_struct['bbox'] = [int(bbox.find('xmin').text),
                              int(bbox.find('ymin').text),
                              int(bbox.find('xmax').text),
                              int(bbox.find('ymax').text)]
        objects.append(obj_struct)

    tree.remove()
    return width, height, objects


def del_xml_element(xml_path, del_label):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for obj in root.findall('object'):
        object_label = obj.find('name').text
        if object_label in del_label:
            root.remove(obj)  # 删除当前的标签值。

    tree.write(xml_path)

    for obj in root.findall('object'):
        object_label = obj.find('name').text
        if object_label == 'knife':
            return 1
        # print("ok")

def copy_file(object_file_path, refeance_file):
    file_lists = os.listdir(object_file_path)
    for index in file_lists:
        file_path = os.path.join(object_file_path, index)
        # tmp = file_path[-3:]
        if file_path[-3:] != 'xml':
            xml_path = file_path[:-3] + 'xml'
            tmp = os.path.exists(xml_path)
            if not os.path.exists(xml_path):
                shutil.copy(refeance_file, xml_path)
        else:
            continue


if __name__=='__main__':
    # xml_path = r'E:\workFile\datasets\image\val'
    # refeance_file = r'E:\workFile\datasets\image\000000 (2).xml'
    # copy_file(xml_path, refeance_file)
    del_label = ['person']
    xml_root_path = r'E:\workFile\datasets\image\new\train\混合'
    save_file_root_path = r'E:\workFile\datasets\image\new\train\混合me_output'
    if not os.path.exists(save_file_root_path):
        os.makedirs(save_file_root_path)

    xml_lists = os.listdir(xml_root_path)
    for index in tqdm(xml_lists):
        file_path = os.path.join(xml_root_path, index)
        if os.path.splitext(file_path)[-1] == '.xml':
            xml_path = file_path
            if del_xml_element(xml_path, del_label) == 1:
                src_image_path = os.path.join(xml_root_path, index[:-3]+'jpg')
                src_xml_path = os.path.join(xml_root_path, index)

                dst_image_path = os.path.join(save_file_root_path, (index[:-3]+'jpg'))
                dst_xml_path = os.path.join(save_file_root_path, index)
                shutil.copy(src_xml_path, dst_xml_path)
                shutil.copy(src_image_path, dst_image_path)

    # del_xml_element(xml_path, del_label)