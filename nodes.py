import folder_paths
import urllib.request
import requests
import base64
import os
import numpy as np
import torchaudio
import soundfile as sf
import time
import json
import torch
import dashscope

from openai import OpenAI
from http import HTTPStatus
from .TensorAndPil import read_png_info, TensorToPil, PilToTensor

import urllib.request
import os


#云端无法运行

def DownloadUrlToFile(url, file_path):
    try:
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 下载文件并显示进度
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)


        urllib.request.urlretrieve(
            url,
            filename=file_path,
            reporthook=progress if os.isatty(1) else None  # 仅终端显示进度
        )

        return True
    except Exception as e:
        print(f"错误: {str(e)}")
        return False


# 默认填入API_KEY
try:
    default_api_key=os.getenv("DASHSCOPE_API_KEY")
except:
    default_api_key=""




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
def openaiVL1(api_key, base_url, model, text, image, seed):

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
        seed=seed,
    )
    result = completion.choices[0].message.content

    return result

#视觉理解模型接口
def openaiVL2(api_key, base_url, model, text, video_url, seed):

    #输入 Base64 编码的本地文件
    base64_video = encode_file(video_url)
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
                        # 直接传入视频文件时，请将type的值设置为video_url
                        "type": "video_url",
                        "video_url": {"url": f"data:video/mp4;base64,{base64_video}"},
                    },
                    {"type": "text", "text": text},
                ],
            }
        ],
        seed=seed,
    )
    result = completion.choices[0].message.content

    return result


#Qwen多模态接口

#输出类型“文本”

#文本
def Qwen1(api_key, base_url, model, role, text):

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": role},
                       {"role": "user", "content": text},],
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text"],

        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )
    return completion

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
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text"],

        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion

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
                        {"type": "input_audio", "input_audio": {"data": f"data:;base64,{base64_audio}","format": "wav",}},
                        {"type": "text", "text": text},
                    ],
                },
            ],
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text"],

        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion

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
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text"],

        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion


#输出类型“文本+音频”

#文本
def Qwen11(api_key, base_url, model, role, text, audio_voice):

    client = OpenAI(api_key=f"{api_key}", base_url=f"{base_url}")

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"{role}输入：{text}"},],
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text", "audio"],
        audio={"voice": audio_voice, "format": "wav"},
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )
    return completion

#图片
def Qwen22(api_key, base_url, model, role, image, text, audio_voice):

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
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text", "audio"],
        audio={"voice": audio_voice, "format": "wav"},
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion

#音频
def Qwen33(api_key, base_url, model, role, audio, text, audio_voice):

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
                        {"type": "input_audio", "input_audio": {"data": f"data:;base64,{base64_audio}","format": "wav",}},
                        {"type": "text", "text": text},
                    ],
                },
            ],
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text", "audio"],
        audio={"voice": audio_voice, "format": "wav"},
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion

#视频
def Qwen44(api_key, base_url, model, role, video, text, audio_voice):

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
        # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
        modalities=["text", "audio"],
        audio={"voice": audio_voice, "format": "wav"},
        # stream 必须设置为 True，否则会报错
        stream=True,
        stream_options={
            "include_usage": True
        }
    )

    return completion




#语音合成
def TTS(api_key, model, voice, text):
    response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
        model=model,
        api_key=api_key,
        text=text,
        voice=voice,
    )
    return response



