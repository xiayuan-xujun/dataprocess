# 对json文件进行一个处理操作，包括但不限于删除标签，修改标签，删除指定标签对应图片
import os
import shutil
import json

import cv2
from PIL import Image
from tqdm import tqdm


# 移除只有一个或者0个标签的json文件和对应的图片。
# 这里还是只是做一个判断是否符合要求就好，不宜做过多的功能，否则很容易造成代码的重复编写。
def FindOneLabelJson(jsonPath):
    f = open(jsonPath, encoding="utf-8")
    jsonFile = f.read()
    param_data = json.loads(jsonFile)

    labelNum = len(param_data["shapes"])
    # labelNum = len(param_data["shapes"])

    if labelNum > 1:
        return False
    else:
        return True


def moveOneJson(jsonRootPath, saveMovePath):
    jsonList = []
    for i in os.listdir(jsonRootPath):
        # tmp = os.path.splitext(i)[1]
        if os.path.splitext(i)[1] == '.json':
            jsonList.append(i)

    for index in tqdm(jsonList):
        jsonOnePath = os.path.join(jsonRootPath, index)
        flag = FindOneLabelJson(jsonOnePath)
        if flag:  # 符合移除条件的语句，则执行。
            imagePath = os.path.join(jsonRootPath, (index[:-5] + '.jpg'))
            jsonPath = os.path.join(jsonRootPath, index)
            shutil.move(imagePath, saveMovePath)
            shutil.move(jsonPath, saveMovePath)


def creatJson(imagePath, template_json_path, image_json_path):
    with open(template_json_path, encoding="utf-8") as f:
        jsonFile = f.read()
        originImageJsonData = json.loads(jsonFile)

        # 替换名字，
        originImageJsonData["imagePath"] = imagePath.split('\\')[-1]
        [w, h] = Image.open(imagePath).size
        # print(w)
        # [w, h] = img.size
        originImageJsonData["imageHeight"] = w
        originImageJsonData["imageWidth"] = h

        data = json.dumps(originImageJsonData, indent=1, ensure_ascii=False)
    # print(data)
    with open(image_json_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(data)
    #
    # with open(jsonPath, 'w', encoding='utf-8')as fp2:
    #     json.dump(originImageJsonData, fp2, ensure_ascii=False)


def exchange_label(json_path):
    with open(json_path, encoding="utf-8") as f:
        jsonFile = f.read()
        try:
            originImageJsonData = json.loads(jsonFile)

            tmp = originImageJsonData["ability"]["main_ability_name"]
            if originImageJsonData["ability"]["main_ability_name"] == "非标准缺陷":
                # 替换名字，
                originImageJsonData["ability"]["main_ability_name"] = "刀闸"
                originImageJsonData["ability"]["sub_ability_name"] = "[1]刀闸[竖形]"
                originImageJsonData["ability"]["params"]["service_name"] = "knife_switch_check"
                originImageJsonData["ability"]["ability_value"] = 1

                data = json.dumps(originImageJsonData, indent=1, ensure_ascii=False)
            # print(data)
                with open(json_path, 'w', encoding='utf-8', newline='\n') as f2:
                    f2.write(data)

                f2.close()
        except:
            return
    f.close()


# 按照以下顺序对文件进行排序。 此处以正序车牌为例，其他一次类推
# 右下、左下、左上、右上
def adjust_points(json_path, image_path, dst_image_path):
    f = open(json_path, encoding="utf-8")
    jsonFile = f.read()
    param_data = json.loads(jsonFile)

    src = cv2.imread(image_path)
    # 右下、左下、左上、右上。

    for i in range(len(param_data["shapes"])):
        # i = i - flag
        indexPoints = param_data["shapes"][i]["points"]

        tmp = indexPoints[0]
        # 往图片上绘制点
        for j in range(len(indexPoints)):
            cv2.putText(src, str(j+1), (int(indexPoints[j][0]), int(indexPoints[j][1])), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200), 5)

    cv2.imwrite(dst_image_path, src)
    # 右下判断：
    # print("ok")

