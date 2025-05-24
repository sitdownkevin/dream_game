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


class ThemeLLM:
    def __init__(self):
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="theme", description="One word that describes the theme of the game")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>

        <task>
        用一个词描述一类游戏主题，比如：科幻、冒险、推理等。
        </task>

        <constraints>
        1. 只需包含一个词的描述。
        2. 使用中文回答。
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["basic_characteristics"],
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
    theme_llm = ThemeLLM()
    result = await theme_llm.arun()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())