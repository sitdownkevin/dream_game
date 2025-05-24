from llm.role.CharacLLM import CharacLLM
from llm.story.BackgroundLLM import BackgroundLLM
from llm.story.DreamLLM import DreamLLM
from llm.story.ConditionLLM import ConditionLLM
from llm.story.ThemeLLM import ThemeLLM
from llm.role.SoulLLM import SoulLLM
from llm.scene.SituationALLM import SituationALLM
from llm.scene.SituationAOptLLM import SituationAOptLLM

import sys, os
import asyncio

class Workflow:
    def __init__(self, verbose: bool = False):
        self.charac_llm = CharacLLM()
        self.background_llm = BackgroundLLM()
        self.dream_llm = DreamLLM()
        self.condition_llm = ConditionLLM()
        self.theme_llm = ThemeLLM()
        self.soul_llm = SoulLLM()
        self.situation_llm = SituationALLM()
        self.situation_aopt_llm = SituationAOptLLM()
        
        self.verbose = verbose
        self.data = None
        
    async def generate_information(self):
        print("Generating information...")
        tasks = [
            self.soul_llm.arun(),
            self.theme_llm.arun(),
        ]
        soul, theme = await asyncio.gather(*tasks)
        if self.verbose:
            print(soul)
            print(theme)
            
        print("Generating background...")
        background = await self.background_llm.arun(theme=theme)
        if self.verbose:
            print(background)
            
        print("Generating character...")
        character = await self.charac_llm.arun(theme=theme, background=background)
        if self.verbose:
            print(character)
            
        print("Generating dream...")
        dream_true = await self.dream_llm.arun(type='true', theme=theme, background=background, character=character)
        if self.verbose:
            print(dream_true)
            
        print("Generating dream fake...")
        dream_fake = await self.dream_llm.arun(type='fake', theme=theme, background=background, character=character, dream_true=dream_true)
        if self.verbose:
            print(dream_fake)
            
        print("Generating condition...")
        tasks = [
            self.condition_llm.arun(type='true', theme=theme, background=background, character=character, dream=dream_true),
            self.condition_llm.arun(type='fake', theme=theme, background=background, character=character, dream=dream_fake),
        ]
        condition_true, condition_fake = await asyncio.gather(*tasks)
        if self.verbose:
            print(condition_true)
            print(condition_fake)
            
        print("Generating situation...")
        tasks = [
            self.situation_llm.arun(
                theme=theme['theme'],
                soul=soul['soul'],
                background=background['background'],
                character=character,
                dream_true=dream_true['dream'],
                dream_fake=dream_fake['dream'],
                condition_true=condition_true['condition'],
                condition_fake=condition_fake['condition'],
            ),
        ]
        situation = await asyncio.gather(*tasks)
        if self.verbose:
            print(situation)
            
        print("Generating situation options...")
        tasks = [
            self.situation_aopt_llm.arun(
                soul=soul['soul'],
                theme=theme['theme'],
                background=background['background'],
                character=character,
                dream_true=dream_true['dream'],
                dream_fake=dream_fake['dream'],
                condition_true=condition_true['condition'],
                condition_fake=condition_fake['condition'],
                current_situation_description=situation['description'],
            ),
        ]
        situation_options = await asyncio.gather(*tasks)
        if self.verbose:
            print(situation_options)
        
        self.data = {
            'soul': soul,
            'theme': theme,
            'background': background,
            'character': character,
            'dream_true': dream_true,
            'dream_fake': dream_fake,
            'condition_true': condition_true,
            'condition_fake': condition_fake,
            'situation': situation,
            'situation_options': situation_options,
        }


async def main():
    workflow = Workflow(verbose=True)
    await workflow.generate_information()
    print(workflow.data)


if __name__ == "__main__":
    asyncio.run(main())