#保存音频
def save_audio(audio_data):
    # 设置默认保存路径
    output_path = "./temp/temp_audio.wav"

    # 处理音频数据维度
    waveform = audio_data["waveform"].squeeze(0)  # 去除batch维度

    # 保存音频文件
    torchaudio.save(
        output_path,
        waveform,
        audio_data["sample_rate"],
        format="wav"
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


#流式输出结果合并
def StreamText(completion):
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


#流式输出音频解码
def StreamAudio(completion):
    # 方式1: 待生成结束后再进行解码
    audio_string = ""
    result = []
    for chunk in completion:
        if chunk.choices:
            if hasattr(chunk.choices[0].delta, "audio"):
                try:
                    audio_string += chunk.choices[0].delta.audio["data"]
                except Exception as e:
                    result.append(chunk.choices[0].delta.audio["transcript"])

        else:
            output = ''.join(result)

    wav_bytes = base64.b64decode(audio_string)
    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
    sf.write("./temp/out_audio.wav", audio_np, samplerate=24000)

    return output






#提前定义AI角色
def role1(language):
    role1 = f"你是一个多国语言翻译专家，可以将用户输入的文本进行翻译。确保翻译结果符合目标语言习惯，并考虑到某些词语的文化内涵和地区差异。只回答{language}，不回答任何额外的解释。"
    return role1
def role2(language):
    role2 = f'''你是一个精通多国语言的自然语言大师，可以将用户输入的文本进行翻译，并在保持原文句意不变的情况下，根据文生图提示词的规则对文本进行润色，只回答润色后的{language}结果，不回答任何额外的解释。
                示例1：
                输入：一个孤独的树在夜晚的月光下。
                中文输出：在一个宁静的夜晚，一棵孤零零的树矗立在柔和的月光下。银色的月光沐浴着大地，投下长长的柔和的阴影，在黑暗的天空中突出了那棵树孤独的身影。
                英文输出：A solitary tree stands under the soft glow of the moon on a tranquil night. The silvery moonlight bathes the landscape, casting long, gentle shadows and highlighting the tree's lone figure against the dark sky.
                示例2：
                输入：The quick brown fox jumps over the lazy dog.
                中文输出：在晴朗的蓝天下，开阔的田野上，一只敏捷的棕色狐狸优雅地跳过一只懒惰的狗。
                英文输出：A swift brown fox, elegantly leaping over a lazy dog, in an open field, under a clear blue sky.'''
    return role2
def role3(language):
    role3 = f"你是一个精通多国语言的自然语言提示词专家，可以根据用户输入的主题去描绘一个画面。只回答{language}，不回答任何额外的解释。"
    return role3








#######################################            节点            #######################################






#######################################            AI助手            #######################################
#AI多模态模型
class AI100:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),     #删除"lazy": True以保证优先加载api_key
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1"}),
                "model":(["qwen-omni-turbo", "qwen-omni-turbo-latest", "qwen-omni-turbo-2025-03-26", "qwen-omni-turbo-2025-01-19"],),
                "mode":(["AI翻译", "AI翻译+润色", "主题创意", "图片反推", "音频反推", "视频反推", "自定义", "无"],),
                "out_language":(["英文", "中文"], {"tooltip": "输出语言，如果模式为自定义则不会发生作用"}),
                "out_audio":("BOOLEAN", {"default": False, "tooltip":"是否开启语音输出，开启后输出将可能变得不可控"}),
                "audio_voice":(["Cherry", "Serena", "Ethan", "Chelsie"], {"tooltip": "语音输出音色选择"})

            },
            "optional": {
                "image": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("STRING", {"multiline": False, "tooltip": "输入视频地址"}),
                "role": ("STRING", {"multiline": True, "default": "自定义AI", "tooltip": "输入自定义AI角色"}),
                "text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "AUDIO")
    RETURN_NAMES = ("OutText", "OutAudio")

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"





    def action(self, api_key, base_url, model, mode, out_language, out_audio, audio_voice, role=None, text=None, image=None, audio=None, video=None):

        # 判断输出类型
        if mode == "图片反推":

            role = "You are a helpful assistant."
            if text == None:
                text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            #tensor张量转PIL图片
            image = TensorToPil(image)

            # 保存图片
            image.save("./temp/temp_image.png")
            image = "./temp/temp_image.png"

            if out_audio:
                completion = Qwen22(api_key, base_url, model, role, image, text, audio_voice)
            else:
                completion = Qwen2(api_key, base_url, model, role, image, text)

            # 删除图片
            DelFile(image)


        elif mode == "音频反推":

            role = "You are a helpful assistant."
            if text == None:
                text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            save_audio(audio)
            audio = "./temp/temp_audio.wav"

            if out_audio:
                completion = Qwen33(api_key, base_url, model, role, audio, text, audio_voice)
            else:
                completion = Qwen3(api_key, base_url, model, role, audio, text)

            DelFile(audio)


        elif mode == "视频反推":

            role = "You are a helpful assistant."
            if text == None:
                text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            if out_audio:
                completion = Qwen44(api_key, base_url, model, role, video, text, audio_voice)
            else:
                completion = Qwen4(api_key, base_url, model, role, video, text)


        elif mode == "AI翻译":
            role = role1(out_language)

            if out_audio:
                completion = Qwen11(api_key, base_url, model, role, text, audio_voice)
            else:
                completion = Qwen1(api_key, base_url, model, role, text)

        elif mode == "AI翻译+润色":
            role = role2(out_language)

            if out_audio:
                completion = Qwen11(api_key, base_url, model, role, text, audio_voice)
            else:
                completion = Qwen1(api_key, base_url, model, role, text)

        elif mode == "主题创意":
            role = role3(out_language)

            if out_audio:
                completion = Qwen11(api_key, base_url, model, role, text, audio_voice)
            else:
                completion = Qwen1(api_key, base_url, model, role, text)

        elif mode == "自定义":

            if out_audio:
                completion = Qwen11(api_key, base_url, model, role, text, audio_voice)
            else:
                completion = Qwen1(api_key, base_url, model, role, text)


        else:
            #模式为“无”，文本原封不动，音频输出为无
            OutText = text
            OutAudio = None



        #如果启用音频输出
        if mode != "无":
            if out_audio:
                OutText = StreamAudio(completion)

                audio_path = "./temp/out_audio.wav"
                waveform, sample_rate = torchaudio.load(audio_path)
                audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}

                OutAudio = audio
            else:
                OutText =  StreamText(completion)
                OutAudio = None

        return (OutText, OutAudio, )

