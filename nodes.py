from openai import OpenAI
import base64
import json
import os
import numpy as np
import torch
import io
from PIL import Image
from http import HTTPStatus
from dashscope import ImageSynthesis
from .TensorAndPil import TensorToPil, PilToTensor
import requests


#复制easy-use定义“*”类型
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")





# tensor张量转PIL图片
def TensorToPil(tensor):
    tensor = tensor
    # 确保张量在CPU并移除批次维度
    if tensor.is_cuda:
        tensor = tensor.cpu()  # 移回CPU
    tensor = tensor.squeeze(0)  # 移除批次维度 (1, H, W, C) -> (H, W, C)

    # 转换为numpy数组并反归一化
    array = tensor.detach().numpy()  # 断开计算图并转换
    array = (array * 255.0).astype(np.uint8)  # 反归一化并转为uint8

    # 转换为PIL图像
    image = Image.fromarray(array)
    return image

#urlPIL图片转tensor张量
def PilToTensor(url):
    response = url
    # 转换为PIL图像对象
    image = Image.open(io.BytesIO(response.content)).convert("RGB")  # 强制转为 RGB

    # PIL图像转换为numpy.array
    pixels = np.array(image).astype(np.uint8) / 255.0  # 归一化到 [0,1]

    # numpy.array转换为tensor张量
    tensor = torch.from_numpy(pixels)
    tensor = tensor.unsqueeze(0)  # 添加批次维度
    if torch.cuda.is_available():
        tensor = tensor.to('cuda')  # 移动到 GPU

    return tensor





#openai接口
def openai(api_key, base_url, model, temperature, role, text):

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": text},
        ],
        stream=False,
        temperature=temperature
    )
    result = response.choices[0].message.content

    return result


#图片理解模型接口
def openaiVL(api_key, base_url, model, text, image):

    #输入 Base64 编码的本地文件
    base64_image = encode_image(image)

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        # 需要注意，传入Base64，图像格式（即image/{format}）需要与支持的图片列表中的Content Type保持一致。"f"是字符串格式化的方法。
                        # PNG图像：  f"data:image/png;base64,{base64_image}"
                        # JPEG图像： f"data:image/jpeg;base64,{base64_image}"
                        # WEBP图像： f"data:image/webp;base64,{base64_image}"
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {"type": "text", "text": text},
                ],
            }
        ],
    )
    result = completion.choices[0].message.content

    return result


#  Base64 编码格式
def encode_image(image):
    with open(image, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


#Qwen多模态接口
def Qwen(api_key, base_url, model, language, image):

    #输入 Base64 编码的本地文件
    base64_image = encode_image(image)

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {"type": "text", "text": f"提示词反推，直接描述，无需引导句，{language}"},
                ],
            },
        ],
        # 设置输出数据的模态，当前支持["text"]
        modalities=["text"],
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )



    #流式输出结果合并
    result = []  # 初始化结果列表

    for chunk in completion:
        if chunk.choices:
            delta = chunk.choices[0].delta
            # 提取有效内容并添加到结果列表
            if delta.content not in (None, ''):
                result.append(delta.content)

    # 合并所有内容片段
    output = ''.join(result)

    return output

#删除文件
def DelImg(image):
    # 先检查文件是否存在（避免 FileNotFoundError）
    if os.path.exists(image):
        try:
            os.remove(image)  # 永久删除文件

        except Exception as e:
            pass
    else:
        pass






#AI多模态模型
class AI100:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "image":("IMAGE",),

                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "base_url": ("STRING",{"multiline": False, "default": "","lazy": True}),
                "model":(["qwen-omni-turbo", "qwen-omni-turbo-latest", "qwen-omni-turbo-2025-01-19"],),

                "language":(["中文", "英文"],),

            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"





    def action(sefl, api_key, base_url, model, language, image):

        #tensor张量转PIL图片
        image = TensorToPil(image)


        # 保存图片
        image.save("temp.png")
        image = "temp.png"

        if language == "中文":
            language = "请输出中文"
        else:
            language = "请输出英文"


        text = Qwen(api_key, base_url, model, language, image)

        # 删除图片
        DelImg(image)

        return (text,)

