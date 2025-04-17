# My-Nodes

AI助手

一个支持在Comfyui中使用阿里百炼模型库及一些小工具的插件

`Github上为测试版`

稳定版可以在comfyui-manager管理器下载最新版本



## 📑 说明书
- 阿里百炼大模型-技术文档

  `https://help.aliyun.com/zh/model-studio/getting-started/what-is-model-studio`


- 如何获取API

  `https://help.aliyun.com/zh/model-studio/user-guide/first-api-call-to-qwen`


- 默认base_url

  `https://dashscope.aliyuncs.com/compatible-mode/v1`


- API填写的三种方式：
  1. 直接输入节点的文本框
  
  3. （便捷）获取的API可以填写到插件根目录下的配置文件中,以便通过节点`从配置文件获取数据`调取

      将 ':' 后双引号中的内容替换为你的**api_key**，具体操作细节详见` -功能- >> -从配置文件获取数据- `

  3. （推荐）将API写入环境变量
  
      右键此电脑>>属性>>高级系统设置>>高级-环境变量>>下方系统变量中新建
      ```
      变量名：DASHSCOPE_API_KEY
      变量值：你的API
      ```
      **重启comfyui后生效,如未生效可尝试重启电脑或检查输入**

      使用此方法后每次新建节点都会预先填入API

## 🚀 更新内容
- **Github 测试版**
  
	_添加节点`AI视频理解`_

	_`AI图片理解`添加更多可选模型_

	_`AI图片处理`和`AI视频理解`添加种子输入_

	_修复节点`Flux助手(简易)`文本输入错误问题_

	_优化节点`Flux助手`API输入机制_

	_`比较分流器`节点可以输入更多类型进行比较，已测试`INT.FLOAT.BOOLEAN.STRING.IMAGE.MASK.AUDIO.LATENT`等大部分类型_
  
- **v1.1.2**

	_添加节点`AI图片处理`_

	_添加可选节点`图片转URL(oss)`_

	_修复节点`从配置文件获取数据`逻辑_

	_优化`Flux助手`获取文本逻辑_

	_`比较分流器`和`选择输出器`可以进行空输入_

	_添加示例工作流_

## 💡 当前计划

- 添加智谱AI开放平台中免费模型可选节点模块



## 📠 图片转URL(OSS)（可选节点）

- 使用阿里云OSS对象存储将图片转为URL

- 如何加载该节点
  
  在comfyui命令行界面输入`pip install oss2`后重启即可成功加载节点

- 如何使用该节点
  
  创建对象存储OSS
  
  创建Bucket官方教程
  
  ```https://developer.aliyun.com/adc/tutorial/612670```

  Bucket权限设置
  
  关闭阻止公共访问，读写权限设置为公共读
  
  随后在右上角个人-Accesskey获取节点所需的AccessKey ID及AccessKey Secret


## ❓ 相关问题

- 连接错误：提示`Connection error`，请检查网络连接或IP代理

- 图片反推：如果使用**多模态AI助手**提示`'NoneType' object has no attribute 'is_cuda'`，可以尝试使用**AI图片理解**节点
 
- 图片处理：提示格式错误`InvalidParameter:Value error, format of image is not valid : payload.input.mask_image_url`，将mask_url从控件转换为输入即可

- 视频反推：如果提示`Exceeded limit on max bytes per data-uri item : 10485760`，可能因为视频比特率过高
 
- 网络问题：如发生网络错误，可以尝试关闭梯子或者检查代理
 
- 配置错误: 如使用**从配置文件中获取数据**中key显示为`[ERROR] Load config`，请检查config.json中文件格式，如标点符号需使用英文




## 🔖 列表
- 多模态AI助手
- 通用AI助手
- AI图片理解
- `测试版`AI视频理解
- AI图片处理
- Flux助手
- 比较分流器
- 选择输出器
- 宽高比
- 文件计数器
- 从配置文件获取API
- （可选）图片转URL(oss)




## ✨ 功能
_(修改于v1.1.1)_

- **列表**
  
  <img src="IMG/list.png" width="800" alt="自定义宽度" />


- **多模态AI助手**

  支持输入` -文本 -图片 -音频 -视频路径`
  
  支持输出` -文本 -音频`

  <img src="IMG/1.png" width="800" alt="自定义宽度" />


- **通用AI助手**

  支持使用openai的大多数模型，**注意**不同模型的temperature值的上限不同，具体参考使用模型的`技术文档`
  
  <img src="IMG/2.png" width="800" alt="自定义宽度" />


- **AI图片理解**
  
  <img src="IMG/3.png" width="800" alt="自定义宽度" />


- **Flux助手**

  不使用自身电脑性能的情况下使用阿里百炼进行flux文生图。缺点：只能使用预设尺寸
  
  <img src="IMG/4.png" width="800" alt="自定义宽度" />


- **比较分流器**

  通过判断来改变输出方向
  
  <img src="IMG/5.png" width="800" alt="自定义宽度" />

  --------------------------------------**if true**-------------------------------**if false**---------------------------------------

  <img src="IMG/5.1.png" width="390" alt="自定义宽度" /><img src="IMG/5.2.png" width="390" alt="自定义宽度" />


- **选择输出器**

  通过判断来选择输出结果
  
  <img src="IMG/6.png" width="800" alt="自定义宽度" />


- **文件计数器**

  适用于easyuse插件for循环的索引
  
  <img src="IMG/7.png" width="800" alt="自定义宽度" />
  <img src="IMG/7.1.png" width="800" alt="自定义宽度" />


- **从配置文件获取数据**

  从config.json文件中获取数据(适用于方法2)

  使用文本文档打开
     `路径：./custom_nodes/ComfyUI-My-Nodes/config.json`

     ```json

     {
	"api_key": "YourApiKey",
	"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
	"OSS_ACCESS_KEY": "Your AccessKey ID",
	"OSS_SECRET_KEY": "Your AccessKey Secret",
     "bucket": "Your Bucket Name",
	"Key": "Value"



     }
     ```
  可以将自己需要快速获取的值按照以上示例填入，注意标点符号为英文，不要忘记可能丢失的`","`

  保存后重启comfyui生效
