from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
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
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
        </game_information>
        
        <task>
        基于游戏信息(`game_information`)，为NPC生成一个想要实现的“真实愿望”.
        </task>
        
        <workflow>
        按照以下步骤为NPC设计一个"真实愿望":
        1. 结合输入的主题(`theme`)、背景(`background`)和人物设定(`character`)，为人物设想一个困境，这个困境是深沉和重大的，影响NPC非常看重的东西.
        2. 从困境的角度出发，思考一个人物渴望实现的愿望. 采用逆向思维，思考NPC为了解决难题想怎么做. 比如说，NPC可能想改变某个通常无法改变的元素，或者从不寻常的因果关系入手解决问题. 实现它非常困难，但能彻底摆脱困境.
        3. 从人物的视角出发，用一句话描述这个愿望，输出.
        </workflow>

        <constraints>
        1. 使用第三人称.
        2. 至少生成200字.
        3. Use Chinese to answer.
        4. 尽可能发挥想象力.
        5. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )
    
    
    def get_prompt_fake(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏NPC">{character}</character>
            <dream_true description="游戏NPC的真实愿望">{dream_true}</dream_true>
        </game_information>
        
        <task>
        基于主题(`theme`)、背景(`background`)和人物设定(`character`)，为NPC生成一个想要实现的“表面愿望”。
        </task>
        
        <dream_true>
        {dream_true}
        </dream_true>
        
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
        3. 使用中文回答.
        4. 尽可能发挥想象力.
        5. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character", "dream_true"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
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
    dream_llm = DreamLLM()
    result_true = await dream_llm.arun(type='TRUE')
    result_fake = await dream_llm.arun(type='FAKE', dream_true=result_true)
    print(result_true)
    print(result_fake)


if __name__ == "__main__":
    asyncio.run(main())