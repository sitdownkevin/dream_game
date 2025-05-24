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


class BackgroundLLM:
    def __init__(self):
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="background", description="One sentence that describes the background of the game"),
            ResponseSchema(name="theme", description="The theme of the game")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>

        <task>
        用一句话描述一个{theme}主题游戏中的背景设定，不能出现现实里的事物，需要有简洁但出人意料的夸张点。
        </task>

        <constraints>
        1. 只需包含地点，不要有任何额外叙述。
        2. 使用中文回答。
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str = '科幻'):
        try:
            return self.chain.invoke({"theme": theme})
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str = '科幻'):
        try:
            return await self.chain.ainvoke({"theme": theme})
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    background_llm = BackgroundLLM()
    result = await background_llm.arun(theme='冒险')
    print(result)


if __name__ == "__main__":
    asyncio.run(main())