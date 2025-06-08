# 📖 Help and Commands

欢迎来到帮助页面。这里将介绍该机器人如何工作以及支持的各项指令。
原作者：https://github.com/olted/aedilebot/tree/main
---

## 🆘 `/foxholehelp`
显示此帮助信息！是不是很方便？

---

## 📊 `/info [entity]`
提供指定物品的统计数据表，例如武器、载具、建筑等。

---

## 💥 `/kill [target] [weapon]`
/custom_kill target: str, weapon1: str, num1: int, weapon2: str):
计算使用指定数量的两种武器组合攻击目标的效果
用于计算使用某种武器摧毁指定目标所需的次数。
其功能等同于下方的自然语言提示方式。

---

## 🔍 Damage Calculator Prompt（自然语言提示）
你也可以直接在频道中输入以下类型的语句，机器人会自动识别并进行计算：

---

## ✨ 示例（可以直接复制到频道试用）：

- `How much 150mm to kill Patridia?`  
- `How many satchels to kill t3 bunker core husk?`  
- `How many 68mm to disable HTD?`  
- `How many satchels to kill Victa?`  
- `How much 40mm to destroy bt pad?`

---

处理流程说明：
当用户发送类似"？how many 150mm to dehusk HTD"的消息时，正则表达式会匹配并触发handle_dehusk函数。
在handle_dehusk函数中：
从正则匹配结果中提取武器（weapon）和目标（target）信息
调用handle_response_inner函数，并指定operation为"dehusk"
handle_response_inner函数会：
根据operation="dehusk"参数，调用calculator.general_dehusk_handler
处理可能出现的各种异常情况，如：
零除错误（武器对目标无伤害）
目标未找到
无效类型
武器未找到
其他未知错误
最终结果会：
如果成功，返回计算结果
如果失败，返回相应的错误信息
使用event.plain_result()将结果发送给用户

🛠️ 无论是用于战术计划还是单纯的好奇，这些功能都能帮助你更好地了解 Foxhole 的战斗机制。
