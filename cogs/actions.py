import random
import discord
from discord.ext import commands
from discord import app_commands

class Action(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #TODO: Make the Hug Action 
  @app_commands.command(name="hug", description="Hugs someone :3")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        links = [
               "https://media.tenor.com/m/Lx6pxlvj44gAAAAC/ralsei-deltarune.gif"
               "https://media.tenor.com/m/CnXZJo9ddGIAAAAC/ralsei-cute-ralsei.gif"
               "https://media.tenor.com/lHCzlH_ez84AAAAi/cute-love.gif"
               "https://media.tenor.com/xFEinJ1BTosAAAAi/cartoon-patting.gif"
               ] 

        chosen_gif = random.choice(links)

        embed = discord.Embed(
               title=f"{interaction.user.display_name} has hugged {member.display_name}",
               description=f"Awwww!",
               color=discord.Color.green()
               )
        
        embed.set_image(url=chosen_gif)

        await interaction.response.send_message(embed=embed)
  
    #TODO: Make the kiss action
    @app_commands.command(name="kiss", description="Kisses someone :3")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        links = [
               "https://media.tenor.com/m/Lx6pxlvj44gAAAAC/ralsei-deltarune.gif"
               "https://media.tenor.com/m/CnXZJo9ddGIAAAAC/ralsei-cute-ralsei.gif"
               "https://media.tenor.com/lHCzlH_ez84AAAAi/cute-love.gif"
               "https://media.tenor.com/xFEinJ1BTosAAAAi/cartoon-patting.gif"
               ] 

        chosen_gif = random.choice(links)

        embed = discord.Embed(
               title=f"{interaction.user.display_name} has kissed {member.display_name}",
               description=f"Awwww!",
               color=discord.Color.green()
               )
        
        embed.set_image(url=chosen_gif)

        await interaction.response.send_message(embed=embed)

    #TODO: Make the headpat action: Kinda done..?
    @app_commands.command(name="headpat", description="Headpat somone :3")
    async def headpat(self, interaction: discord.Interaction, member: discord.Member):
        links = [
               "https://media.tenor.com/m/Lx6pxlvj44gAAAAC/ralsei-deltarune.gif"
               "https://media.tenor.com/m/CnXZJo9ddGIAAAAC/ralsei-cute-ralsei.gif"
               "https://media.tenor.com/lHCzlH_ez84AAAAi/cute-love.gif"
               "https://media.tenor.com/xFEinJ1BTosAAAAi/cartoon-patting.gif"
               ] 

        chosen_gif = random.choice(links)

        embed = discord.Embed(
               title=f"{interaction.user.display_name} has headpatted {member.display_name}",
               description=f"Awwww!",
               color=discord.Color.green()
               )
        
        embed.set_image(url=chosen_gif)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Action(bot))
