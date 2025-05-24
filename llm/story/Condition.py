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
DEFAULT_OPENAI_TEMPERATURE = 0.8


class ConditionLLM:
    def __init__(self, type: str = 'TRUE', system_prompt: str = None):
        self.system_prompt = system_prompt
        
        assert type in ['TRUE', 'FAKE'], "type must be 'TRUE' or 'FAKE'"
        self.type = type.upper()
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt(type=self.type)
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="condition", description="Paragraph that describes the condition of reaching the dream", type="string")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self, type: str = 'TRUE'):
        LABELS = {
            'TRUE': "真实愿望",
            'FAKE': "虚假愿望",
        }
        
        prompt_template = """
        <system>{system_prompt}</system>        

        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <character description="游戏主角">{character}</character>
            <dream description="游戏主角的{dream_type}">{dream}</dream>
        </game_information>
        
        <task>
        基于游戏信息(`game_information`)，为主角生成一个达成愿望的条件.
        </task>
        
        <workflow>
        按照以下步骤为主角设计一个达成愿望的条件:
        1. 结合输入的主题(`theme`)、背景(`background`)、人物设定(`character`)和{dream_type}(`dream`)，采用逆向思维，思考一个有助于{dream_type}实现的条件. 比如说，改变某个通常无法改变的元素，或者引发不寻常的因果关系.
        2. 这个条件必须是能渐进式地被满足的.
        3. 从人物的视角出发，将需要满足的条件用一句话描述为输出.
        </workflow>

        <constraints>
        1. Use Chinese to answer.
        2. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character", "dream"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "dream_type": LABELS[type],
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )
    

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    def run(self, theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream: str = '想要实现一个能够改变世界的愿望'):
        try:
            return self.chain.invoke({"theme": theme, "background": background, "character": character, "dream": dream})
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str = '科幻', background: str = '未来世界', character: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。', dream: str = '想要实现一个能够改变世界的愿望'):
        try:
            return await self.chain.ainvoke({"theme": theme, "background": background, "character": character, "dream": dream})
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    condition_llm_true = ConditionLLM(type='TRUE')
    condition_llm_fake = ConditionLLM(type='FAKE')
    result_true = await condition_llm_true.arun()
    result_fake = await condition_llm_fake.arun()
    print(result_true)
    print(result_fake)


if __name__ == "__main__":
    asyncio.run(main())