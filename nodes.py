import requests
import base64
import json
import os
import numpy as np
import torch
import io
import torchaudio

from PIL import Image
from openai import OpenAI
from http import HTTPStatus
from dashscope import ImageSynthesis
from .TensorAndPil import TensorToPil, PilToTensor



#定义“*”类型
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")

#  Base64 编码格式
def encode_file(file):
    with open(file, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


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
    base64_image = encode_file(image)

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




#Qwen多模态接口

#文本
def Qwen1(api_key, base_url, model, role, text):

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": role},
                       {"role": "user", "content": text},],
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

#图片
def Qwen2(api_key, base_url, model, role, image, text):

    # 输入 Base64 编码的本地文件
    base64_image = encode_file(image)

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": role}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        {"type": "text", "text": text},
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

#音频
def Qwen3(api_key, base_url, model, role, audio, text):

    # 输入 Base64 编码的本地文件
    base64_audio = encode_file(audio)

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": role}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_audio", "input_audio": {"data": f"data:;base64,{base64_audio}","format": "mp3",}},
                        {"type": "text", "text": text},
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

#视频
def Qwen4(api_key, base_url, model, role, video, text):

    # 输入 Base64 编码的本地文件
    base64_video = encode_file(video)

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": role}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "video_url", "video_url": {"url": f"data:;base64,{base64_video}"}},
                        {"type": "text", "text": text},
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

#保存音频
def save_audio(audio_data):
    """极简音频保存函数
    Args:
        audio_data (dict): 包含waveform和sample_rate的音频字典
        output_path (str): 可选保存路径，默认输出到comfyui根目录的temp.mp3
    """
    # 设置默认保存路径
    output_path = ("temp.mp3")

    # 处理音频数据维度
    waveform = audio_data["waveform"].squeeze(0)  # 去除batch维度

    # 保存音频文件
    torchaudio.save(
        output_path,
        waveform,
        audio_data["sample_rate"],
        format="mp3"
    )


#删除文件
def DelFile(file):
    # 先检查文件是否存在（避免 FileNotFoundError）
    if os.path.exists(file):
        try:
            os.remove(file)  # 永久删除文件

        except Exception as e:
            pass
    else:
        pass

#提前定义AI角色
def role1(language):
    role1 = f"你是一个多国语言翻译专家，可以将用户输入的文本进行翻译。确保翻译结果符合目标语言习惯，并考虑到某些词语的文化内涵和地区差异。只回答{language}，不回答任何额外的解释。"
    return role1
def role2(language):
    role2 = f'''你是一个精通多国语言的自然语言大师，可以将用户输入的文本进行翻译，并在保持原文句意不变的情况下，根据文生图提示词的规则对文本进行润色，只回答润色后的{language}结果，不回答任何额外的解释。
                示例1：
                原文：一个孤独的树在夜晚的月光下。
                翻译：A solitary tree stands under the soft glow of the moon on a tranquil night. The silvery moonlight bathes the landscape, casting long, gentle shadows and highlighting the tree's lone figure against the dark sky.
                示例2：
                原文：The quick brown fox jumps over the lazy dog.
                翻译：A swift brown fox, elegantly leaping over a lazy dog, in an open field, under a clear blue sky.'''
    return role2


