# Works with Python 3.6
import random
import asyncio
import discord
from discord.ext import commands  # Used to make commands

from problem import problem  # Gets an embed of the problem requested via problem id.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PREFIX = "~"  # Sets the prefix of the bot

LOOP = asyncio.get_event_loop()  # Creates an event loop (used to make tasks with asyncio)
channel_loop = {}  # Channel loop dictionary used to store tasks under their channel id.

bot = commands.Bot(command_prefix=PREFIX,
    description='A Discord bot to interface with the Project Euler website and provide a random set of problems.',
    case_insensitive=True)

cogs = ['cogs.basic']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.event
async def on_ready():  # Once the bot is ready:

    print("Logged in as {} - {} The bot is ready!".format(bot.user.name, bot.user.id))
    for cog in cogs:
        bot.load_extension(cog)
    game = discord.Game(name="for {}help".format(PREFIX), type=3)
    await bot.change_presence(activity=game)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.event
async def on_message(message):
    """
    On every single message that the bot sees, this will trigger.
    First, it makes sure that bot doesn't reply to itself.
    Then, it makes sure that the user executing commands isn't in a DM.
    Finally, it processes commands
    """

    # Ensures that the bot doesn't reply to itself
    if message.author == bot.user:
        return

    if "hello there" in message.content.lower():
        await message.channel.send("General Kenobi!")

    elif not message.content.startswith("{}about".format(PREFIX)):  # If the message is not the standard about command:
        if isinstance(message.channel, discord.abc.PrivateChannel):  # If it is a private channel:
            # Tell them they can't:
            await message.channel.send("You are not allowed to call commands other than `{}about` in DMs.".format(PREFIX))
            return

    await bot.process_commands(message)  # Process commands after this is triggered (bot commands won't work without this)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.event
async def on_command_error(message, exception):
    #print("Exception: {}\n\nMessage: {}".format(exception, message))
    embed = discord.Embed(title="Error from command", description=str(exception), colour=discord.Colour.red())
    print("Error with message from{}: {}\n{}".format(message.author.id, message, exception))
    await message.channel.send(embed=embed)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def start(message, wait_time):
    """
    Checks to make sure there isn't a euler loop task already running.
    If there isn't, creates a task, and adds it to the channel_loop dictionary.
    """

    seconds_per_unit = {"s": [1, "seconds"],
                        "m": [60, "minutes"],
                        "h": [36000, "hours"],
                        "d": [86400, "days"]}

    if message.channel.id in channel_loop:  # Checks the dictionary for a channel id mating the one where the command is being called.
        await message.channel.send("There is already a Project Euler loop in this channel.")
    else:
        try:
            # Calculate number of seconds
            s = int(wait_time[:-1]) * seconds_per_unit[wait_time[-1]][0]
            await message.channel.send("You have started the random problem loop with a time interval of {} {}.".format(wait_time[:-1][0], seconds_per_unit[wait_time[-1]][1]))

            loop = LOOP.create_task(euler(message, s))  # Create a new euler() task.
            channel_loop[message.channel.id] = loop  # Adds the task to the channel_loop dictionary under the channel.id

        except ValueError:  # If the argument did not pass the int(time_wait) test above:
            await message.channel.send("Please input a valid time interval.")  # Tell them that they messed up.
            return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def euler(message, s):
    """
    This function is more of a filler, in order to make the command a task, which allows us to cancel it with the `stop` command.
    """

    random_problem_order = random.sample(range(1, 654), 653)  # Creates a random sample of 653 numbers.

    for random_problem_number in random_problem_order:
        problem_embed = await problem(bot, message, random_problem_number)  # Call the problem function with the random_problem_number.
        await message.channel.send(embed=problem_embed)  # Sends the embed returned.
        await asyncio.sleep(int(s))  # Await n amount of time before going to the next number.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def stop(message):
    """
    Function to stop the loop in that channel.
    """
    if message.channel.id in channel_loop:  # Checks if there is a loop in that channel:
        task_to_cancel = channel_loop[message.channel.id]  # Gets the task object.
        task_to_cancel.cancel()  # Cancels.
        await message.channel.send("You have cancelled the loop in this channel.")  # Alert the user.
        del channel_loop[message.channel.id]  # Delete the channel loop entry.
    else:  # If there is no loop:
        await message.channel.send("There is no loop in this channel.")  # Alert the user.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@bot.command(pass_context=True)
async def getproblem(message, problem_id):
    """
    Command to get info about a problem based on its id.
    """
    problem_embed = await problem(bot, message, problem_id)
    await message.channel.send(embed=problem_embed)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TOKEN = ""

bot.run(TOKEN, bot=True, reconnect=True)  # Runs the bot
