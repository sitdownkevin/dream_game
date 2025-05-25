from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio
import os


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME_SOTA", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = 1.0


class DreamLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt_true = self.get_prompt_true()
        self.prompt_fake = self.get_prompt_fake()
        self.chain_true = self.get_chain_true()
        self.chain_fake = self.get_chain_fake()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="dream", description="Paragraph that describes the dream of the NPC")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt_true(self):
        messages = []
        
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <task>
        <goal>
        基于游戏信息(`game_information`)，为NPC生成一个想要实现的“真实愿望”.
        </goal>
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
        </game_information>
        <constraints>
        1. 使用第三人称.
        2. 至少生成200字.
        3. 尽可能发挥想象力.
        </constraints>
        <workflow>
        按照以下步骤为NPC设计一个"真实愿望":
        1. 结合输入的主题(`theme`)、背景(`background`)和人物设定(`character`)，为人物设想一个困境，这个困境是深沉和重大的，影响NPC非常看重的东西.
        2. 从困境的角度出发，思考一个人物渴望实现的愿望. 采用逆向思维，思考NPC为了解决难题想怎么做. 比如说，NPC可能想改变某个通常无法改变的元素，或者从不寻常的因果关系入手解决问题. 实现它非常困难，但能彻底摆脱困境.
        3. 从人物的视角出发，用一句话描述这个愿望，输出.
        </workflow>
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
            format_instructions=self.output_parser.get_format_instructions()
        )
    
    
    def get_prompt_fake(self):
        messages = []
        
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <task>
        <goal>
        基于游戏信息(`game_information`)，为NPC生成一个想要实现的“表面愿望”。
        </goal>
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
            <dream_true description="游戏NPC的真实愿望">{dream_true}</dream_true>
        </game_information>
        <workflow>
        按照以下步骤为NPC设计一个"表面愿望":
        1. 结合输入的主题(`theme`)、背景(`background`)和人物设定(`character`)和真实愿望(`dream`)，思考NPC无法实现真实愿望时，会引发什么难题。
        2. 采用逆向思维，思考NPC为了解决难题想采用什么独特的行动。比如说，NPC可能想改变某个通常无法改变的元素，或者从不寻常的因果关系入手解决问题。
        3. 考虑约束条件：独特行动必须无法实现人物的真实愿望。
        4. 从人物的视角出发，将人物想要采取的独特行动用一句话描述为人物的愿望，输出。
        </workflow>
        <other_information>
        表面愿望的定义是：NPC认为真实愿望难以实现时，妥协后希望实现的愿望，比真实愿望更容易实现，但偏离了真实愿望，显得自暴自弃。
        例如：真实愿望是”想要让全人类幸福...“，但难以实现，妥协后的表面愿望是：”制造让全人类永远产生幸福幻觉的成瘾药物...“
        </other_information>
        <constraints>
        1. 使用第三人称.
        2. 至少生成200字.
        3. 尽可能发挥想象力.
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
            format_instructions=self.output_parser.get_format_instructions()
        )
    
    
    def get_chain_true(self):
        return self.prompt_true | self.llm | self.output_parser
    
    
    def get_chain_fake(self):
        return self.prompt_fake | self.llm | self.output_parser
    
    
    def run(self, type: str = 'TRUE', theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream_true: str = '想要实现一个能够改变世界的愿望'):
        assert type in ['TRUE', 'FAKE']
        
        try:
            if type == 'TRUE':
                return self.chain_true.invoke({"theme": theme, "background": background, "character": character})
            elif type == 'FAKE':
                return self.chain_fake.invoke({"theme": theme, "background": background, "character": character, "dream_true": dream_true})
            else:
                raise ValueError(f"Invalid type: {type}")
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, type: str = 'TRUE', theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream_true: str = '想要实现一个能够改变世界的愿望'):
        assert type in ['TRUE', 'FAKE']
        
        try:
            if type == 'TRUE':
                return await self.chain_true.ainvoke({"theme": theme, "background": background, "character": character})
            elif type == 'FAKE':
                return await self.chain_fake.ainvoke({"theme": theme, "background": background, "character": character, "dream_true": dream_true})
            else:
                raise ValueError(f"Invalid type: {type}")
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
    
    dream_llm = DreamLLM(system_prompt=SYSTEM_PROMPT)
    result_true = await dream_llm.arun(type='TRUE')
    result_fake = await dream_llm.arun(type='FAKE', dream_true=result_true)
    print('真实愿望:')
    print(result_true)
    print('表面愿望:')
    print(result_fake)


if __name__ == "__main__":
    asyncio.run(main())