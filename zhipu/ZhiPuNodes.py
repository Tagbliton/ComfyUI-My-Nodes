import time

from zhipuai import ZhipuAI
from ..nodes import encode_file, DelFile
from ..TensorAndPil import TensorToPil, PilToTensor



#语言模型
def LanguageModel(api_key, model, do_sample, temperature, top_p, role, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 请填写您要调用的模型名称
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": text},
        ],
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
    )
    results = response.choices[0].message.content
    return results


#推理模型
def InferenceModel(api_key, model, do_sample, temperature, top_p, max_tokens, role, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 请填写您要调用的模型名称
        messages=[
            {"role": "system", "content": role},# System Prompt建议设置为:Please think deeply before your response.
            {"role": "user", "content": text}
        ],
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,

    )
    results=response.choices[0].message.content
    return results


#视觉理解
#图像
def VLModel1(api_key, model, image):
    client = ZhipuAI(api_key=api_key) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=[
          {
            "role": "user",
            "content": [
              {
                "type": "image_url",
                "image_url": {
                    "url": image
                }
              },
              {
                "type": "text",
                "text": "请描述这个图片"
              }
            ]
          }
        ]
    )

    results=response.choices[0].message.content
    return results

#视频
def VLModel2(api_key, model, video_base64):
    client = ZhipuAI(api_key=api_key) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=[
          {
            "role": "user",
            "content": [
              {
                "type": "video_url",
                "video_url": {
                    "url" : video_base64
                }
              },
              {
                "type": "text",
                "text": "请仔细描述这个视频"
              }
            ]
          }
        ]
    )
    results = response.choices[0].message.content
    return results