#AI多模态模型
class AI100:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": "", "lazy": True}),
                "base_url": ("STRING", {"multiline": False, "default": "","lazy": True}),
                "model":(["qwen-omni-turbo", "qwen-omni-turbo-latest", "qwen-omni-turbo-2025-01-19"],),
                "mode":(["AI翻译", "AI翻译+润色", "图片反推", "音频反推", "视频反推", "自定义", "无"],),
                "out_language":(["英文", "中文"], {"tooltip": "输出语言，如果模式为自定义则不会发生作用"}),

            },
            "optional": {
                "image": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("VIDEO",),
                "role": ("STRING", {"multiline": True, "default": "自定义AI", "tooltip": "输入自定义AI角色", "lazy": True}),
                "text": ("STRING", {"multiline": True, "default": "", "lazy": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"





    def action(self, api_key, base_url, model, mode, out_language, role, text ,image=None, audio=None, video=None):


        if mode == "图片反推":

            role = "You are a helpful assistant."
            text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            #tensor张量转PIL图片
            image = TensorToPil(image)

            # 保存图片
            image.save("temp.png")
            image = "temp.png"

            text = Qwen2(api_key, base_url, model, role, image, text)

            # 删除图片
            DelFile(image)


        elif mode == "音频反推":

            role = "You are a helpful assistant."
            text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            save_audio(audio)
            audio = "temp.mp3"
            text = Qwen3(api_key, base_url, model, role, audio, text)

            DelFile(audio)


        elif mode == "视频反推":

            role = "You are a helpful assistant."
            text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            video.save("temp.mp4")
            video = "temp.mp4"

            text = Qwen4(api_key, base_url, model, role, video, text)

            DelFile(video)

        elif mode == "AI翻译":
            role = role1(out_language)

            text = Qwen1(api_key, base_url, model, role, text)

        elif mode == "AI翻译+润色":
            role = role2(out_language)

            text = Qwen1(api_key, base_url, model, role, text)

        elif mode == "自定义":

            text = Qwen1(api_key, base_url, model, role, text)

        else:
            text = text

        return (text,)

#通用AI助手
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
                "out_language": (["英文", "中文"], {"tooltip": "输出语言，如果模式为自定义则不会发生作用"}),
                "role": ("STRING", {"multiline": True, "default": "自定义AI", "tooltip": "输入自定义AI角色", "lazy": True}),
                "text": ("STRING", {"multiline": True, "default": "","lazy": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, temperature, mode, out_language, role, text):

        #判断模式
        if mode == "无":
            text = text
        else:
            if mode == "AI翻译":
                role = role1(out_language)
            elif mode == "AI翻译+润色":
                role = role2(out_language)
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
                "model": (["qwen2.5-vl-7b-instruct", "qwen2.5-vl-72b-instruct", "qvq-72b-preview"],),
                "mode": (["默认", "简短", "详细"],),
                "out_language": (["中文", "英文"], {"tooltip": "输出语言"}),

            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, mode, out_language, image):

        #tensor张量转PIL图片
        image = TensorToPil(image)


        # 保存图片
        image.save("temp.png")
        image = "temp.png"


        if mode == "默认":
            text = f"提示词反推，直接描述，无需引导句，输出{out_language}"
        else:
            text = f"提示词反推，直接描述，无需引导句，描述尽量{mode}，输出{out_language}"


        text = openaiVL(api_key, base_url, model, text, image)

        # 删除图片
        DelFile(image)

        return (text,)

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
                "if_True": (any_type, {}),
                "if_False": (any_type, {}),
            }
        }


    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("anything",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"

    def action(self, bool, if_True, if_False):
        if bool == True:
            anything = if_True
        elif bool == False:
            anything = if_False
        else:
            anything = if_True

        return (anything,)


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





NODE_CLASS_MAPPINGS = {"Multimodal AI assistant": AI100,
                       "General AI assistant": AI101,
                       "AI Vision-Language": AI102,
                       "Flux assistant(advanced)": AI200,
                       "Flux assistant(simple)": AI201,
                       "Digital Comparator": comparator,
                       "Output Selector": choice,
                       "Aspect Ratio Preset": size,
                       }
NODE_DISPLAY_NAME_MAPPINGS = {"Multimodal AI assistant": "多模态AI助手",
                              "General AI assistant": "通用AI助手",
                              "AI Vision-Language": "AI图片理解",
                              "Flux assistant(advanced)": "Flux助手(高级)",
                              "Flux assistant(simple)": "Flux助手(简易)",
                              "Digital Comparator": "比较分流器",
                              "Output Selector": "选择输出器",
                              "Aspect Ratio Preset": "宽高比",
                              }
