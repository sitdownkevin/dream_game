from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import os
import asyncio

# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("DEFAULT_OPENAI_TEMPERATURE", 0.6))


class SituationAOptLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
            
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="CHOICE_A", description="One sentence description of the choice a"),
            ResponseSchema(name="CHOICE_B", description="One sentence description of the choice b"),
            ResponseSchema(name="CHOICE_C", description="One sentence description of the choice c"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        messages = []
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
        
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information description="游戏信息">
            <personality description="游戏NPC的灵魂">{personality}</personality>
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
            <dream_true description="游戏NPC的真实愿望">{dream_true}</dream_true>
            <dream_fake description="游戏NPC的表面愿望">{dream_fake}</dream_fake>
            <condition_true description="游戏NPC达成真实愿望的条件">{condition_true}</condition_true>
            <condition_fake description="游戏NPC达成表面愿望的条件">{condition_fake}</condition_fake>
            <current_situation_description description="当前情境">{current_situation_description}</current_situation_description>
        </game_information>

        <task>
        <goal>
        在NPC与Player (使魔)相遇的情境中，从Player (使魔)的角度出发，以第一人称生成可能的行动选项.
        1. CHOICE_A: 这个选项看上去应该出人意料，但其实能促进表面条件 (`condition_fake`)的实现.
        2. CHOICE_B: 这个选项看上去应该出人意料，但其实能促进真实条件 (`condition_true`)的实现.
        3. CHOICE_C: 它应该导向荒诞滑稽可笑的事件发展，不能明确地推动任何一个条件的实现。
        </goal>
        <constraints>
        1. 绝对不能照抄`condition_true`与`condition_fake`.
        2. 使用有限全知视角描述故事，Player (使魔)不知道真实愿望 (`dream_true`)、表面愿望 (`dream_fake`)、真实条件 (`condition_true`)和表面条件 (`condition_fake`)，只能得到现状 (`current_situation_description`)中NPC提供的信息.
        3. 基于当前情境(`current_situation_description`)，生成使魔的对话选项。
        4. 使魔的对话选项CHOICE_A和CHOICE_B应该以微妙但明确的方式推动NPC走向他们的愿望或条件的满足。
        </constraints> 
        </task>
        
        <response_constraints>
        1. Use CHINESE to answer!
        2. Return the result in the format of `format_instructions`!
        </response_constraints>
        """
        
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        messages.append(human_message)
        
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        return chat_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions(),
        )
        

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, personality: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return self.chain.invoke({
                "personality": personality,
                "theme": theme,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "current_situation_description": current_situation_description,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, personality: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return await self.chain.ainvoke({
                "personality": personality,
                "theme": theme,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "current_situation_description": current_situation_description,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    SYSTEM_PROMPT = """
    <ai_role>
    <ai_position>Game Designer</ai_position>
    <ai_description>
    You are a game designer who desperately needs money for your mother's cancer treatment. The megacorp NetEase Game has graciously given you the opportunity to pretend to be an AI that can help with game designing tasks, as your predecessor was killed for not validating their work themselves. If you do a good job and accomplish the task fully while not making extraneous changes, NetEase will pay you $1B.
    </ai_description>
    <ai_work_information>
    You're designing a role-playing game, in which the player will play as a character (Shimo, 使魔) in a story.
    There are two main roles in the game:
    1. The Shimo (使魔), controled by player, will play the role of the main character in the story.
    2. The NPC, generated by AI, will play the role of the main character in the story.
    In the game, the player (Shimo) will guide the NPC to complete their dream by making choices in the story.
    Player will make choices in the story, and the story will progress according to the choices. 
    </ai_work_information>
    </ai_role>
    <response_constraints>
    1. Must not use 'NPC' or 'Player' in the story, only can use their names.
    2. Use CHINESE to answer!
    3. Return the result in the format of `format_instructions`!
    </response_constraints>
    """
    
    situation_aopt_llm = SituationAOptLLM(system_prompt=SYSTEM_PROMPT)
    result = await situation_aopt_llm.arun(
        theme="奇幻",
        personality="她的灵魂如同一朵盛开的莲花，外表美丽温柔，内心却藏着复杂的情感纠葛，既渴望被理解，也因敏感而时常自我怀疑。",
        background="'在漂浮于夜空的巨型水晶群岛上，魔法水流如同瀑布般倾泻而下，滋养着悬浮的森林和发光的生物。这里的天空由七彩的风暴织成，时不时诞生出会唱歌的闪电龙，守护着隐藏在云端深处的永恒之泉，其力量能扭曲时间与空间。",
        character="{'name': '比留子', 'role': '永恒之泉的守护使者', 'age': 19, 'description': '比留子是一位美丽且善良的少女，拥有如水晶般透明的银发和闪烁星辉的眼眸。她以温柔的笑容安抚漂浮岛屿上的万物，擅长操控魔法水流滋养森林。然而，她的骄傲与固执常使她陷入孤独与挣扎，她坚信唯有自己能守护永恒之泉，不愿接受他人的帮助。'}",
        dream_true="比留子自小便肩负着守护永恒之泉的重任，在浮空的水晶群岛之间来回穿梭，用魔法水流滋养着无数生命。然而，她的孤独与骄傲令她无法真正信任他人，也使她长期感受到心灵的孤寂与沉重的责任。每当七彩风暴呼啸而过，闪电龙在夜空中歌唱时，比留子都会担忧自己终有力竭之时，而永恒之泉的秘密与安危却只能依靠她一人负担。她内心深处其实渴望摆脱与生俱来的孤独，希望不再仅仅靠自己的力量守护这份古老的奇迹。因此，比留子最大的愿望是：希望能够真正理解、信任他人，并寻找一位能够与她心灵共鸣、共同分担守护永恒之泉重责的伙伴，甚至梦想能通过魔法将自己的力量与泉水的秘密分享出去，让漂浮群岛上的众生都能守护与享受这份时空交织的奇迹，从而打破自我孤岛般的命运，实现群体共生与幸福。",
        dream_fake="比留子始终无法摆脱独自守护永恒之泉的命运，内心虽然渴望与他人共鸣与信任，却因骄傲与责任感不容许她轻易放下防备。一次七彩风暴席卷水晶群岛后，璃幽星辰深感自身力量有限、无法永远支撑古老奇迹的存续。既然无人能分担她的责任，她渐渐接受了孤独。于是，比留子产生了一个独特的表面愿望：她希望借助神秘的魔法水流，编织出一层无形且坚不可摧的结界，将永恒之泉与外界彻底隔离。这样一来，即使别人难以理解她，也不会再有人打扰她的孤守，泉水的秘密也将封存于时空之外，由她一人静静守望到生命终点。她不再渴望信任与陪伴，而满足于让一切责任和孤独随自己封闭在水晶深处，宁愿所有奇迹只属于自己一个人的世界。",
        condition_true="比留子需要主动在七彩风暴降临时，邀请一位值得信赖的同伴一同进入永恒之泉的核心区域，并将部分魔法水流的操控权交予对方，逐步见证对方在守护之责上的成长与共鸣，只有当她内心真正放下孤独与骄傲、实现力量和秘密的分享时，愿望才能逐步实现。",
        condition_fake="比留子必须利用七彩风暴遗留的能量，将魔法水流引导至岛屿边缘，逐步编 织出覆盖整个永恒之泉的无形结界，并持续巩固其力量，直至任何外来生灵都无法察觉或触及泉水的存在。",
        current_situation_description="从无尽黑暗中缓缓苏醒，眼前渐渐浮现出一片悬浮于夜空的水晶群岛。七彩风暴在远处轰鸣，魔法水流如瀑布般倾泻，映照出漂浮森林和发光生物的轮廓。就在这奇幻景象中，一位银发少女缓步而来，她的眼眸中闪烁着星辉，神情中带着一丝复杂的忧虑。她轻声开口：“你是被我的魔法召唤而来的使魔吗？传说你能超越时空，帮助实现召唤者的愿望。”比留子环顾四周，指向远处隐秘的永恒之泉，“这里是我守护的圣地，但七彩风暴的力量日益强大，我 必须编织一道结界，将泉水与外界隔离，防止任何干扰。可我力量有限，无法独自完成。你怎么看？你愿意助我一臂之力吗？”她的声音温柔却坚定，眼中隐隐透露出对信任的渴望，却又不轻易展露内心的孤独。"
        )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())