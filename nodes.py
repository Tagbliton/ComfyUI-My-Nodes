import requests
import base64
import os
import numpy as np
import torchaudio
import soundfile as sf
import time


from openai import OpenAI
from http import HTTPStatus
from dashscope import ImageSynthesis
from .TensorAndPil import TensorToPil, PilToTensor



# 默认填入API_KEY
default_api_key=os.getenv("DASHSCOPE_API_KEY")




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
        messages=[{"role": "user", "content": f"{role}输入：'{text}'"},],
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


#保存音频
def save_audio(audio_data):
    # 设置默认保存路径
    output_path = ("temp.wav")

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
def StreamAudio1(completion):
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
    sf.write("./temp/out_temp.wav", audio_np, samplerate=24000)

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


#AI多模态模型
class AI100:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1","lazy": True}),
                "model":(["qwen-omni-turbo", "qwen-omni-turbo-latest", "qwen-omni-turbo-2025-03-26", "qwen-omni-turbo-2025-01-19"],),
                "mode":(["AI翻译", "AI翻译+润色", "主题创意", "图片反推", "音频反推", "视频反推", "自定义", "无"],),
                "out_language":(["英文", "中文"], {"tooltip": "输出语言，如果模式为自定义则不会发生作用"}),
                "out_audio":("BOOLEAN", {"default": False, "tooltip":"是否开启语音输出"}),
                "audio_voice":(["Cherry", "Serena", "Ethan", "Chelsie"], {"tooltip": "语音输出音色选择"})

            },
            "optional": {
                "image": ("IMAGE",),
                "audio": ("AUDIO",),
                "video": ("STRING", {"multiline": False, "tooltip": "输入视频地址"}),
                "role": ("STRING", {"multiline": True, "default": "自定义AI", "tooltip": "输入自定义AI角色", "lazy": True}),
                "text": ("STRING", {"multiline": True, "default": "", "lazy": True}),
            },
        }

    RETURN_TYPES = ("STRING", "AUDIO")
    RETURN_NAMES = ("OutText", "OutAudio")

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"





    def action(self, api_key, base_url, model, mode, out_language, out_audio, audio_voice, role, text ,image=None, audio=None, video=None):

        # 判断输出类型
        if mode == "图片反推":

            role = "You are a helpful assistant."
            text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            #tensor张量转PIL图片
            image = TensorToPil(image)

            # 保存图片
            image.save("temp.png")
            image = "temp.png"

            if out_audio:
                completion = Qwen22(api_key, base_url, model, role, image, text, audio_voice)
            else:
                completion = Qwen2(api_key, base_url, model, role, image, text)

            # 删除图片
            DelFile(image)


        elif mode == "音频反推":

            role = "You are a helpful assistant."
            text = f"提示词反推，直接描述，无需引导句，请输出{out_language}"

            save_audio(audio)
            audio = "temp.wav"

            if out_audio:
                completion = Qwen33(api_key, base_url, model, role, audio, text, audio_voice)
            else:
                completion = Qwen3(api_key, base_url, model, role, audio, text)

            DelFile(audio)


        elif mode == "视频反推":

            role = "You are a helpful assistant."
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
            completion = text

        if mode == "无":
            OutText = completion
        else:
            if out_audio:
                OutText = StreamAudio1(completion)

                audio_path = "./temp/out_temp.wav"
                waveform, sample_rate = torchaudio.load(audio_path)
                audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}

                OutAudio = audio
            else:
                OutText = StreamText(completion)
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
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1","lazy": True}),
                "model": ("STRING", {"multiline": False, "default": "deepseek-v3","lazy": True}),
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
            elif mode == "主题创意":
                role = role3(out_language)
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
                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "base_url": ("STRING", {"multiline": False, "default": "https://dashscope.aliyuncs.com/compatible-mode/v1", "lazy": True}),
                "model": (["qwen2.5-vl-7b-instruct", "qwen2.5-vl-72b-instruct", "qvq-72b-preview"],),
                "mode": (["默认", "简短", "详细"],),
                "out_language": (["英文", "中文"], {"tooltip": "输出语言"}),

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

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
                "model": (["flux-schnell", "flux-dev", "flux-merged"],),
                "seed":("INT", {"default": 0, "min": 0, "max": 4294967290}),
                "steps":("INT", {"default": 50, "min": 0, "max": 100,"step": 1,"round": False, "display": "number", "tooltip": "图片生成的推理步数，如果不提供，则默认为30。 flux-schnell 模型官方默认 steps 为4，flux-dev 模型官方默认 steps 为50。", "lazy": False}),
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
        if api_key is None:
            api_key=os.getenv("DASHSCOPE_API_KEY")
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

                "api_key": ("STRING", {"multiline": False, "default": default_api_key}),
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


    def action(selft, api_key, model, size, promp):
        if api_key is None:
            api_key=os.getenv("DASHSCOPE_API_KEY")
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
                "bool": ("BOOLEAN", {"default": True, "lazy": True}),
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

    CATEGORY = "我的节点"
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






