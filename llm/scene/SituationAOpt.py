from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm.scene.SituationA import SituationALLM


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("DEFAULT_OPENAI_TEMPERATURE", 0.3))


class SituationAOptLLM:
    def __init__(self):
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
        self.situation_llm = SituationALLM(verbose=True)
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="CHOICE_A", description="One sentence description of the choice a"),
            ResponseSchema(name="CHOICE_B", description="One sentence description of the choice b"),
            ResponseSchema(name="CHOICE_C", description="One sentence description of the choice c"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <soul>
        {soul}
        </soul>
        
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
        {dream_true}
        </dream_true>
        
        <dream_fake>
        {dream_fake}
        </dream_fake>
        
        <condition_true>
        {condition_true}
        </condition_true>
        
        <condition_fake>
        {condition_fake}
        </condition_fake>
        
        <current_situation_description>
        {current_situation_description}
        </current_situation_description>

        <task>
        在主角与使魔相遇的情境中，生成使魔的对话选项。
        1. CHOICE_A: 这个选项表面上听起来很有吸引力，但对真实愿望有潜在的微妙损害。
        2. CHOICE_B: 这个选项应该涉及努力或风险，但承诺真正的满足感。
        3. CHOICE_C: 它应该导致一个中立、分散注意力或复杂的支线事件，不能明确地推动任何一个条件的实现。
        </task>

        <constraints>
        1. 使魔对话选项（促进真实愿望/条件）
        2. 基于灵魂(`soul`)、主题(`theme`)、背景(`background`)、人物设定(`character`)、达成真实愿望的条件(`condition_true`)、达成虚假愿望的条件(`condition_fake`)，生成使魔的对话选项。
        3. 基于当前情境(`current_situation_description`)，生成使魔的对话选项。
        4. 使魔的对话选项应该以微妙但明确的方式推动主角走向他们的真实愿望或真实条件的满足。这个选项应该涉及努力或风险，但承诺真正的满足感。
        5. 使用中文回答。
        6. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["soul", "theme", "background", "character", "dream_true", "dream_fake", "condition_true", "condition_fake", "current_situation_description"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
            validate_template=False
        )


    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, soul: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return self.chain.invoke({
                "soul": soul,
                "theme": theme,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "current_situation_description": current_situation_description,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, soul: str, theme: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, current_situation_description: str):
        try:
            return await self.chain.ainvoke({
                "soul": soul,
                "theme": theme,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "current_situation_description": current_situation_description,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    
    async def generate_options(self):
        situation_description = await self.situation_llm.agenerate_situation()
        if situation_description is None:
            return None
        
        result = await self.arun(
            soul=self.situation_llm.data['soul'],
            theme=self.situation_llm.data['theme'],
            background=self.situation_llm.data['background'],
            character=self.situation_llm.data['character'],
            dream_true=self.situation_llm.data['dream_true'],
            dream_fake=self.situation_llm.data['dream_fake'],
            condition_true=self.situation_llm.data['condition_true'],
            condition_fake=self.situation_llm.data['condition_fake'],
            current_situation_description=situation_description['description'],
        )
        
        return result
        

async def main():
    situation_aopt_llm = SituationAOptLLM()
    result = await situation_aopt_llm.generate_options()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())