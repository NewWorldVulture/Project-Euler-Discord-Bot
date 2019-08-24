import discord
from discord.ext import commands
from datetime import datetime as d

# New - The Cog class must extend the commands.Cog class
class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='about',
        description='The about command'
    )
    async def about_command(self, ctx):
        # About command that spews useful information about the bot.

        help_embed = discord.Embed(
            title="ProjectEuler Discord Bot",
            description="""The Project Euler Discord Bot is a bot that selects random problems from
            the Project Euler website every n amount of time, which can be specified in seconds,
            minutes, hours, or days, with no limit (thanks for taking the hit, repl.it)

            For information about Project Euler, see the Project Euler Website: https://projecteuler.net/about
            For more information about the bot, see here: https://github.com/Dersyx/project-euler-discord-bot/tree/master""",
            colour=discord.Colour.blue()
            )  # Embed that's sent back to the user.

        # I'm cheating here a bit cause I couldn't figure out how to call for PREFIX directly.
        commands_list = """**Current Prefix:** `~`
        `about` - Shows this message
        `start <amount>` - Starts the random problem loop with <amount> of delay between each random problem which is specified with <amount>(d, h, m, s). **(Limited to server administrators)**
        `stop` - Stops the random problem loop, if there is a loop in the channel the command is called from. **(Limited to server administrators)**
        `getproblem <id>` - Displays a problem from the Project Euler website based on its number."""

        help_embed.add_field(name="Commands", value=commands_list)  # Add a field of available commands for the bot.

        await ctx.send(embed=help_embed)  # Sends the help_embed to the channel the command was called.


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
