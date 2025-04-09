import oss2
import io
import os

from ..TensorAndPil import TensorToPil


def upload_to_oss(image, OSS_ACCESS_KEY, OSS_SECRET_KEY, endpoint, bucket, file_name):
    """ 上传到阿里云OSS """
    auth = oss2.Auth(
        OSS_ACCESS_KEY,
        OSS_SECRET_KEY
    )
    bucket1 = oss2.Bucket(auth, endpoint, bucket)

    # 生成图片字节流
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # 上传文件
    file_name = file_name
    bucket1.put_object(file_name, img_buffer)


    return f"https://{bucket}.{endpoint}/{file_name}"


#AI图片处理
class ImageToUrlOSS:
    ENDPOINT = {
        "华东1（杭州）": "oss-cn-hangzhou.aliyuncs.com",
        "华东2（上海）": "oss-cn-shanghai.aliyuncs.com",
        "华东5（南京-本地地域）": "oss-cn-nanjing.aliyuncs.com",
        "华北1（青岛）": "oss-cn-qingdao.aliyuncs.com",
        "华北2（北京）": "oss-cn-beijing.aliyuncs.com",
        "华北5（呼和浩特）": "oss-cn-huhehaote.aliyuncs.com",
        "华北6（乌兰察布）": "oss-cn-wulanchabu.aliyuncs.com",
        "华南1（深圳）": "oss-cn-shenzhen.aliyuncs.com",
        "华南2（河源）": "oss-cn-heyuan.aliyuncs.com",
        "华南3（广州）": "oss-cn-guangzhou.aliyuncs.com",
        "西南1（成都）": "oss-cn-chengdu.aliyuncs.com",
        "华东6（福州-本地地域）": "oss-cn-fuzhou.aliyuncs.com",
        "华中1（武汉-本地地域）": "oss-cn-wuhan-lr.aliyuncs.com",
        "中国香港": "oss-cn-hongkong.aliyuncs.com",
        "日本（东京）": "oss-ap-northeast-1.aliyuncs.com",
        "韩国（首尔）": "oss-ap-northeast-2.aliyuncs.com",
        "新加坡": "oss-ap-southeast-1.aliyuncs.com",
        "阿联酋（迪拜）": "oss-me-east-1.aliyuncs.com",
    }


    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(s):

        endpoint = list(s.ENDPOINT.keys())
        return {
            "required": {

                "bucket": ("STRING", {"multiline": False, "default": "", "tooltip": "请输入你创建的 Bucket 名称"}),
                "endpoint": (endpoint,),
            },
            "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "OSS_ACCESS_KEY": ("STRING", {"multiline": False, "default": "", "tooltip": "未输入将从系统环境中获取"}),
                "OSS_SECRET_KEY": ("STRING", {"multiline": False, "default": "", "tooltip": "未输入将从系统环境中获取"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("image_url", "mask_url" )
    FUNCTION = "action"
    CATEGORY = "我的节点"

    def action(self, endpoint, bucket, image=None, mask=None, OSS_ACCESS_KEY=None, OSS_SECRET_KEY=None):

        #初始化
        endpoint = self.ENDPOINT[endpoint]
        image_url = None
        mask_url = None
        if OSS_ACCESS_KEY is None:
            OSS_ACCESS_KEY = os.getenv('OSS_ACCESS_KEY')
        if OSS_SECRET_KEY is None:
            OSS_SECRET_KEY = os.getenv('OSS_SECRET_KEY')


        #可选输出
        if image is not None:
            image = TensorToPil(image)
            image_name = "IMAGE/temp.png"
            image_url = upload_to_oss(image, OSS_ACCESS_KEY, OSS_SECRET_KEY, endpoint, bucket, image_name)

        if mask is not None:
            #MASK转IMAGE
            mask = mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])).movedim(1, -1).expand(-1, -1, -1, 3)
            mask = TensorToPil(mask)
            mask_name = "IMAGE/masktemp.png"
            mask_url = upload_to_oss(mask, OSS_ACCESS_KEY, OSS_SECRET_KEY, endpoint, bucket, mask_name)

        return (image_url, mask_url,)
