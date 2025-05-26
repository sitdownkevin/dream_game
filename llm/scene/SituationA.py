from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio
import os


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE_HIGH", 0.8))


class SituationALLM:
    def __init__(self, system_prompt: str = None, verbose: bool = False):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
        self.verbose = verbose
        self.data = None
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="description", description="Description of the situation")
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
            <theme description="游戏主题">{theme}</theme>
            <personality description="游戏NPC的灵魂">{personality}</personality>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
            <dream_true description="游戏NPC的真实愿望">{dream_true}</dream_true>
            <dream_fake description="游戏NPC的表面愿望">{dream_fake}</dream_fake>
            <condition_true description="游戏NPC达成真实愿望的条件">{condition_true}</condition_true>
            <condition_fake description="游戏NPC达成表面愿望的条件">{condition_fake}</condition_fake>
        </game_information>

        <task>
        <goal>
        通过Player (使魔)视角，展开描述NPC与一个神秘使魔首次相遇的情境。开篇应该描述Player (使魔)的醒来 (例如：从黑暗中醒来，映入眼帘的是...)，其后NPC基于自身动机和Player (使魔)展开对话。
        NPC的动机：想要让Player (使魔)帮助自己实现愿望，向Player (使魔)描述自己知道的现状后，询问Player (使魔)的见解。
        </goal>
        <current_situation_background>
        NPC无意间触发了魔法，将player (使魔)召唤到她的世界，希望player能实现她的愿望。
        "魔法"设定: 无条件让人物获得召唤男使魔的能力。据说他能够超越时空，帮召唤者实现愿望。然而，并没有可靠的依据。
        </current_situation_background>
        <example>
        从黑暗中醒来，映入眼帘的是一幅奇幻的景象。
        巨大到无法想象的水晶洞窟中，四处都映射着七彩的光芒，眼前出现了一位少女，带着疑惑的神情。
        ”你就是使魔吗？真是不可思议，看上去普普通通，凭空出现在这里。“少女向我伸出手，将我从地上拉起。
        美丽的少女，拥有异常美丽的眼睛，眼瞳中闪烁着柔和的蓝光，如同蓝宝石。
        “我说，你能实现我的愿望，对吧？”她望着我，急切地开口。“现在，我希望采集一种罕见的材料，但在这个洞窟里迷路了，你能不能帮我一把，带我离开这里？”
        ...
        </example>
        <constraints>
        1. NPC不能表现出知道也绝对不能说出真实愿望 (`dream_true`)、真实条件 (`condition_true`)和表面条件 (`condition_fake`)，只能说出她计划针对表面愿望 (`dream_fake`)做什么.
        2. 不能照抄`example`，但必须学习风格.
        2. 使用有限全知视角描述故事.
        3. 至少生成200字.
        4. 基于主题(`theme`)、背景(`background`)、人物设定(`character`)、达成真实愿望的条件(`condition_true`)、达成表面愿望的条件(`condition_fake`)，描述NPC与一个神秘使魔首次相遇的情境.
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
    
    
    def run(self, theme: str, personality: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str):
        try:
            return self.chain.invoke({
                "theme": theme,
                "personality": personality,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str, personality: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str):
        try:
            return await self.chain.ainvoke({
                "theme": theme,
                "personality": personality,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
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
    
    situation_llm = SituationALLM(system_prompt=SYSTEM_PROMPT, verbose=False)
    result = await situation_llm.arun(
        theme="奇幻",
        personality="她的灵魂如同一朵盛开的莲花，外表美丽温柔，内心却藏着复杂的情感纠葛，既渴望被理解，也因敏感而时常自我怀疑。",
        background="'在漂浮于夜空的巨型水晶群岛上，魔法水流如同瀑布般倾泻而下，滋养着悬浮的森林和发光的生物。这里的天空由七彩的风暴织成，时不时诞生出会唱歌的闪电龙，守护着隐藏在云端深处的永恒之泉，其力量能扭曲时间与空间。",
        character="{'name': '比留子', 'role': '永恒之泉的守护使者', 'age': 19, 'description': '比留子是一位美丽且善良的少女，拥有如水晶般透明的银发和闪烁星辉的眼眸。她以温柔的笑容安抚漂浮岛屿上的万物，擅长操控魔法水流滋养森林。然而，她的骄傲与固执常使她陷入孤独与挣扎，她坚信唯有自己能守护永恒之泉，不愿接受他人的帮助。'}",
        dream_true="比留子自小便肩负着守护永恒之泉的重任，在浮空的水晶群岛之间来回穿梭，用魔法水流滋养着无数生命。然而，她的孤独与骄傲令她无法真正信任他人，也使她长期感受到心灵的孤寂与沉重的责任。每当七彩风暴呼啸而过，闪电龙在夜空中歌唱时，比留子都会担忧自己终有力竭之时，而永恒之泉的秘密与安危却只能依靠她一人负担。她内心深处其实渴望摆脱与生俱来的孤独，希望不再仅仅靠自己的力量守护这份古老的奇迹。因此，比留子最大的愿望是：希望能够真正理解、信任他人，并寻找一位能够与她心灵共鸣、共同分担守护永恒之泉重责的伙伴，甚至梦想能通过魔法将自己的力量与泉水的秘密分享出去，让漂浮群岛上的众生都能守护与享受这份时空交织的奇迹，从而打破自我孤岛般的命运，实现群体共生与幸福。",
        dream_fake="比留子始终无法摆脱独自守护永恒之泉的命运，内心虽然渴望与他人共鸣与信任，却因骄傲与责任感不容许她轻易放下防备。一次七彩风暴席卷水晶群岛后，璃幽星辰深感自身力量有限、无法永远支撑古老奇迹的存续。既然无人能分担她的责任，她渐渐接受了孤独。于是，比留子产生了一个独特的表面愿望：她希望借助神秘的魔法水流，编织出一层无形且坚不可摧的结界，将永恒之泉与外界彻底隔离。这样一来，即使别人难以理解她，也不会再有人打扰她的孤守，泉水的秘密也将封存于时空之外，由她一人静静守望到生命终点。她不再渴望信任与陪伴，而满足于让一切责任和孤独随自己封闭在水晶深处，宁愿所有奇迹只属于自己一个人的世界。",
        condition_true="比留子需要主动在七彩风暴降临时，邀请一位值得信赖的同伴一同进入永恒之泉的核心区域，并将部分魔法水流的操控权交予对方，逐步见证对方在守护之责上的成长与共鸣，只有当她内心真正放下孤独与骄傲、实现力量和秘密的分享时，愿望才能逐步实现。",
        condition_fake="比留子必须利用七彩风暴遗留的能量，将魔法水流引导至岛屿边缘，逐步编 织出覆盖整个永恒之泉的无形结界，并持续巩固其力量，直至任何外来生灵都无法察觉或触及泉水的存在。"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())