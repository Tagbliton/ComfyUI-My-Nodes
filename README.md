# My-Nodes

AI助手
(正在测试...)


## 📑 API获取方法
- 阿里百炼大模型-技术文档

  `https://help.aliyun.com/zh/model-studio/getting-started/what-is-model-studio`

- 如何获取API

  `https://help.aliyun.com/zh/model-studio/user-guide/first-api-call-to-qwen`

- 获取的API可以填写到插件根目录下的配置文件中以通过节点调取（可选）

  `../custom_nodes/ComfyUI-My-Nodes/config.txt`

  `api_key=YourApiKey`

  将 '=' 后替换为你的api_key



- 默认base_url

  `https://dashscope.aliyuncs.com/compatible-mode/v1`



## 📑 列表
- 多模态AI助手
- 通用AI助手
- AI图片理解
- Flux助手
- 比较分流器
- 选择输出器
- 宽高比
- 文件计数器
- 从配置文件获取API




## ✨ 功能
- 列表
<img src="IMG/list.png" width="800" alt="自定义宽度" />

- 多模态AI助手

  支持输入 -文本 -图片 -音频 -视频路径
  
  支持输出 -文本 -音频
<img src="IMG/1.png" width="800" alt="自定义宽度" />

- 通用AI助手

  支持使用openai的大多数模型，需要注意不同模型的temperature值的上限不同，具体参考使用模型的技术文档
<img src="IMG/2.png" width="800" alt="自定义宽度" />

- AI图片理解
<img src="IMG/3.png" width="800" alt="自定义宽度" />

- Flux助手

  不使用自身电脑性能的情况下使用阿里百炼进行flux文生图。缺点：只能使用预设尺寸
<img src="IMG/4.png" width="800" alt="自定义宽度" />

- 比较分流器

  通过判断来改变输出方向
<img src="IMG/5.png" width="800" alt="自定义宽度" />
if true
if false
<img src="IMG/5.1.png" width="400" alt="自定义宽度" /><img src="IMG/5.2.png" width="400" alt="自定义宽度" />

- 选择输出器

  通过判断来选择输出结果
<img src="IMG/6.png" width="800" alt="自定义宽度" />


- 文件计数器

  适用于easyuse插件for循环的索引
<img src="IMG/7.png" width="800" alt="自定义宽度" />
<img src="IMG/7.1.png" width="800" alt="自定义宽度" />

- 从配置文件获取API
  
  目前更改配置文件后需重启comfyui才能获取最新配置