#通用AI助手
class AI101:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1"}),
                "model": ("STRING", {"multiline": False, "default": "deepseek-v3"}),
                "temperature": ("FLOAT", {"default": 1.3,"min": 0.0,"max": 2,"step": 0.1,"round": False, "display": "number", "tooltip": "较高的值将使输出更加随机，而较低的值将使其更加集中和确定性"}),
                "mode": (["AI翻译", "AI翻译+润色", "自定义", "无"],),
                "out_language": (["英文", "中文"], {"tooltip": "输出语言，如果模式为自定义则不会发生作用"}),
                "role": ("STRING", {"multiline": True, "tooltip": "输入自定义AI角色"}),
                "text": ("STRING", {"multiline": True}),
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
            elif mode == "主题创意":
                role = role3(out_language)
            else:
                role = f"{role}"


            text = openai(api_key, base_url, model, temperature, role, text)



        return (text,)



#######################################            AI视觉理解            #######################################
#AI图片理解
class AI102:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1"}),
                "model": (["qwen-vl-max", "qwen-vl-max-latest", "qwen-vl-plus", "qwen-vl-plus-latest", "qwen2-vl-7b-instruct", "qwen2-vl-72b-instruct", "qwen2.5-vl-7b-instruct", "qwen2.5-vl-72b-instruct", "qvq-72b-preview"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1}),
                "mode": (["默认", "简短", "详细"],),
                "out_language": (["英文", "中文"], {"tooltip": "输出语言"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, mode, out_language, image, seed):

        #tensor张量转PIL图片
        image = TensorToPil(image)


        # 保存图片
        image.save("./temp/temp_image.png")
        image = "./temp/temp_image.png"


        if mode == "默认":
            text = f"图中描绘的是什么景象?提示词反推，直接描述，无需引导句，输出{out_language}"
        else:
            text = f"图中描绘的是什么景象?提示词反推，直接描述，无需引导句，描述尽量{mode}，输出{out_language}"


        text = openaiVL1(api_key, base_url, model, text, image, seed)

        # 删除图片
        DelFile(image)

        return (text,)

#AI视频理解
class AI1021:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "video_url": ("STRING",{"multiline": False, "default": ""}),
                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1"}),
                "model": (["qwen-vl-max", "qwen-vl-max-latest", "qwen-vl-plus"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1}),
                "mode": (["默认", "简短", "详细"],),
                "out_language": (["英文", "中文"], {"tooltip": "输出语言"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, base_url, model, mode, out_language, video_url, seed):

        if mode == "默认":
            text = f"这段视频描绘的是什么景象?提示词反推，直接描述，无需引导句，输出{out_language}"
        else:
            text = f"这段视频描绘的是什么景象?提示词反推，直接描述，无需引导句，描述尽量{mode}，输出{out_language}"


        text = openaiVL2(api_key, base_url, model, text, video_url, seed)



        return (text,)

#AI图片处理
class AI103:
    MODE = {
        "全局风格化": "stylization_all",
        "局部风格化": "stylization_local",
        "指令编辑": "description_edit",
        "局部重绘": "description_edit_with_mask",
        "去水印": "remove_watermark",
        "扩图": "expand",
        "图像超分": "super_resolution",
        "图像上色": "colorization",
        "线稿生图": "doodle",
        "垫图": "control_cartoon_feature"
    }


    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(s):

        mode = list(s.MODE.keys())
        return {
            "required": {
                "image_url":("STRING",),
                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "mode": (mode,),
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "mask_url": ("STRING",),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING", )
    RETURN_NAMES = ("image", "url" )
    FUNCTION = "action"
    CATEGORY = "我的节点"

    def action(self, api_key, mode, text, image_url, mask_url=None):
        function = self.MODE[mode]


        if mode == "图像超分":
            upscale_factor=2
        else:
            upscale_factor=None


        if mode == "扩图":
            value=1.5
        else:
            value=None

        if mode != "局部重绘":
            mask_url = None


        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"

        headers = {
            "X-DashScope-Async": "enable",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "wanx2.1-imageedit",
            "input": {
                "function": function,
                "prompt": text,
                "base_image_url": image_url,
                "mask_image_url": mask_url
            },
            "parameters": {
                "upscale_factor": upscale_factor,
                "top_scale": value,
                "bottom_scale": value,
                "left_scale": value,
                "right_scale": value,
                "n": 1
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 检查HTTP错误

            print("请求成功！响应内容：")
            print(response.json()['output'])

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if response:
                print(f"响应状态码: {response.status_code}")
                print(f"错误详情: {response.text}")

        # 状态查询
        task_id = f"{response.json()['output']['task_id']}"
        task_status = response.json()['output']['task_status']

        print(f"任务ID: {task_id}")
        print(f"状态: {task_status}")
        if task_status == 'PENDING':

            url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

            headers = {"Authorization": f"Bearer {api_key}"}

            time.sleep(2.5)

            while task_status != 'SUCCEEDED':

                # 需要查询的任务ID（替换为实际ID）

                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()  # 检查HTTP错误

                    result = response.json()
                    task_status = result['output']['task_status']

                    print(f"状态: {task_status}")
                    print(result)


                except requests.exceptions.RequestException as e:
                    print(f"请求失败: {e}")
                    if 'response' in locals():
                        print(f"响应状态码: {response.status_code}")
                        print(f"错误详情: {response.text}")

                if task_status == 'FAILED':
                    break



                time.sleep(2.5)
            if task_status == 'SUCCEEDED':
                print("任务成功！")
                url = result['output']['results'][0]['url']


                #PIL图片转terson张量
                terson = PilToTensor(url)

                return (terson, url,)
            if task_status == 'FAILED':
                print(f"响应状态码: {response.status_code}")
                print(f"错误类型: {response.json()['output']['code']}")
                print(f"错误详情: {response.json()['output']['message']}")
                raise ValueError(f"{response.json()['output']['code']}:{response.json()['output']['message']}")
                pass

                return ()



#AI语音合成
class AI104:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "model": (["qwen-tts"],),
                "audio_voice":(["Cherry", "Serena", "Ethan", "Chelsie"], {"tooltip": "语音输出音色选择"}),
                "text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, audio_voice, text):

        response=TTS(api_key, model, audio_voice, text)

        url=response["output"]["audio"]["url"]

        audio_path = "./temp/out_audio.wav"

        DownloadUrlToFile(url, audio_path)

        waveform, sample_rate = torchaudio.load(audio_path)
        audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}



        return (audio,)




######################################            AI图片生成            #######################################
#Flux助手高级
class AI200:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "model": (["flux-schnell", "flux-dev", "flux-merged"],),
                "seed":("INT", {"default": 0, "min": 0, "max": 4294967290}),
                "steps":("INT", {"default": 0, "min": 0, "max": 100,"step": 1,"round": False, "display": "number", "tooltip": "如果为0，自动配置。 flux-schnell 模型官方默认 steps 为4，flux-dev 模型官方默认 steps 为50，flux-merged 默认 steps 为30。"}),
                "guidance":("FLOAT", {"default": 3.5, "min": 0, "max": 100, "step": 0.1,"round": False, "display": "number", "tooltip": "指导度量值，用于在图像生成过程中调整模型的创造性与文本指导的紧密度。较高的值会使得生成的图像更忠于文本提示，但可能减少多样性；较低的值则允许更多创造性，增加图像变化。默认值为3.5。"}),
                "size": (["1024*1024", "512*1024", "768*512", "768*1024", "1024*576", "576*1024"],),
                "offload":(["False", "True"], {"default": "False","tooltip": "一个布尔值，表示是否在采样过程中将部分计算密集型组件临时从GPU卸载到CPU，以减轻内存压力或提升效率。如果您的系统资源有限或希望加速采样过程，可以启用此选项，默认为False。", } ),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, seed, steps, guidance, size, offload, prompt):

        if steps == 0:
            if model == "flux-schnell":
                steps=4
            elif model == "flux-dev":
                steps=50
            else:
                steps=30
        else:
            pass


        rsp = dashscope.ImageSynthesis.call(api_key=api_key,
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


            #url转tensor张量
            tensor = PilToTensor(url)


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

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "model": (["flux-schnell(快速)", "flux-dev(高质量)", "flux-merged(优化)"],),
                "size": (["1024*1024", "512*1024", "768*512", "768*1024", "1024*576", "576*1024"],),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(selft, api_key, model, size, prompt):

        if model == "flux-schnell(快速)":
            model = "flux-schnell"
            steps = 4
        elif model == "flux-dev(高质量)":
            model = "flux-dev"
            steps = 50
        else:
            model = "flux-merged"
            steps = 30


        rsp = dashscope.ImageSynthesis.call(api_key=api_key,
                                  model=model,
                                  steps=steps,
                                  size=size,
                                  prompt=prompt,)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            print(rsp.usage)

            # 解析 JSON
            url = rsp["output"]["results"][0]["url"]


            #url转tensor张量
            tensor = PilToTensor(url)


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
                "if_True": (any_type, {}),
                "if_False": (any_type, {}),
                "a": (any_type, {}),
                "b": (any_type, {}),
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

    CATEGORY = "我的节点/Tools"

    def action(self, mode, a=None, b=None, if_True=None, if_False=None):
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

        #尝试比较张量
        try:
            boolean  = torch.equal(a, b)
            if mode == "==":
                boolean=boolean
            if mode == "!=":
                if boolean:
                    boolean=False
                else:
                    boolean=True
            else:
                boolean = boolean
                print("请注意，张量比较仅支持'=='和'!='，其余模式均默认为'=='")
        except:
            boolean = comparators[mode](a, b)

        if boolean:
            output1, output2 = if_True, if_False
        else:
            output1, output2 = if_False, if_True

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
                "bool": ("BOOLEAN", {"default": True}),
                "if_True": (any_type, {}),
                "if_False": (any_type, {}),
            }
        }


    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("anything",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点/Tools"

    def action(self, bool, if_True=None, if_False=None):
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
                "size":("STRING", {"multiline": False, "default": "1024*1024", "tooltip": "输入格式：宽度*高度（例如：800*600）"}),
            },
        }

    RETURN_TYPES = ("INT",
                    "INT",)
    RETURN_NAMES = ("width",
                    "height",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点/Tools"

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




#文件计数器
class ScanFileCountNode:
    """
    自定义节点：文件夹文件计数器
    功能：统计指定路径下所有文件数量（默认过滤子目录）
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "./input",
                    "dynamicPrompts": False,
                    "multiline": False,
                    "tooltip": "文件夹路径"
                }),
            },
            "optional": {
                "include_subfolders": ("BOOLEAN", {"default": False, "tooltip": "是否包含子文件夹"}),
                "file_extensions": ("STRING", {"default": "*", "tooltip": "计数文件格式，如png、jpg、txt，*表示所有文件"})
            }
        }
    RETURN_TYPES = ("INT", "STRING")  # 输出类型
    RETURN_NAMES = ("文件数量", "统计信息")  # 输出名称

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点/Tools"
    def action(self, folder_path, include_subfolders=False, file_extensions="*"):
        # 输入验证
        if not os.path.exists(folder_path):
            raise ValueError(f"路径不存在: {folder_path}")
        if not os.path.isdir(folder_path):
            raise ValueError(f"路径不是目录: {folder_path}")

        # 处理文件扩展名过滤
        ext_list = [ext.strip().lower() for ext in file_extensions.split(",")] if file_extensions != "*" else []

        # 递归扫描函数
        def scan_recursive(path):
            count = 0
            for entry in os.scandir(path):
                if entry.is_file():
                    if not ext_list or entry.name.split('.')[-1].lower() in ext_list:
                        nonlocal total_count
                        total_count += 1
                elif include_subfolders and entry.is_dir():
                    scan_recursive(entry.path)
            return count

        total_count = 0
        scan_recursive(folder_path)

        # 生成统计信息
        ext_info = "所有类型" if file_extensions == "*" else f"指定类型: {file_extensions}"
        scan_mode = "包含子目录" if include_subfolders else "仅当前目录"
        stats = f"扫描完成 | 路径: {folder_path}\n模式: {scan_mode}\n类型: {ext_info}\n总任务数: {total_count}"

        return (total_count, stats, )



#读取png元数据
class ReadPngInfo:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {
            "required":{
                "image": (sorted(files), {"image_upload": True})},
                }
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("parameters", "json_data")
    FUNCTION = "action"
    CATEGORY = "我的节点/PngInfo"

    def action(self, image):
        path=folder_paths.get_annotated_filepath(image)
        # 读取数据
        parameters, json_data = read_png_info(path)

        return (parameters, json_data, )

#写入png元数据
class WritePngInfo:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "./user/default/workflows", "tooltip": "保存路径"}),
                "name": ("STRING", {"default": "name"}),
                "json_data": ("STRING", {"multiline": True, "default": ""})
            }
        }
    RETURN_TYPES = ()

    FUNCTION = "action"
    CATEGORY = "我的节点/PngInfo"

    OUTPUT_NODE = True
    def action(self, json_data, path, name):

        number=int(time.time())
        path=f"{path}/{name}{number}.json"
        try:
            with open(path, "w", encoding='utf-8') as f:
                f.write(json_data)


        except:
            pass

        return ()




#从配置文件获取数据
class GetDataFromConfig:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        # 获取节点文件所在目录路径

        config_path = "./custom_nodes/ComfyUI-My-Nodes/config.json"

        keys = []
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                keys = list(config.keys())
                if not keys:
                    keys = ["[ERROR] Empty config"]
        except Exception as e:
            print(f"❌ ConfigValueNode load failed: {str(e)}")
            keys = ["[ERROR] Load config"]

        return {
            "required": {
                "key": (keys, {"default": keys[0] if keys else "error"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    FUNCTION = "action"
    CATEGORY = "我的节点/Tools"

    def action(self, key):
        # 再次读取确保获取最新值

        config_path = "./custom_nodes/ComfyUI-My-Nodes/config.json"

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            if key.startswith("[ERROR]"):
                return ("Configuration error detected",)

            value = config.get(key, f"[MISSING] Key: {key}")

        except FileNotFoundError:
            value = "[ERROR] config.json not found"
        except json.JSONDecodeError:
            value = "[ERROR] Invalid JSON format"
        except Exception as e:
            value = f"[ERROR] {str(e)}"

        return (value,)










# 节点注册

NODE_CLASS_MAPPINGS = {"Multimodal AI assistant": AI100,
                       "General AI assistant": AI101,
                       "AI Vision-Language-image": AI102,
                       "AI Vision-Language-video": AI1021,
                       "AI image processing": AI103,
                       "AI TTS": AI104,
                       "Flux assistant(advanced)": AI200,
                       "Flux assistant(simple)": AI201,
                       "Digital Comparator": comparator,
                       "Output Selector": choice,
                       "Aspect Ratio Preset": size,
                       "Scan File Count Node": ScanFileCountNode,
                       "Read Png Info": ReadPngInfo,
                       "Write Png Info": WritePngInfo,
                       "Get Data From Config":GetDataFromConfig
                       }
NODE_DISPLAY_NAME_MAPPINGS = {"Multimodal AI assistant": "AI多模态助手",
                              "General AI assistant": "AI通用助手",
                              "AI Vision-Language-image": "AI图片理解",
                              "AI Vision-Language-video": "AI视频理解",
                              "AI image processing": "AI图片处理",
                              "AI TTS": "AI语音合成",
                              "Flux assistant(advanced)": "Flux助手(高级)",
                              "Flux assistant(simple)": "Flux助手(简易)",
                              "Digital Comparator": "比较分流器",
                              "Output Selector": "选择输出器",
                              "Aspect Ratio Preset": "宽高比",
                              "Scan File Count Node": "文件计数器",
                              "Read Png Info": "读取PNG元数据",
                              "Write Png Info": "写入PNG元数据",
                              "Get Data From Config": "从配置文件获取数据"
                              }


print("\n\033[32;36m=============================comfyui-my-nodes基础节点已载入成功=============================\033[0m")


#尝试导入可选节点，如未安装环境依赖则失败
try:
    from .oss.oss import ImageToUrlOSS

    # 节点注册
    NODE_CLASS_MAPPINGS["Image To Url(OSS)"] = ImageToUrlOSS
    NODE_DISPLAY_NAME_MAPPINGS["Image To Url(OSS)"] = "图片转URL(OSS)"

    print("\033[32;36m===============================comfyui-my-nodes已载入oss节点===============================\033[0m\n")
except:
    pass
