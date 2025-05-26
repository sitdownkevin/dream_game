import os
import asyncio
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE_HIGH", 0.8))


class CharacLLM:
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
            ResponseSchema(
                name="name", description="The name of the character", type="string"),
            ResponseSchema(
                name="role", description="The role of the character", type="string"),
            ResponseSchema(
                name="age", description="The age of the character", type="integer"
            ),
            ResponseSchema(
                name="description", description="A short description of the character", type="string"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)

    def get_prompt(self):
        messages = []
        
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <task>
        <goal>
        基于游戏信息(`game_information`)，为NPC生成一个设定.
        </goal>
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <personality description="NPC特性">{personality}</personality>
        </game_information>
        <constraints>
        1. NPC设定包括名字、年龄、角色、描述.
        2. NPC设定的名字要有想象力，不能和世面已有的游戏角色重名.
        3. NPC设定的名字不能学习原神、魔兽的风格.
        4. NPC 设定的名字不能包含'璃'、'星'字.
        5. 年龄在14-20岁之间.
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
            format_instructions=self.output_parser.get_format_instructions(),
        )

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser

    def run(self, theme: str = None, background: str = None, personality: str = None):
        try:
            return self.chain.invoke({"theme": theme, "background": background, "personality": personality})
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def arun(self, theme: str = None, background: str = None, personality: str = None):
        try:
            return await self.chain.ainvoke({"theme": theme, "background": background, "personality": personality})
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    charac_llm = CharacLLM()
    result = await charac_llm.arun(
        theme='科幻',
        background='未来世界',
        personality='善良和美丽的角色，但同时具有一个正面的性格特性和高度负面的性格特性'
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
