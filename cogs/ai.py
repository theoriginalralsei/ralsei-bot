import discord
import asyncio
from discord.ext import commands
from discord import app_commands
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM

class Generator:
    def __init__(self, vocab_size: int, embed_size: int, hidden_size: int, num_classes: int):
        self.model = AutoModelForCausalLM.from_pretrained("gpt2")
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")

        if torch.cuda.is_available():
            self.model.to("cuda")

        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model.eval()
        torch.set_grad_enabled(False)

    def generate_sync(self, prompt: str, man_tokens: int):
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt",
            truncation=True,
            max_length=256,
        ).to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

        outputs_ids = self.model.generate(
            **inputs,
            max_new_tokens=man_tokens,
            do_sample=True,
            temperature=0.5,
            top_p=0.95,
            repitition_penalty=1.2,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        return self.tokenizer.decode(outputs_ids[0], skip_special_tokens=True)

    async def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        return await asyncio.to_thread(self.generate_sync, prompt, max_tokens)

class AI(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.generator = Generator(vocab_size=1000, embed_size=768, hidden_size=768, num_classes=50257)

    @app_commands.command(name="ai", description="A half useful AI i made")
    async def generate(self, interaction: discord.Interaction, prompt: str) -> None:
        await interaction.response.defer(epthemeral=True)

        if len(prompt) > 1000:
            await interaction.followup.send("Prompt too long! (Max 1000 characters)", ephemeral=True)
            return

        try:
            embed = discord.Embed(
                title="AI",
                color=discord.Color.blue(),
            )

            embed.add_field(name="Prompt", value=prompt, inline=False)
            response = self.generator.generate_text(prompt)

            if len(response) > 1000:
                response = response[:1000] + "..."

            embed.add_field(name="Response", value=response, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            print(e)
            raise e


async def setup(bot):
    await bot.add_cog(AI(bot))
