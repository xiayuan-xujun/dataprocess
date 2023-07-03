# txt文件格式,既是yolo系列的txt格式转换成labelme的json格式,也是coco的格式.

import argparse
import json
import os
import numpy as np
import yaml
from tqdm import tqdm
from copy import deepcopy


def process_labelme(anno_path, classes=None):
    with open(anno_path, "r") as jp:
        data = json.load(jp)
    img_width = data["imageWidth"]
    img_height = data["imageHeight"]
    ret = []
    for shape in data["shapes"]:
        if classes is None or shape["label"] in classes.keys():
            x1, y1 = np.min(shape["points"], axis=0)
            x2, y2 = np.max(shape["points"], axis=0)
            ret.append([shape["label"], (x1 + x2) / 2 / img_width, (y1 + y2) / 2 / img_height,
                        (x2 - x1) / img_width, (y2 - y1) / img_height])
    return ret


def process_voc(anno_path, classes=None):
    from xml.dom.minidom import parse
    domTree = parse(anno_path)
    rootNode = domTree.documentElement
    img_width = int(rootNode.getElementsByTagName("width")[0].childNodes[0].data)
    img_height = int(rootNode.getElementsByTagName("height")[0].childNodes[0].data)
    ret = []
    for node in rootNode.getElementsByTagName("object"):
        try:
            cls = node.getElementsByTagName("name")[0].childNodes[0].data
        except:
            continue
        if classes is not None and cls not in classes.keys():
            continue
        x1 = int(float(node.getElementsByTagName("xmin")[0].childNodes[0].data))
        y1 = int(float(node.getElementsByTagName("ymin")[0].childNodes[0].data))
        x2 = int(float(node.getElementsByTagName("xmax")[0].childNodes[0].data))
        y2 = int(float(node.getElementsByTagName("ymax")[0].childNodes[0].data))
        ret.append([cls, (x1 + x2) / 2 / img_width, (y1 + y2) / 2 / img_height,
                    (x2 - x1) / img_width, (y2 - y1) / img_height])
    return ret


process_func = {
    "voc": process_voc,
    "labelme": process_labelme
}
fmt = {
    "voc": "xml",
    "labelme": "json"
}


def main(args):
    classes = args.classes
    classes_list = deepcopy(classes) if classes is not None else []
    classes = {cls: i for i, cls in enumerate(classes)} if classes is not None else None
    classes_index = deepcopy(classes) if classes is not None else {}
    if args.label_type not in ["voc", "labelme"]:
        print("label_type not in {}".format(["voc", "labelme"]))
    data_dir = args.data_dir if args.data_dir[-1] == '/' else args.data_dir + '/'
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        os.symlink(os.path.abspath(data_dir), os.path.join(args.output_dir, "images"))
        os.makedirs(os.path.join(args.output_dir, "labels"))

    for dirname, _, filelist in tqdm(os.walk(data_dir, followlinks=True)):
        label_files = [name for name in filelist if fmt[args.label_type] in name.lower()]
        output_dirname = os.path.join(args.output_dir, 'labels', dirname[len(data_dir):])
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)
        for name in label_files:
            data = process_func[args.label_type](os.path.join(dirname, name), classes)
            for item in data:
                # 跳过空标签
                if item[0] == "":
                    print("{} 存在空标签，跳过".format(os.path.join(dirname, name)))
                    continue
                if item[0] not in classes_list:
                    classes_list.append(item[0])
                    classes_index[item[0]] = len(classes_index)
                item[0] = classes_index[item[0]]
            with open(os.path.join(output_dirname, name.replace(fmt[args.label_type], 'txt')), "w") as f:
                for item in data:
                    f.write("%d\t%.06f\t%.06f\t%.06f\t%.06f\n" % (item[0], item[1], item[2], item[3], item[4]))
    with open(os.path.join(args.output_dir, "data.yaml"), "w") as f:
        root = os.path.abspath(args.output_dir)
        data = {
            "download": None,
            "train": os.path.join(root, 'images/train'),
            "val": os.path.join(root, 'images/val'),
            "test": os.path.join(root, 'images/test'),
            "nc": len(classes_index),
            "names": classes_list
        }
        f.write(yaml.dump(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default=r'F:\DownKyi-1.5.0\Media\0522\image', help="图片、标注路径txt")
    parser.add_argument("--output_dir", type=str, default=r'F:\DownKyi-1.5.0\Media\0522\image', help="输出路径")
    parser.add_argument("--classes", type=str, default=['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
        'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
        'hair drier', 'toothbrush'], nargs='+', help="类别列表")
    parser.add_argument("--label_type", type=str, default='labelme', help="标签格式类型, labelme 和 voc 两种可选")
    args = parser.parse_args()
    main(args)