#AI助手
class AI101:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "base_url": ("STRING", {"multiline": False, "default": "","lazy": True}),
                "model": ("STRING", {"multiline": False, "default": "","lazy": True}),
                "temperature": ("FLOAT", {"default": 1.3,"min": 0.0,"max": 2,"step": 0.1,"round": False, "display": "number", "tooltip": "较高的值将使输出更加随机，而较低的值将使其更加集中和确定性", "lazy": False}),
                "mode": (["AI翻译", "AI翻译+润色", "自定义", "无"],),
                "role": ("STRING", {"multiline": True, "default": "自定义AI", "tooltip": "输入自定义AI角色", "lazy": True}),
                "text": ("STRING", {"multiline": True, "default": "","lazy": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, temperature, mode, role, text):

        #判断模式
        if mode == "无":
            text = text
        else:
            if mode == "AI翻译":
                role = "你是一个中英文翻译专家，可以将用户输入的文本翻译成英文。确保翻译结果符合中英文语言习惯，并考虑到某些词语的文化内涵和地区差异。只回答英文，不回答任何额外的解释。"
            elif mode == "AI翻译+润色":
                role = '''你是一个精通中英文的自然语言大师，可以将用户输入的文本翻译成英文，并在保持原文句意不变的情况下，根据文生图提示词的规则对文本进行润色，只回答润色后的英文结果，不回答任何额外的解释。
                示例1：
                原文：一个孤独的树在夜晚的月光下。
                翻译：A solitary tree stands under the soft glow of the moon on a tranquil night. The silvery moonlight bathes the landscape, casting long, gentle shadows and highlighting the tree's lone figure against the dark sky.
                示例2：
                原文：The quick brown fox jumps over the lazy dog.
                翻译：A swift brown fox, elegantly leaping over a lazy dog, in an open field, under a clear blue sky.'''
            else:
                role = f"{role}"


            text = openai(api_key, base_url, model, temperature, role, text)



        return (text,)

#AI图片理解
class AI102:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "base_url": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "model": (["qwen2.5-vl-7b-instruct", "qwen2.5-vl-72b-instruct ", "qvq-72b-preview"],),
                "mode": (["默认", "简短", "详细"],),
                "language": (["中文", "英文"],),

            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, mode, language, image):

        #tensor张量转PIL图片
        image = TensorToPil(image)


        # 保存图片
        image.save("temp.png")
        image = "temp.png"


        if mode == "默认":
            text = f"提示词反推，直接描述，无需引导句，输出{language}"
        else:
            text = f"提示词反推，直接描述，无需引导句，描述尽量{mode}，输出{language}"


        text = openaiVL(api_key, base_url, model, text, image)

        # 删除图片
        DelImg(image)

        return (text,)


# NODE_CLASS_MAPPINGS = {"多模态AI助手": AI100,
#                        "AI助手": AI101,
#                        "AI图片理解": AI102,}
# NODE_DISPLAY_NAME_MAPPINGS = {"多模态AI助手": "多模态AI助手",
#                               "AI助手": "AI助手",
#                               "AI图片理解": "AI图片理解",}








#Flux助手高级
class AI200:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "model": (["flux-schnell", "flux-dev", "flux-merged"],),
                "seed":("INT", {"default": 0, "min": 0, "max": 4294967290}),
                "steps":("INT", {"default": 30, "min": 0, "max": 100,"step": 1,"round": False, "display": "number", "tooltip": "图片生成的推理步数，如果不提供，则默认为30。 flux-schnell 模型官方默认 steps 为4，flux-dev 模型官方默认 steps 为50。", "lazy": False}),
                "guidance":("FLOAT", {"default": 3.5, "min": 0, "max": 100, "step": 0.1,"round": False, "display": "number", "tooltip": "指导度量值，用于在图像生成过程中调整模型的创造性与文本指导的紧密度。较高的值会使得生成的图像更忠于文本提示，但可能减少多样性；较低的值则允许更多创造性，增加图像变化。默认值为3.5。", "lazy": False}),
                "size": (["1024*1024", "512*1024", "768*512", "768*1024", "1024*576", "576*1024"],),
                "offload":(["False", "True"], {
                    "default": "False",
                    "tooltip": "一个布尔值，表示是否在采样过程中将部分计算密集型组件临时从GPU卸载到CPU，以减轻内存压力或提升效率。如果您的系统资源有限或希望加速采样过程，可以启用此选项，默认为False。", } ),
                "prompt": ("STRING", {"multiline": True, "default": "","lazy": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, seed, steps, guidance, size, offload, prompt):
        rsp = ImageSynthesis.call(api_key=api_key,
                                  model=model,
                                  seed=seed,
                                  steps=steps,
                                  guidance=guidance,
                                  size=size,
                                  offload=offload,
                                  prompt=prompt,
                                  )
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            print(rsp.usage)






            # 解析 JSON
            url = rsp["output"]["results"][0]["url"]

            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误

            #url转tensor张量
            tensor = PilToTensor(response)


        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

        return (tensor, )


#Flux助手简易
class AI201:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "model": (["flux-schnell(快速)", "flux-dev(高质量)", "flux-merged(优化)"],),
                "size": (["1024*1024", "512*1024", "768*512", "768*1024", "1024*576", "576*1024"],),
                "prompt": ("STRING", {"multiline": True, "default": "","lazy": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, size, prompt):
        if model == "flux-schnell(快速)":
            model = "flux-schnell"
            steps = 4
        elif model == "flux-dev(高质量)":
            model = "flux-dev"
            steps = 50
        else:
            model = "flux-merged"
            steps = 30


        rsp = ImageSynthesis.call(api_key=api_key,
                                  model=model,
                                  steps=steps,
                                  size=size,
                                  prompt=prompt,)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            print(rsp.usage)

            # 解析 JSON
            url = rsp["output"]["results"][0]["url"]

            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误

            #url转tensor张量
            tensor = PilToTensor(response)


        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

        return (tensor, )



# NODE_CLASS_MAPPINGS = {"Flux助手(高级)": AI200,
#                        "Flux助手(简易)": AI201,}
# NODE_DISPLAY_NAME_MAPPINGS = {"Flux助手(高级)": "Flux助手(高级)",
#                               "Flux助手(简易)": "Flux助手(简易)",}











#比较分流器
class comparator:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["==", "!=", ">=", ">", "<=", "<",],),
            },
            "optional": {
                "a": ("FLOAT",{"default": 0.0, "step": 0.1, "round": False, "display": "number","lazy": False}),
                "b": ("FLOAT",{"default": 0.0, "step": 0.1, "round": False, "display": "number","lazy": False}),
                "input1": (any_type, {}),
                "input2": (any_type, {}),
            },
        }

    RETURN_TYPES = (any_type,
                    any_type,
                    "BOOLEAN")
    RETURN_NAMES = ("output1",
                    "output2",
                    "boolean")

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"

    def action(self, mode, a, b, input1, input2):
        comparators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">=": lambda a, b: a >= b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            "<": lambda a, b: a < b
        }

        if mode not in comparators:
            return (None, None, None)

        boolean = comparators[mode](a, b)
        if boolean:
            output1, output2 = input1, input2
        else:
            output1, output2 = input2, input1

        return (output1, output2, boolean, )




