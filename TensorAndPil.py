import numpy as np
import torch
import io
from PIL import Image
from PIL.PngImagePlugin import PngInfo




#读取图片元数据
def read_png_info(image_path):
    with Image.open(image_path) as img:
        pnginfo = img.text
        parameters = pnginfo.get("parameters", "")
        workflow = pnginfo.get("workflow", "")
    return parameters, workflow





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
