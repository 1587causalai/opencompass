# Brainstorm & Git Commits   


本篇文档用于记录学习过程头脑风暴, 以及 git 操作记录. 方便后续回顾.


## 2023-12-07

### 1. 添加配置系统文档
```bash
git add docs/zh_cn/learning_notes/config_system.md
git commit -m "docs: add comprehensive guide for OpenCompass config system"
```
- 添加了配置系统详解文档
- 修复了 --num-gpus 参数问题

### 2. 添加开发日志
```bash
git add docs/zh_cn/index.rst docs/zh_cn/learning_notes/development_log.md
git commit -m "docs: add development log to track git operations"
```
- 创建开发日志文档
- 将开发日志加入到文档索引

### 3. API 调用 vpn 问题

我需要云端的机器访问本地的vpn when call for openai api model, 


### 4. 下一步搞什么鬼呢？

下一步搞什么鬼呢？我想一下啊。api 模型的评测, 多模态模型的评测?

我需要云端的机器访问本地的vpn when call for openai api model, 

我连接云端服务器的命令是这个:
ssh -p 44773 root@ssh.intern-ai.org.cn -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

然后运行脚本 @eval_api_demo.py ,  请注意，并不是云端的所有的流量都用本地的vpn访问，只是运行这一个脚本的时候，临时性的使用本地的vpn。