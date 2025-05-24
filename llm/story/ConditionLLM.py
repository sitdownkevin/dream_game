from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = "deepseek-ai/DeepSeek-V3"
DEFAULT_OPENAI_TEMPERATURE = 0.3


class ConditionLLM:
    def __init__(self):
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
            ResponseSchema(name="condition", description="One sentence that describes the condition of the character")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt_true(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <role>
        你是一位具有逆向思维和强大创造力的游戏剧情设计师
        </role>
        
        <theme>
        {theme}
        </theme>
        
        <background>
        {background}
        </background>
        
        <character>
        {character}
        </character>
        
        <dream_true>
        {dream}
        </dream_true>
        
        <task>
        任务是基于主题(`theme`)、背景(`background`)和人物设定(`character`)，为主角生成一个达成愿望的条件
        </task>
        
        <workflow>
        按照以下步骤为主角设计一个达成真实愿望的条件：
        1. 结合输入的主题(`theme`)、背景(`background`)、人物设定(`character`)和真实愿望(`dream_true`)，采用逆向思维，思考一个有助于真实愿望实现的条件。比如说，改变某个通常无法改变的元素，或者引发不寻常的因果关系。
        2. 这个条件必须是能渐进式地被满足的。
        3. 从人物的视角出发，将需要满足的条件用一句话描述为输出。
        </workflow>

        <constraints>
        1. 使用中文回答。
        2. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character", "dream"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )
    
    
    def get_prompt_fake(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <role>
        你是一位具有逆向思维和强大创造力的游戏剧情设计师
        </role>
        
        <theme>
        {theme}
        </theme>
        
        <background>
        {background}
        </background>
        
        <character>
        {character}
        </character>
        
        <dream_fake>
        {dream}
        </dream_fake>
        
        <task>
        任务是基于主题(`theme`)、背景(`background`)和人物设定(`character`)，为主角生成一个达成愿望的条件
        </task>
        
        <workflow>
        按照以下步骤为主角设计一个达成真实愿望的条件：
        1. 结合输入的主题(`theme`)、背景(`background`)、人物设定(`character`)和虚假愿望(`dream_fake`)，采用逆向思维，思考一个有助于虚假愿望实现的条件。比如说，改变某个通常无法改变的元素，或者引发不寻常的因果关系。
        2. 这个条件必须是能渐进式地被满足的。
        3. 从人物的视角出发，将需要满足的条件用一句话描述为输出。
        </workflow>

        <constraints>
        1. 使用中文回答。
        2. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character", "dream"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )
    
    
    def get_chain_true(self):
        return self.prompt_true | self.llm | self.output_parser
    
    
    def get_chain_fake(self):
        return self.prompt_fake | self.llm | self.output_parser
    
    
    def run(self, type: str = 'true', theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream: str = '想要实现一个能够改变世界的愿望'):
        try:
            if type == 'true':
                return self.chain_true.invoke({"theme": theme, "background": background, "character": character, "dream_true": dream})
            elif type == 'fake':
                return self.chain_fake.invoke({"theme": theme, "background": background, "character": character, "dream_fake": dream})
            else:
                raise ValueError(f"Invalid type: {type}")
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, type: str = 'true', theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream: str = '想要实现一个能够改变世界的愿望'):
        try:
            if type == 'true':
                return await self.chain_true.ainvoke({"theme": theme, "background": background, "character": character, "dream": dream})
            elif type == 'fake':
                return await self.chain_fake.ainvoke({"theme": theme, "background": background, "character": character, "dream": dream})
            else:
                raise ValueError(f"Invalid type: {type}")
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    condition_llm = ConditionLLM()
    result_true = await condition_llm.arun(type='true')
    result_fake = await condition_llm.arun(type='fake')
    print(result_true)
    print(result_fake)


if __name__ == "__main__":
    asyncio.run(main())