#选择输出器
class choice:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "bool": ("BOOLEAN", {"default": None, "lazy": True}),
                "any1": (any_type, {}),
                "any2": (any_type, {}),
            }
        }


    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("anything",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"

    def action(self, bool, any1, any2):
        if bool == True:
            anything = any1
        elif bool == False:
            anything = any2
        else:
            anything = any1

        return (anything,)






# NODE_CLASS_MAPPINGS = {"比较器": comparator,
#                        "选择器": choice,}
# NODE_DISPLAY_NAME_MAPPINGS = {"比较器": "比较器",
#                               "选择器": "选择器",}



#宽高比预设
class size:

    PRESETS = {
        "16:9": (1280, 720),
        "9:16": (720, 1280),
        "4:3": (1000, 750),
        "3:4": (750, 1000),
        "2:1": (1000, 500),
        "1:2": (500, 1000),
        "自定义": (1024, 1024)  # 默认值
    }



    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        presets = list(s.PRESETS.keys())
        presets.insert(0, "自定义")  # 确保自定义选项在首位
        return {
            "required": {
                "mode": (presets, {"default": "自定义"}),
                "size":("STRING", {"multiline": False, "default": "1024*1024", "tooltip": "输入格式：宽度*高度（例如：800*600）", "lazy": True}),
            },
        }

    RETURN_TYPES = ("INT",
                    "INT",)
    RETURN_NAMES = ("width",
                    "height",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"

    def action(self, mode, size):
        # 使用预设值或解析自定义尺寸
        if mode != "自定义":
            return self.PRESETS[mode]

        try:
            width_str, height_str = size.replace(' ', '').split('*')
            width = int(width_str)
            height = int(height_str)

            # 添加合理性检查
            if width <= 0 or height <= 0:
                raise ValueError("尺寸必须为正值")

        except (ValueError, AttributeError) as e:
            print(f"⚠️ 无效尺寸输入，已使用默认值 1024x1024。错误详情：{str(e)}")
            width, height = self.PRESETS["自定义"]


        return (width, height, )


# NODE_CLASS_MAPPINGS = {"宽高比": size,}
# NODE_DISPLAY_NAME_MAPPINGS = {"宽高比": "宽高比",}





NODE_CLASS_MAPPINGS = {"多模态AI助手": AI100,
                       "AI助手": AI101,
                       "AI图片理解": AI102,
                       "Flux助手(高级)": AI200,
                       "Flux助手(简易)": AI201,
                       "比较分流器": comparator,
                       "选择输出器": choice,
                       "宽高比": size,
                       }
NODE_DISPLAY_NAME_MAPPINGS = {"多模态AI助手": "多模态AI助手",
                              "AI助手": "AI助手",
                              "AI图片理解": "AI图片理解",
                              "Flux助手(高级)": "Flux助手(高级)",
                              "Flux助手(简易)": "Flux助手(简易)",
                              "比较分流器": "比较分流器",
                              "选择输出器": "选择输出器",
                              "宽高比": "宽高比",
                              }


