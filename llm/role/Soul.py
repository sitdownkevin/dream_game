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


class SoulLLM:
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
            ResponseSchema(name="soul", description="One sentence that describes the soul of the character", type="string")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <basic_characteristics description="主角基本人物特性">
        善良和美丽的少女，同时具有一个正面的性格特性和高度负面的性格特性.
        </basic_characteristics>

        <task>
        基于主角基本人物特性(`basic_characteristics`)，给出一个可能的灵魂设定.
        </task>

        <constraints>
        1. Use Chinese to answer.
        2. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions(), "system_prompt": self.system_prompt},
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