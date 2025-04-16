from zhipuai import ZhipuAI


#语言模型
def LanguageModel(api_key, model, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 请填写您要调用的模型名称
        messages=[
            {"role": "system", "content": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。"},
            {"role": "user", "content": text},
        ],

    )
    results = response.choices[0].message.content
    return results


#推理模型
def InferenceModel(api_key, model, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 请填写您要调用的模型名称
        messages=[
            {"role": "user", "content": text}
        ],
        max_tokens=12000,

    )
    results=response.choices[0].message.content
    return results


#视觉理解
#图像
def VLModel1(api_key, model):
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
                    "url": "temp.png"
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
def ImgModel(api_key, model, text):
    client = ZhipuAI(api_key=api_key)  # 请填写您自己的APIKey

    response = client.images.generations(
        model=model,  # 填写需要调用的模型编码
        prompt=text,
    )
    results=response.data[0].url
    return results


#视频生成
def VidModel(api_key, model, text, quality, with_audio, size, fps):
    client = ZhipuAI(api_key=api_key) # 请填写您自己的APIKey

    response = client.videos.generations(
        model=model,
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

    task_status="PROCESSING"

    #如果没有成功或失败，即循环
    while task_status != "SUCCESS" or "FAIL":


        response = client.videos.retrieve_videos_result(id=id)

        task_status=response.task_status


    if task_status=="FAIL":
        cover_image_url = None
        url = None
    else:
        cover_image_url=response.video_result[0].cover_image_url
        url=response.video_result[0].url

    return cover_image_url, url