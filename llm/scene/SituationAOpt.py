from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
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
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information description="游戏信息">
            <soul description="游戏NPC的灵魂">{soul}</soul>
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
        在NPC与Player (使魔)相遇的情境中，生成Player (使魔)的第一人称行动选项。
        1. CHOICE_A: 这个选项有些荒诞滑稽可笑，但能提高表面条件，有助于NPC表面愿望的满足，但对真实愿望有潜在的微妙损害。
        2. CHOICE_B: 这个选项有些荒诞滑稽可笑，但能真实条件的满足，有助于实现NPC的真实愿望。
        3. CHOICE_C: 它应该荒诞滑稽可笑的事件发展，不能明确地推动任何一个条件的实现。
        </task>

        <constraints>
        1. 不能照抄`condition_true`与`condition_fake`，但必须遵循.
        1. 使用有限全知视角描述故事.
        2. 基于灵魂(`soul`)、主题(`theme`)、背景(`background`)、人物设定(`character`)、达成真实愿望的条件(`condition_true`)、达成表面愿望的条件(`condition_fake`)，生成使魔的对话选项。
        3. 基于当前情境(`current_situation_description`)，生成使魔的对话选项。
        4. 使魔的对话选项CHOICE_A和CHOICE_B应该以微妙但明确的方式推动NPC走向他们的愿望或条件的满足。
        5. Use Chinese to answer.
        6. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["soul", "theme", "background", "character", "dream_true", "dream_fake", "condition_true", "condition_fake", "current_situation_description"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )


    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, soul: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return self.chain.invoke({
                "soul": soul,
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
        
    
    async def arun(self, soul: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return await self.chain.ainvoke({
                "soul": soul,
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
    situation_aopt_llm = SituationAOptLLM()
    result = await situation_aopt_llm.arun(
        theme="奇幻",
        soul="她的灵魂如同一朵盛开的莲花，外表美丽温柔，内心却藏着复杂的情感纠葛，既渴望被理解，也因敏感而时常自我怀疑。",
        background="'在漂浮于夜空的巨型水晶群岛上，魔法水流如同瀑布般倾泻而下，滋养着悬浮的森林和发光的生物。这里的天空由七彩的风暴织成，时不时诞生出会唱歌的闪电龙，守护着隐藏在云端深处的永恒之泉，其力量能扭曲时间与空间。",
        character="{'name': '璃幽星辰', 'role': '永恒之泉的守护使者', 'age': 19, 'description': '璃幽星辰是一位美丽且善良的少女，拥有如水晶般透明的银发和闪烁星辉的眼眸。她以温柔的笑容安抚漂浮岛屿上的万物，擅长操控魔法水流滋养森林。然而，她的骄傲与固执常使她陷入孤独与挣扎，她坚信唯有自己能守护永恒之泉，不愿接受他人的帮助。'}",
        dream_true="璃幽星辰自小便肩负着守护永恒之泉的重任，在浮空的水晶群岛之间来回穿梭，用魔法水流滋养着无数生命。然而，她的孤独与骄傲令她无法真正信任他人，也使她长期感受到心灵的孤寂与沉重的责任。每当七彩风暴呼啸而过，闪电龙在夜空中歌唱时，璃幽星辰都会担忧自己终有力竭之时，而永恒之泉的秘密与安危却只能依靠她一人负担。她内心深处其实渴望摆脱与生俱来的孤独，希望不再仅仅靠自己的力量守护这份古老的奇迹。因此，璃幽星辰最大的愿望是：希望能够真正理解、信任他人，并寻找一位能够与她心灵共鸣、共同分担守护永恒之泉重责的伙伴，甚至梦想能通过魔法将自己的力量与泉水的秘密分享出去，让漂浮群岛上的众生都能守护与享受这份时空交织的奇迹，从而打破自我孤岛般的命运，实现群体共生与幸福。",
        dream_fake="璃幽星辰始终无法摆脱独自守护永恒之泉的命运，内心虽然渴望与他人共鸣与信任，却因骄傲与责任感不容许她轻易放下防备。一次七彩风暴席卷水晶群岛后，璃幽星辰深感自身力量有限、无法永远支撑古老奇迹的存续。既然无人能分担她的责任，她渐渐接受了孤独。于是，璃幽星辰产生了一个独特的表面愿望：她希望借助神秘的魔法水流，编织出一层无形且坚不可摧的结界，将永恒之泉与外界彻底隔离。这样一来，即使别人难以理解她，也不会再有人打扰她的孤守，泉水的秘密也将封存于时空之外，由她一人静静守望到生命终点。她不再渴望信任与陪伴，而满足于让一切责任和孤独随自己封闭在水晶深处，宁愿所有奇迹只属于自己一个人的世界。",
        condition_true="璃幽星辰需要主动在七彩风暴降临时，邀请一位值得信赖的同伴一同进入永恒之泉的核心区域，并将部分魔法水流的操控权交予对方，逐步见证对方在守护之责上的成长与共鸣，只有当她内心真正放下孤独与骄傲、实现力量和秘密的分享时，愿望才能逐步实现。",
        condition_fake="璃幽星辰必须利用七彩风暴遗留的能量，将魔法水流引导至岛屿边缘，逐步编 织出覆盖整个永恒之泉的无形结界，并持续巩固其力量，直至任何外来生灵都无法察觉或触及泉水的存在。",
        current_situation_description="从无尽的黑暗中缓缓苏醒，眼前逐渐浮现出一片奇异的光影。那是漂浮于夜空的巨型水晶群岛，晶莹剔透的水晶反射着七彩风暴的光辉，魔法水流如瀑布般倾泻而下，滋养着悬浮的森林和发光的生物。空气中弥漫着淡淡的水汽与魔法的气息，远处隐约传来闪电龙悠扬的歌声。就在这片梦幻般的景 象中，一位少女缓缓走近，她拥有银白如水晶般透明的长发，眼眸中闪烁着星辉，脸上带着温柔却略显忧虑的笑容。她轻声唤道：“你终于醒了……我叫璃幽星辰，是这永恒之泉的守护使者。”\n\n璃幽星辰的声音柔和却带着一丝坚定，她缓缓讲述着自己肩负的重任：守护隐藏在云端深处的永恒之泉，用魔法水流滋养着这片漂浮群岛上的生命。然而，七彩风暴的力量日益强大，孤独的守护让她感到力不从心。她坦言自己一直独自承担着这份责任，不愿轻易信任他人，但如今 她必须做出改变。她计划在下一次七彩风暴来临时，邀请一位值得信赖的伙伴进入永恒之泉的核心，将部分魔法水流的操控权交予对方，逐步实现力量的分享 与共鸣。\n\n她的目光深邃，似乎在探寻着我的反应：“你作为使魔，拥有超越时空的力量，我想知道，你怎么看待我这份计划？你愿意帮助我吗？”璃幽星辰 的声音中带着一丝渴望与试探，仿佛在寻找一个能够理解她孤独与责任的人。她没有直接诉说自己的真实愿望，而是将希望寄托在这段合作与信任的可能性上 。\n\n在这片由魔法与奇迹交织的水晶群岛上，璃幽星辰与我第一次相遇。她的骄傲与温柔交织成复杂的情感，等待着我这个神秘使魔的回应，也许这将是她 打破孤独、迎来共生未来的开始。"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())