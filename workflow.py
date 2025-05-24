from llm.role.Charac import CharacLLM
from llm.story.Background import BackgroundLLM
from llm.story.Dream import DreamLLM
from llm.story.Condition import ConditionLLM
from llm.story.Theme import ThemeLLM
from llm.role.Soul import SoulLLM
from llm.scene.SituationA import SituationALLM
from llm.scene.SituationAOpt import SituationAOptLLM
from llm.scene.SituationAResult import SituationAResultLLM
from llm.scene.SituationB import SituationBLLM
from llm.scene.SituationBOpt import SituationBOptLLM
from llm.scene.SituationBResult import SituationBResultLLM
from llm.scene.SituationC import SituationCLLM
from llm.scene.SituationCOpt import SituationCOptLLM
from llm.scene.SituationCResult import SituationCResultLLM
from llm.story.Ending import EndingLLM

import asyncio
import random


class Workflow:
    def __init__(self, verbose: bool = False):
        # Configuration
        self.verbose = verbose
        
        # 初始化所有LLM实例
        self.charac_llm = CharacLLM()
        self.background_llm = BackgroundLLM()
        self.dream_llm = DreamLLM()
        self.condition_llm_true = ConditionLLM(type='TRUE')
        self.condition_llm_fake = ConditionLLM(type='FAKE')
        self.theme_llm = ThemeLLM()
        self.soul_llm = SoulLLM()
        self.situation_a_llm = SituationALLM()
        self.situation_a_opt_llm = SituationAOptLLM()
        self.situation_a_result_llm = SituationAResultLLM()
        self.situation_b_llm = SituationBLLM()
        self.situation_b_opt_llm = SituationBOptLLM()
        self.situation_b_result_llm = SituationBResultLLM()
        self.situation_c_llm = SituationCLLM()
        self.situation_c_opt_llm = SituationCOptLLM()
        self.situation_c_result_llm = SituationCResultLLM()
        self.ending_llm = EndingLLM(type="NORMAL")
        # 存储各种生成的数据
        self.soul = None
        self.theme = None
        self.background = None
        self.character = None
        self.dream_true = None
        self.dream_fake = None
        self.condition_true = None
        self.condition_fake = None
        self.situation_a = None
        self.situation_a_options = None
        self.situation_a_options_choice = None
        self.situation_a_result = None
        self.situation_b = None
        self.situation_b_options = None
        self.situation_b_options_choice = None
        self.situation_b_result = None
        self.situation_c = None
        self.situation_c_options = None
        self.situation_c_options_choice = None
        self.situation_c_result = None
        self.ending = None

    async def generate_soul_and_theme(self):
        """并行生成灵魂和主题"""
        print("生成灵魂和主题...")
        tasks = [
            self.soul_llm.arun(),
            self.theme_llm.arun(),
        ]
        soul_result, theme_result = await asyncio.gather(*tasks)
        
        self.soul = soul_result['soul']
        self.theme = theme_result['theme']
        
        if self.verbose:
            print(f"灵魂: {soul_result}")
            print(f"主题: {theme_result}")

    async def generate_background(self):
        """生成背景故事"""
        print("生成背景故事...")
        background_result = await self.background_llm.arun(theme=self.theme)
        self.background = background_result['background']
        
        if self.verbose:
            print(f"背景: {background_result}")

    async def generate_character(self):
        """生成角色"""
        print("生成角色...")
        character_result = await self.charac_llm.arun(
            theme=self.theme, 
            background=self.background
        )
        self.character = character_result
        
        if self.verbose:
            print(f"角色: {character_result}")

    async def generate_dreams(self):
        """生成真实和虚假梦境"""
        print("生成真实梦境...")
        dream_true_result = await self.dream_llm.arun(
            type='TRUE', 
            theme=self.theme, 
            background=self.background, 
            character=self.character
        )
        self.dream_true = dream_true_result['dream']
        
        if self.verbose:
            print(f"真实梦境: {dream_true_result}")

        print("生成虚假梦境...")
        dream_fake_result = await self.dream_llm.arun(
            type='FAKE', 
            theme=self.theme, 
            background=self.background, 
            character=self.character, 
            dream_true=self.dream_true
        )
        self.dream_fake = dream_fake_result['dream']
        
        if self.verbose:
            print(f"虚假梦境: {dream_fake_result}")

    async def generate_conditions(self):
        """并行生成真实和虚假条件"""
        print("生成条件...")
        tasks = [
            self.condition_llm_true.arun(
                theme=self.theme, 
                background=self.background, 
                character=self.character, 
                dream=self.dream_true
            ),
            self.condition_llm_fake.arun(
                theme=self.theme, 
                background=self.background, 
                character=self.character, 
                dream=self.dream_fake
            ),
        ]
        condition_true_result, condition_fake_result = await asyncio.gather(*tasks)
        
        self.condition_true = condition_true_result['condition']
        self.condition_fake = condition_fake_result['condition']
        
        if self.verbose:
            print(f"真实条件: {condition_true_result}")
            print(f"虚假条件: {condition_fake_result}")

    async def generate_situation(self):
        """生成情景 A 描述"""
        print("生成情景 A...")
        situation_result = await self.situation_a_llm.arun(
            theme=self.theme,
            soul=self.soul,
            background=self.background,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
        )
        self.situation = situation_result['description']
        
        if self.verbose:
            print(f"情景 A: {situation_result}")

    async def generate_situation_options(self):
        """生成情景 A 选项"""
        print("生成情景 A 选项...")
        situation_options_result = await self.situation_a_opt_llm.arun(
            soul=self.soul,
            theme=self.theme,
            background=self.background,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            current_situation_description=self.situation_a,
        )
        self.situation_a_options = situation_options_result
        
        if self.verbose:
            print(f"情景 A 选项: {situation_options_result}")


    async def make_choice_for_situation(self, choice: str):
        """情景 A 玩家做出选择"""
        assert choice in ['CHOICE_A', 'CHOICE_B', 'CHOICE_C']
        print(f"情景 A 玩家选择...")
        self.situation_a_options_choice = self.situation_a_options[choice]
        if self.verbose:
            print(f"选择: {self.situation_a_options_choice}")
        
        print("生成情景 A 结果...")
        situation_result_result = await self.situation_a_result_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            current_situation_description=self.situation_a,
            current_situation_options_choice=self.situation_a_options_choice,
        )
        
        self.situation_a_result = situation_result_result['result']
        if self.verbose:
            print(f"情景 A 结果: {self.situation_a_result}")


    async def generate_situation_b(self):
        """生成情景 B 描述"""
        print("生成情景 B...")
        situation_b_result = await self.situation_b_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_a,
            prev_situation_options_choice=self.situation_a_options_choice,
            prev_situation_result=self.situation_a_result,
        )
        self.situation_b = situation_b_result['description']
        if self.verbose:
            print(f"情景 B: {situation_b_result}")


    async def generate_situation_b_options(self):
        """生成情景 B 选项"""
        print("生成情景 B 选项...")
        situation_b_options_result = await self.situation_b_opt_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_a,
            prev_situation_options_choice=self.situation_a_options_choice,
            prev_situation_result=self.situation_a_result,
            current_situation_description=self.situation_b,
        )
        self.situation_b_options = situation_b_options_result
        if self.verbose:
            print(f"情景 B 选项: {situation_b_options_result}")

    
    async def make_choice_for_situation_b(self, choice: str):
        """情景 B 玩家做出选择"""
        assert choice in ['CHOICE_A', 'CHOICE_B', 'CHOICE_C']
        
        print(f"情景 B 玩家选择...")
        self.situation_b_options_choice = self.situation_b_options[choice]
        if self.verbose:
            print(f"选择: {self.situation_b_options_choice}")
            
        print("生成情景 B 结果...")
        situation_b_result_result = await self.situation_b_result_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_a,
            prev_situation_options_choice=self.situation_a_options_choice,
            prev_situation_result=self.situation_a_result,
            current_situation_description=self.situation_b,
            current_situation_options_choice=self.situation_b_options_choice,
        )
        self.situation_b_result = situation_b_result_result['result']
        if self.verbose:
            print(f"情景 B 结果: {self.situation_b_result}")


    async def generate_situation_c(self):
        """生成情景 C 描述"""
        print("生成情景 C...")
        situation_c_result = await self.situation_c_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_b,
            prev_situation_options_choice=self.situation_b_options_choice,
            prev_situation_result=self.situation_b_result,
        )
        self.situation_c = situation_c_result['description']
        if self.verbose:
            print(f"情景 C: {situation_c_result}")
    
    async def generate_situation_c_options(self):
        """生成情景 C 选项"""
        print("生成情景 C 选项...")
        situation_c_options_result = await self.situation_c_opt_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_b,
            prev_situation_options_choice=self.situation_b_options_choice,
            prev_situation_result=self.situation_b_result,
            current_situation_description=self.situation_c,
        )
        self.situation_c_options = situation_c_options_result
        if self.verbose:
            print(f"情景 C 选项: {situation_c_options_result}")
    
    
    async def make_choice_for_situation_c(self, choice: str):
        """情景 C 玩家做出选择"""
        assert choice in ['CHOICE_A', 'CHOICE_B', 'CHOICE_C']
        
        print(f"情景 C 玩家选择...")
        self.situation_c_options_choice = self.situation_c_options[choice]
        if self.verbose:
            print(f"选择: {self.situation_c_options_choice}")
            
        print("生成情景 C 结果...")
        situation_c_result_result = await self.situation_c_result_llm.arun(
            theme=self.theme,
            background=self.background,
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            prev_situation_description=self.situation_b,
            prev_situation_options_choice=self.situation_b_options_choice,
            prev_situation_result=self.situation_b_result,
            current_situation_description=self.situation_c,
            current_situation_options_choice=self.situation_c_options_choice,
        )
        self.situation_c_result = situation_c_result_result['result']
        if self.verbose:
            print(f"情景 C 结果: {self.situation_c_result}")

    async def generate_ending(self):
        """生成结局"""
        print("生成结局...")
        ending_result = await self.ending_llm.arun(
            soul=self.soul,
            character=self.character,
            dream_true=self.dream_true,
            dream_fake=self.dream_fake,
            condition_true=self.condition_true,
            condition_fake=self.condition_fake,
            situation_a_description=self.situation_a,
            situation_a_options_choice=self.situation_a_options_choice,
            situation_a_result=self.situation_a_result,
            situation_b_description=self.situation_b,
            situation_b_options_choice=self.situation_b_options_choice,
            situation_b_result=self.situation_b_result,
            situation_c_description=self.situation_c,
            situation_c_options_choice=self.situation_c_options_choice,
            situation_c_result=self.situation_c_result,
        )
        self.ending = ending_result['ending']
        if self.verbose:
            print(f"结局: {ending_result}")

    async def play(self):
        """执行完整的生成流程"""
        await self.generate_soul_and_theme()
        await self.generate_background()
        await self.generate_character()
        await self.generate_dreams()
        await self.generate_conditions()
        
        await self.generate_situation()
        await self.generate_situation_options()
        await self.make_choice_for_situation(f'CHOICE_{random.choice(["A", "B", "C"])}')
        
        await self.generate_situation_b()
        await self.generate_situation_b_options()
        await self.make_choice_for_situation_b(f'CHOICE_{random.choice(["A", "B", "C"])}')
        
        await self.generate_situation_c()
        await self.generate_situation_c_options()
        await self.make_choice_for_situation_c(f'CHOICE_{random.choice(["A", "B", "C"])}')
        
        await self.generate_ending()


    def get_all_data(self):
        """获取所有生成的数据"""
        return {
            'soul': self.soul,
            'theme': self.theme,
            'background': self.background,
            'character': self.character,
            'dream_true': self.dream_true,
            'dream_fake': self.dream_fake,
            'condition_true': self.condition_true,
            'condition_fake': self.condition_fake,
            'situation_a': self.situation_a,
            'situation_a_options': self.situation_a_options,
            'situation_a_options_choice': self.situation_a_options_choice,
            'situation_a_result': self.situation_a_result,
            'situation_b': self.situation_b,
            'situation_b_options': self.situation_b_options,
            'situation_b_options_choice': self.situation_b_options_choice,
            'situation_b_result': self.situation_b_result,
            'situation_c': self.situation_c,
            'situation_c_options': self.situation_c_options,
            'situation_c_options_choice': self.situation_c_options_choice,
            'situation_c_result': self.situation_c_result,
            'ending': self.ending,
        }


async def main():
    workflow = Workflow(verbose=True)
    await workflow.play()

if __name__ == "__main__":
    asyncio.run(main())
