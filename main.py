from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from typing import Dict, List
from astrbot.api import logger
from astrbot.core import AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
import traceback
from . import calculator
import re

class EntityNotFoundError(Exception):
    def __init__(self,name, message="找不到你请求的实体，请重新尝试。"):
        self.name = name
        self.message = message
        super().__init__(self.message)
    def show_message(self):
        return self.message
    
class InvalidTypeError(EntityNotFoundError):
    def __init__(self, name, message="该实体类型无效，请重试。"):
        super().__init__(name,message)

class TargetNotFoundError(EntityNotFoundError):
    def __init__(self, name, message=f"在数据集中未找到指定目标，请重试。"):
        super().__init__(name,message)

class TargetOfTypeNotFoundError(EntityNotFoundError):
    def __init__(self, name, message=f"在数据集中未找到此操作的目标类型，请重试。"):
        super().__init__(name,message)

class WeaponNotFoundError(EntityNotFoundError):
    def __init__(self,name, message=f"在数据集中未找到指定武器，请重试。"):
        super().__init__(name,message)

class LocationNotFoundError(EntityNotFoundError):
    def __init__(self,name,message="无法找到指定的城镇/遗迹位置，请重试。"):
        super().__init__(name,message)

class BunkerSpecParseError(TargetNotFoundError):
    def __init__(self,name,message="地堡规格无效，请按以下格式重试：\n`how many <武器> to kill size <数字> tier <1/2/3> bunker with <数量> <改装> ...`\n例如：`How many tremola to kill a size 15 t3 bunker with 2 mg 3 atg 3 howi 1 ramp`"):
        super().__init__(name,message)

@register("foxhole", "FoxholeBot", "Foxhole 游戏数据查询插件", "1.0.0")
class FoxholePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        self.config = config
        self.foxhole_group: List[str] = config.get(
            "foxhole_group", []
        )  # 启用此插件的群聊
        


    def handle_response_inner(self, weapon=None, target=None, operation="kill", num1=0, weapon2=None):
        try:
            if operation=="kill":
                return calculator.general_kill_handler(weapon, target)
            if operation=="disable":
                return calculator.general_disable_handler(weapon,target)
            if operation =="dehusk":
                return calculator.general_dehusk_handler(weapon, target)
            if operation =="bunker":
                return calculator.general_bunker_kill_handler(weapon, target)
            if operation =="custom_kill":
                return calculator.custom_kill_handler(weapon, num1, weapon2, target)
        except ZeroDivisionError as e:
            logger.error(f"[FoxholeBot] 零除错误: {str(e)}")
            return f"该武器对目标没有伤害"
        except TargetNotFoundError as e:
            logger.error(f"[FoxholeBot] 目标未找到: {str(e)}")
            return e.show_message()
        except InvalidTypeError as e:
            logger.error(f"[FoxholeBot] 无效类型: {str(e)}")
            return e.show_message()
        except WeaponNotFoundError as e:
            logger.error(f"[FoxholeBot] 武器未找到: {str(e)}")
            return e.show_message()
        except EntityNotFoundError as e:
            logger.error(f"[FoxholeBot] 实体未找到: {str(e)}")
            return e.show_message()
        except Exception as e:
            error_msg = f"[FoxholeBot] 未知错误: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(e)
            traceback.print_tb(e.__traceback__)
            return ("在处理你的请求时发生了内部错误。请联系机器人的开发者。")

    @filter.command("foxholehelp")
    async def help(self, event: AiocqhttpMessageEvent):
        group_id = event.get_group_id()
        
        print("group_id:",group_id)
        # 如果群聊不在检测列表中，则不进行检测
        if group_id not in self.foxhole_group:
            print("not in group")
            return
        """显示帮助信息"""
        help_text = (
            "欢迎使用 Foxhole 数据计算插件！以下是可用的命令：\n\n"
            "📌 基础命令：\n"
            "- /foxholehelp - 显示此帮助信息\n"
            "- /info [名字] - 查看任何武器/建筑/载具的统计数据表\n"
            "- /kill [目标] [武器] - 计算使用指定武器摧毁目标所需数量\n"
            "- /custom_kill [目标] [武器1] [数量1] [武器2] - 计算使用指定数量的两种武器组合攻击目标的效果\n\n"
            "💡 伤害计算示例：\n"
            "- ^how (many|much)(.*) to (kill|destroy|disable|dehusk)(.*)\n"
            "祝您在前线好运！"
        )
        yield event.plain_result(help_text)

    @filter.command("custom_kill")
    async def custom_kill(self, event: AiocqhttpMessageEvent, target: str, weapon1: str, num1: int, weapon2: str):
        """计算使用指定数量的两种武器组合攻击目标的效果"""
        group_id = event.get_group_id()
        # 如果群聊不在检测列表中，则不进行检测
        if group_id not in self.foxhole_group:
            return
        result = self.handle_response_inner(weapon1, target, "custom_kill", num1, weapon2)
        yield event.plain_result(result)

    @filter.command("info")
    async def statsheet(self, event: AiocqhttpMessageEvent, entity: str):
        """查看任何实体的统计数据表"""
        group_id = event.get_group_id()
        print("group_id：",group_id)
        # 如果群聊不在检测列表中，则不进行检测
        if group_id not in self.foxhole_group:
            print("not in group")
            return
        data = calculator.statsheet_handler(entity)
        result = f"**{data[1]}** 的统计数据表:\n\n"
        
        if data[0] == "Weapons":
            result += f"原始伤害: {data[2]}\n"
            result += f"伤害类型: {data[3]}\n"
        elif data[0] == "Structures":
            result += f"原始生命值: {data[2]}\n"
            result += f"减伤类型: {data[3]}\n"
            result += f"修理消耗: {data[5]}\n"
        elif data[0] in ["Vehicles", "Tripods", "Emplacements"]:
            result += f"原始生命值: {data[2]}\n"
            result += f"减伤类型: {data[3]}\n"
            if data[6] != "0":
                result += f"最大穿透率: {data[5]}%\n"
                result += f"最小穿透率: {data[4]}%\n"
                result += f"装甲生命值: {data[6]}\n"
            if data[7] != "":
                result += f"装填时间: {data[7]}\n"
            if data[8] != "":
                result += f"主武器: {data[8]}\n"
            if data[9] != "":
                result += f"炮塔瘫痪率: {data[9]}%\n"
            if data[10] != "":
                result += f"履带瘫痪率: {data[10]}%\n"
        elif data[0] in ["Multitier_structures"]:
            result += f"原始生命值: {data[2]}\n"
            result += f"基础材料消耗: {data[3]}\n"
            result += f"修理消耗: {data[4]}\n"
            result += f"城镇等级: {data[5]}\n"
        else:
            raise EntityNotFoundError(data[0])
        yield event.plain_result(result)

    """ 
    这是dc的代码自动补全，暂时用不上
    @statsheet.autocomplete("entity")
    async def statsheet_autocompletion(
        interaction:discord.Interaction,
        current:str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        usedlist = []
        if len(current)>1:
            guess = fuzz.fuzzy_match_any_command(current)
            for possible_value in guess:
                if possible_value.lower() != possible_value and len(data)<20:
                    if possible_value not in usedlist:
                        data.append(app_commands.Choice(name=possible_value,value=possible_value))
                        usedlist.append(possible_value)
                elif possible_value.lower() == possible_value and len(data)<20:
                    value = fuzz.fuzzy_match_any(possible_value)["max_value"]
                    if value not in usedlist:
                        data.append(app_commands.Choice(name=value,value=value))
                        usedlist.append(value)
        return data
    """


    @filter.command("kill")
    async def kill(self, event: AiocqhttpMessageEvent,
                    target: str,
                    weapon: str):
        group_id = event.get_group_id()
        # 如果群聊不在检测列表中，则不进行检测
        if group_id not in self.foxhole_group:
            return
        try:
            result = self.handle_response_inner(target=target, weapon=weapon, operation="kill", num1=0, weapon2=None)
            yield event.plain_result(result)
        except Exception as e:
            yield event.plain_result(f"命令执行出错: {str(e)}")