#图像生成
def ImgModel(api_key, model, quality, size, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey

    response = client.images.generations(
        model=model,  # 填写需要调用的模型编码
        prompt=text,
        quality=quality,
        size=size,
    )

    results=response.data[0].url
    return results


#视频生成
def VidModel(api_key, model, quality, with_audio, fps, size, text, image):
    client = ZhipuAI(api_key=api_key) # 请填写您自己的APIKey

    response = client.videos.generations(
        model=model,
        image_url=image,  # 提供的图片URL地址或者 Base64 编码
        prompt=text,
        quality=quality,  # 输出模式，"quality"为质量优先，"speed"为速度优先
        with_audio=with_audio,
        size=size,  # 视频分辨率，支持最高4K（如: "3840x2160"）
        fps=fps,  # 帧率，可选为30或60
    )
    print(response.id)
    print(response.task_status)
    id=response.id
    task_status=response.task_status

    #状态处理
    time.sleep(2)
    if task_status=="PROCESSING":

        #如果没有成功或失败，即循环
        while task_status != "SUCCESS":


            response = client.videos.retrieve_videos_result(id=id)

            task_status=response.task_status

            time.sleep(2)


    if task_status=="FAIL":
        cover_image_url = None
        url = None
    else:
        cover_image_url=response.video_result[0].cover_image_url
        url=response.video_result[0].url

    return cover_image_url, url






#智谱语言模型
class AI301:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": (["GLM-4-Flash-250414", "GLM-4-FlashX", "GLM-4-Air-250414", "GLM-4-Long", "GLM-4-AirX", "GLM-4-Plus"],),
                "do_sample":("BOOLEAN", {"display": True, "tooltip": "当do_sample为true时，启用采样策略；当do_sample为false时，温度和top_p等采样策略参数将不生效，模型输出随机性会大幅度降低。默认值为true。"}),
                "temperature":("FLOAT", {"default": 0.95, "min": 0.00, "max": 1.00, "step": 0.01,"round": False, "display": "number", "tooltip": "采样温度，控制输出的随机性，必须为正数 取值范围是：[0.0,1.0]， 默认值为 0.95，值越大，会使输出更随机，更具创造性；值越小，输出会更加稳定或确定 建议您根据应用场景调整 top_p 或 temperature 参数，但不要同时调整两个参数"}),
                "top_p":("FLOAT", {"default": 0.70, "min": 0.00, "max": 1.00, "step": 0.01,"round": False, "display": "number", "tooltip": "用温度取样的另一种方法，称为核取样 取值范围是：[0.0, 1.0]，默认值为 0.70 模型考虑具有 top_p 概率质量 tokens 的结果 例如：0.10 意味着模型解码器只考虑从前 10% 的概率的候选集中取 tokens 建议您根据应用场景调整 top_p 或 temperature 参数，但不要同时调整两个参数"}),
                "role": ("STRING", {"multiline": True, "default": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。"}),
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, do_sample, temperature, top_p, role, text):

        results=LanguageModel(api_key, model, do_sample, temperature, top_p, role, text)

        return (results, )



#智谱推理模型
class AI302:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": (["GLM-Z1-Flash", "GLM-Z1-Air", "GLM-Z1-AirX"],),
                "do_sample": ("BOOLEAN", {"display": True, "tooltip": "当do_sample为true时，启用采样策略；当do_sample为false时，温度和top_p等采样策略参数将不生效，模型输出随机性会大幅度降低。默认值为true。"}),
                "temperature": ("FLOAT", {"default": 0.95, "min": 0.00, "max": 1.00, "step": 0.01, "round": False, "display": "number", "tooltip": "采样温度，控制输出的随机性，必须为正数 取值范围是：[0.0,1.0]， 默认值为 0.95，值越大，会使输出更随机，更具创造性；值越小，输出会更加稳定或确定 建议您根据应用场景调整 top_p 或 temperature 参数，但不要同时调整两个参数"}),
                "top_p": ("FLOAT", {"default": 0.70, "min": 0.00, "max": 1.00, "step": 0.01, "round": False, "display": "number", "tooltip": "用温度取样的另一种方法，称为核取样 取值范围是：[0.0, 1.0]，默认值为 0.70 模型考虑具有 top_p 概率质量 tokens 的结果 例如：0.10 意味着模型解码器只考虑从前 10% 的概率的候选集中取 tokens 建议您根据应用场景调整 top_p 或 temperature 参数，但不要同时调整两个参数"}),
                "max_tokens": ("INT", {"default": 12000, "min": 0, "max": 30000, "step": 1, "round": False, "display": "number", "tooltip": "模型输出的最大token数，最大输出为30k。"}),
                "role": ("STRING", {"multiline": True, "default": "Please think deeply before your response."}),
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "action"

    # OUTPUT_NODE = False

    CATEGORY = "我的节点"

    def action(self, api_key, model, do_sample, temperature, top_p, max_tokens, role, text):

        results = InferenceModel(api_key, model, do_sample, temperature, top_p, max_tokens, role, text)

        return (results,)




#智谱视觉理解
class AI303:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "image": ("IMAGE", ),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": (["glm-4v-flash", "glm-4v-plus-0111"],),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, image):
        #tensor张量转PIL图片
        image = TensorToPil(image)

        # 保存图片
        image.save("temp.png")
        image = "temp.png"

        results=VLModel1(api_key, model, image)

        # 删除图片
        DelFile(image)

        return (results, )




#智谱图像生成
class AI304:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": (["CogView-3-Flash", "CogView-4-250304"],),
                "quality":(["standard", "hd"], {"tooltip": "生成图像的质量，默认为 standard\nhd : 生成更精细、细节更丰富的图像，整体一致性更高，耗时约20 秒\nstandard :快速生成图像，适合对生成速度有较高要求的场景，耗时约 5-10 秒\n此参数仅支持cogview-4-250304 。"}),
                "size": (["1024x1024", "768x1344", "864x1152", "1344x768", "1152x864", "1440x720", "720x1440"],),
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, quality, size, text):

        url=ImgModel(api_key, model, quality, size, text)

        image=PilToTensor(url)

        return (image, )





#智谱视频生成
class AI305:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "model": (["CogVideoX-Flash", "CogVideoX-2"], {"tooltip": "说明：cogvideox-flash：不支持quality 、size 、fps 参数设置"}),
                "quality": (["quality", "speed"],),
                "with_audio":("BOOLEAN", {"default": False, "tooltip": "是否生成 AI 音效。默认值: False（不生成音效）。"}),
                "fps": ([30, 60],),
                "size": (["720x480", "1024x1024", "1280x960", "960x1280", "1920x1080", "1080x1920", "2048x1080", "3840x2160"],),
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "image": ("IMAGE", )
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING",)
    RETURN_NAMES = ("cover_image", "url",)


    FUNCTION = "action"

    #OUTPUT_NODE = False

    CATEGORY = "我的节点"


    def action(self, api_key, model, quality, with_audio, fps, size, text, image=None):

        if image is not None:
            image=TensorToPil(image)
            image.save("temp.png")
            image = "temp.png"

        cover_image_url, url=VidModel(api_key, model, quality, with_audio, fps, size, text, image)

        if image is not None:
            # 删除图片
            DelFile(image)
        cover_image=PilToTensor(cover_image_url)

        return (cover_image, url, )