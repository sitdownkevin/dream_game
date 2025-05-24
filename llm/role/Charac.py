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


class CharacLLM:
    def __init__(self):
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="name", description="The name of the character"),
            ResponseSchema(name="role", description="The role of the character"),
            ResponseSchema(name="description", description="A short description of the character"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <theme>
        {theme}
        </theme>
        
        <background>
        {background}
        </background>
        
        <soul>
        {soul}
        </soul>
        
        <task>
        根据主题(`theme`)、背景(`background`)、灵魂(`soul`)，给出一个主角设定。
        </task>

        <constraints>
        1. 主角设定包括名字、角色、描述。
        2. 使用中文回答。
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "soul"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str = '科幻', background: str = '未来世界', soul: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。'):
        try:
            return self.chain.invoke({"theme": theme, "background": background, "soul": soul})
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str = '科幻', background: str = '未来世界', soul: str = '善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。'):
        try:
            return await self.chain.ainvoke({"theme": theme, "background": background, "soul": soul})
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    charac_llm = CharacLLM()
    result = await charac_llm.arun()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())