#用@filter.regex构建一个how开头匹配的玩家消息
    @filter.regex(r"^how (many|much)(.*) to (kill|destroy|disable|dehusk)(.*)")
    async def on_message(self, event: AiocqhttpMessageEvent):
        group_id = event.get_group_id()
        if group_id not in self.foxhole_group:
            return
        message = event.message_str
        response = handle_response(message)
        yield event.plain_result(response)






    async def terminate(self):
        """插件终止时的清理工作"""
        pass


def handle_response(message) -> str:
    p_message = message.lower()
    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', move_string_to_rear(p_message) )
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        if "size" in target:
            return handle_response_inner(weapon, target, operation="bunker")
        return handle_response_inner(weapon, target)
    
    token_pair = re.findall('how (many|much)(.*) to disable (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, operation="disable")
    
    token_pair = re.findall('how (many|much)(.*) to dehusk (.*)', move_string_to_rear(p_message))
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, operation="dehusk")
    
    return None

# bot logic
def handle_response_inner(weapon,target, operation="kill", num1=0, weapon2=None):
    try:
        if operation=="kill":
            return calculator.general_kill_handler(weapon, target) #return calculator.relic_th_kill_handler(weapon, target)
        if operation=="disable":
            return calculator.general_disable_handler(weapon,target)
        if operation =="dehusk":
            return calculator.general_dehusk_handler(weapon, target)
        if operation =="bunker":
            return calculator.general_bunker_kill_handler(weapon, target)
        if operation =="custom_kill":
            return calculator.custom_kill_handler(weapon, num1, weapon2, target)
    except ZeroDivisionError as e:
        return f"This weapon does no damage to this entity"
    except TargetNotFoundError as e:
        return e.show_message()
    except InvalidTypeError as e:
        return e.show_message()
    except WeaponNotFoundError as e:
        return e.show_message()
    except EntityNotFoundError as e:
        return e.show_message()
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        return ("Inner error happened during processing of your request. "
                "Please, contact bot's devs about this.")
    
def move_string_to_rear(string):
    tier_dictionary = { "tier 1":"t1","tier 2":"t2","tier 3":"t3","concrete":"t3"}
    for replacement_string in move_to_rear_string_list:
        if replacement_string in string:
            if replacement_string in ["tier 1","tier 2","tier 3","concrete"]:
                new_string = tier_dictionary[replacement_string]
                return string.replace(replacement_string, "") + " " + str(new_string)
            if replacement_string in ["unemplaced","unentrenched"]:
                return string.replace(replacement_string, "")
            if replacement_string in ["emplaced","entrenched"]:
                return string.replace(replacement_string, "") + " " + str("emplaced")
            if replacement_string in ["t1","t2","t3"]:
                return string.replace(replacement_string, "") + " " + str(replacement_string)
    return string
move_to_rear_string_list = [ "t1","t2","t3","unemplaced","unentrenched","emplaced", "entrenched","tier 1", "tier 2","tier 3","concrete"]
# text processing functions
def clean_capitalize(str):
    result = ""
    list_of_words = str.split() 
    for elem in list_of_words:
        if len(result) > 0:
            result = result + " " + elem.strip().capitalize()
        else:
            result = elem.capitalize()
    if not result:
        return str
    else:
        return result