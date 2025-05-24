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
DEFAULT_OPENAI_TEMPERATURE = 0.8


class BackgroundLLM:
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
            ResponseSchema(name="background", description="Paragraph that describes the background of the game", type="string")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>

        <task>
        游戏的主题是: {theme}. 根据游戏主题描述一个背景设定.
        </task>

        <constraints>
        1. 描述需要包含地点.
        2. 描述需要简洁.
        3. 需要有出人意料的夸张点.
        4. 不能出现现实里的事物.
        5. Use Chinese to answer.
        6. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
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