class GetApiFromConfig:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "./custom_nodes/ComfyUI-My-Nodes/config.txt", "tooltip": "文件路径"})
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("API_KEY", )
    FUNCTION = "action"
    CATEGORY = "我的节点"

    def action(self, file_path):
        api_key = ""


        try:
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Config file not found: {file_path}")

            # 读取并解析文件
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("api_key="):
                        api_key = line.split("=", 1)[1].strip()

            if api_key == "YourApiKey":
                raise ValueError("API key not found in config file")
            # 验证结果
            if not api_key:
                raise ValueError("API key not found in config file")


        except Exception as e:
            print(f"Error reading config file: {str(e)}")
            return ("", )  # 返回空值或抛出异常

        return (api_key, )
    @classmethod
    def IS_CHANGED(s, api_key):
       return ""



# 节点注册

NODE_CLASS_MAPPINGS = {"Multimodal AI assistant": AI100,
                       "General AI assistant": AI101,
                       "AI Vision-Language": AI102,
                       "AI image processing": AI103,
                       "Flux assistant(advanced)": AI200,
                       "Flux assistant(simple)": AI201,
                       "Digital Comparator": comparator,
                       "Output Selector": choice,
                       "Aspect Ratio Preset": size,
                       "Scan File Count Node": ScanFileCountNode,
                       "Get Api From Config":GetApiFromConfig
                       }
NODE_DISPLAY_NAME_MAPPINGS = {"Multimodal AI assistant": "多模态AI助手",
                              "General AI assistant": "通用AI助手",
                              "AI Vision-Language": "AI图片理解",
                              "AI image processing": "AI图片处理",
                              "Flux assistant(advanced)": "Flux助手(高级)",
                              "Flux assistant(simple)": "Flux助手(简易)",
                              "Digital Comparator": "比较分流器",
                              "Output Selector": "选择输出器",
                              "Aspect Ratio Preset": "宽高比",
                              "Scan File Count Node": "文件计数器",
                              "Get Api From Config": "从配置文件获取API"
                              }


print("\n\033[32;36m=============================comfyui-my-nodes基础节点已载入成功=============================\033[0m")


#尝试导入可选节点，如未安装环境依赖则失败
try:
    from .oss.oss import ImageToUrl

    # 节点注册

    NODE_CLASS_MAPPINGS = {"Multimodal AI assistant": AI100,
                           "General AI assistant": AI101,
                           "AI Vision-Language": AI102,
                           "AI image processing": AI103,
                           "Flux assistant(advanced)": AI200,
                           "Flux assistant(simple)": AI201,
                           "Image To Url(OSS)": ImageToUrlOSS,
                           "Digital Comparator": comparator,
                           "Output Selector": choice,
                           "Aspect Ratio Preset": size,
                           "Scan File Count Node": ScanFileCountNode,
                           "Get Api From Config": GetApiFromConfig
                           }
    NODE_DISPLAY_NAME_MAPPINGS = {"Multimodal AI assistant": "多模态AI助手",
                                  "General AI assistant": "通用AI助手",
                                  "AI Vision-Language": "AI图片理解",
                                  "AI image processing": "AI图片处理",
                                  "Flux assistant(advanced)": "Flux助手(高级)",
                                  "Flux assistant(simple)": "Flux助手(简易)",
                                  "Image To Url(OSS)": "图片转URL(OSS)",
                                  "Digital Comparator": "比较分流器",
                                  "Output Selector": "选择输出器",
                                  "Aspect Ratio Preset": "宽高比",
                                  "Scan File Count Node": "文件计数器",
                                  "Get Api From Config": "从配置文件获取API"
                                  }
    print("\033[32;36m===============================comfyui-my-nodes已载入可选节点===============================\033[0m\n")
except:
    print("\033[33;36m===============================comfyui-my-nodes未载入可选节点===============================\033[0m\n")
    pass