def copy_easy_json(image_path, json_path):
    image_lists = os.listdir(image_path)
    for index_image in image_lists:
        one_image_path = os.path.join(image_path, index_image)
        one_json_path = one_image_path.split('.')[0] + '.json'
        with open(json_path, encoding="utf-8") as f2:
            jsonFile = f2.read()
            originImageJsonData = json.loads(jsonFile)
            #  "imagePath": "5-1678361094-1209_YT-54_20230317080709.jpg",
            tmp = originImageJsonData["imagePath"]
            originImageJsonData["imagePath"] = index_image

            data = json.dumps(originImageJsonData, indent=1, ensure_ascii=False)
            # print(data)
            with open(one_json_path, 'w', encoding='utf-8', newline='\n') as f3:
                f3.write(data)

            f3.close()
        f2.close()



def copy_json(preset_json_path, add_json_path, save_file_pth):
    preset_json_lists = os.listdir(preset_json_path)
    add_image_lists = os.listdir(add_json_path)
    for index_preset_json in preset_json_lists:
        if index_preset_json.split('.')[-1] != 'json':
            continue
        else:
            device_id_preset = index_preset_json.split('_')[1]
            for index_add_json in add_image_lists:
                device_id_add = index_add_json.split('_')[0]
                if device_id_add == device_id_preset:
                    origin_image_name = os.path.join(add_json_path, index_add_json)
                    add_image_name = os.path.join(save_file_pth, index_add_json)
                    shutil.copy(origin_image_name, add_image_name)

                    one_preset_json_path = os.path.join(preset_json_path, index_preset_json)
                    add_json_name = os.path.join(save_file_pth, (index_add_json.split('.')[0] + '.json'))
                    shutil.copy(one_preset_json_path, add_json_name)

                    with open(add_json_name, encoding="utf-8") as f2:
                        jsonFile = f2.read()
                        originImageJsonData = json.loads(jsonFile)
                        #  "imagePath": "5-1678361094-1209_YT-54_20230317080709.jpg",
                        tmp = originImageJsonData["imagePath"]
                        originImageJsonData["imagePath"] = index_add_json

                        data = json.dumps(originImageJsonData, indent=1, ensure_ascii=False)
                        # print(data)
                        with open(add_json_name, 'w', encoding='utf-8', newline='\n') as f3:
                            f3.write(data)

                        f3.close()
                    f2.close()


    print("he")



def labelme_to_EIseg(labelme_path, eiseg_path):
    labelme_file_lists = os.listdir(labelme_path)
    for json_index in labelme_file_lists:
        if json_index[-4:] != 'json':
            continue
        else:
            labelme_json_path = os.path.join(labelme_path, json_index)
            eiseg_json_path = os.path.join(eiseg_path, json_index)
            eiseg_list = []
            with open(labelme_json_path, encoding="utf-8") as f1:
                json_file = f1.read()
                json_data = json.loads(json_file)
                for points in json_data["shapes"]:
                    eiseg_point = "{\"name\": \"pig\", \"labelIdx\": 1, \"color\": [244, 108, 59], \"points\":" + str(points["points"]) + "}"
                    eiseg_list.append(eiseg_point)
                    print("ok")
            f1.close()
           # 写入文件
            with open(eiseg_json_path, 'w', encoding='utf-8', newline='\n') as f3:
                f3.write("[")
                # 每次输入一行，加一个逗号。
                len_eiseg_list = len(eiseg_list)
                for t, list_index in enumerate(eiseg_list):
                    f3.write(list_index)
                    if t != len_eiseg_list-1:
                        f3.write(",")
                f3.write("]")


    print("ok")


def delete_eiseg_name(file_path):
    labelme_file_lists = os.listdir(file_path)
    for json_index in labelme_file_lists:
        if json_index[-4:] != 'json':
            continue
        else:
            new_name = json_index[:-len("_labelme.json")]
            new_path = os.path.join(file_path, new_name + '.json')
            old_path = os.path.join(file_path, json_index)
            shutil.move(old_path, new_path)
            print("ok")



if __name__ == '__main__':
    template_json_path = r'F:\workfile\230602-15\save_wordpad\negative\credit_photo_110380_202302031130599265.json'
    file_path = r'F:\workfile\230602-15\save_wordpad\negative\val'

    file_lists = os.listdir(file_path)
    for index in tqdm(file_lists):
        image_path = os.path.join(file_path, index)
        image_json_path = image_path[:-3]+'json'

        creatJson(image_path, template_json_path, image_json_path)