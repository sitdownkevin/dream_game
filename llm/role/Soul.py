from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio
import os


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("DEFAULT_OPENAI_TEMPERATURE", 0.3))


class SoulLLM:
    def __init__(self):
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="soul", description="One sentence description of the character")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <basic_characteristics>
        ### 游戏基本人物特性：
        善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。
        </basic_characteristics>

        <task>
        根据基本人物特性(`basic_characteristics`)，给出一个可能的主角设定。
        </task>

        <constraints>
        1. 主角设定必须符合基本人物特性。
        2. 只需包含一句话的简要特征描述。
        3. 使用中文回答。
        4. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self):
        try:
            return self.chain.invoke({})
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self):
        try:
            return await self.chain.ainvoke({})
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    soul_llm = SoulLLM()
    result = await soul_llm.arun()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())