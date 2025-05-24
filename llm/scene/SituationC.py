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


class SituationCLLM:
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
            ResponseSchema(name="description", description="Paragraph that describes the situation")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information>
            <theme>{theme}</theme>
            <background>{background}</background>
            <soul>{soul}</soul>
            <character>{character}</character>
            <dream_true>{dream_true}</dream_true>
            <dream_fake>{dream_fake}</dream_fake>
            <condition_true>{condition_true}</condition_true>
            <condition_fake>{condition_fake}</condition_fake>
            <prev_situation_description>{prev_situation_description}</prev_situation_description>
            <prev_situation_options_choice>{prev_situation_options_choice}</prev_situation_options_choice>
            <prev_situation_result>{prev_situation_result}</prev_situation_result>
        </game_information>

        <task>
        描述主角与一个试图阻碍其进展的对立角色相遇的情景。
        使魔在一旁观察，思考如何应对。
        </task>

        <constraints>
        1. Use Chinese to answer.
        2. Based on the information in `game_information`.
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "soul", "character", "dream_true", "dream_fake", "condition_true", "condition_fake", "prev_situation_description", "prev_situation_options_choice", "prev_situation_result"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str, background: str, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str):
        try:
            return self.chain.invoke({
                "theme": theme,
                "background": background,
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "prev_situation_description": prev_situation_description,
                "prev_situation_options_choice": prev_situation_options_choice,
                "prev_situation_result": prev_situation_result,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str, background: str, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str):
        try:
            return await self.chain.ainvoke({
                "theme": theme,
                "background": background,
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "prev_situation_description": prev_situation_description,
                "prev_situation_options_choice": prev_situation_options_choice,
                "prev_situation_result": prev_situation_result,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    situation_c_llm = SituationCLLM()
    result = await situation_c_llm.arun(
        theme="科幻",
        background="未来世界",
        soul="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        character="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        dream_true="想要实现一个能够改变世界的愿望",
        dream_fake="想要实现一个能够改变世界的愿望",
        condition_true="想要实现一个能够改变世界的愿望",
        condition_fake="想要实现一个能够改变世界的愿望",
        prev_situation_description="主角在游戏中遇到了一个使魔，使魔告诉主角一个实现愿望的方法",
        prev_situation_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。",
        prev_situation_result="主角选择了使魔的对话选项，使魔告诉主角一个实现愿望的方法",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())