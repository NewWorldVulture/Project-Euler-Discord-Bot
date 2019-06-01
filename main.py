# Works with Python 3.6
import os  
import random
import asyncio 
import discord
from discord.ext import commands  # Used to make commands

from keep_alive import keep_alive  # Used to keep it alive on repl.it
from time_duration import time_duration  # Used to set the duration between sending problems.
from problem import problem  # Gets an embed of the problem requested via problem id.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PREFIX = "~"  # Sets the prefix of the bot

LOOP = asyncio.get_event_loop()  # Creates an event loop (used to make tasks with asyncio)
channel_loop = {}  # Channel loop dictionary used to store tasks under their channel id.

client = commands.Bot(command_prefix=PREFIX)  # Defines the bot client with command PREFIX.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.event
async def on_ready():  # Once the bot is ready:
    """
    Changes the status of the bot to whatever, and notifies the console that the bot is ready.
    """

    print("The bot is ready!")
    await client.change_presence(game=discord.Game(name="for {}about".format(PREFIX), type=3))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.event
async def on_message(message):
    """
    On every single message that the bot sees, this will trigger.
    First, it makes sure that bot doesn't reply to itself.
    Then, it makes sure that the user executing commands isn't in a DM.
    Finally, it processes commands
    """

    # Ensures that the bot doesn't reply to itself
    if message.author == client.user:
        return

    if "hello there" in message.content or "Hello there" in message.content:
        await client.send_message(message.channel, "General Kenobi!")

    elif not message.content.startswith("{}about".format(PREFIX)):  # If the message is not the standard about command:
        if message.channel.is_private:  # If it is a private channel:
            # Tell them they can't:
            await client.send_message(message.channel, "You are not allowed to call other commands besides `{}about` in DMs.".format(PREFIX))
            return

    await client.process_commands(message)  # Process commands after this is triggered (bot commands won't work without this)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.event
async def on_command_error(exception, ctx):
    embed = discord.Embed(title="Error from command", description=str(exception), colour=discord.Colour.red())
    await client.send_message(ctx.message.channel, embed=embed)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.command()
async def about():
    """
    About command that spews useful information about the bot.
    """

    help_embed = discord.Embed(
        title="ProjectEuler Discord Bot",
        description="""The Project Euler Discord Bot is a bot that selects random problems from
        the Project Euler website every n amount of time, which can be specified in seconds,
        minutes, hours, or days, with no limit (thanks for taking the hit, repl.it)

        For information about Project Euler, see the Project Euler Website: https://projecteuler.net/about
        For more information about the bot, see here: https://repl.it/@Dersyx/Project-Euler-Discord-Bot""",
        colour=discord.Colour.blue()
        )  # Embed that's sent back to the user.

    commands = """**Current Prefix:** {}
    `about` - Shows this message
    `start <amount>` - Starts the random problem loop with <amount> of delay between each random problem which is specified with <amount>(d, h, m, s). **(Limited to server administrators)**
    `stop` - Stops the random problem loop, if there is a loop in the channel the command is called from. **(Limited to server administrators)**
    `getproblem <id>` - Displays a problem from the Project Euler website based on its number.""".format(PREFIX)

    help_embed.add_field(name="Commands", value=commands)  # Add a field of available commands for the bot.

    await client.say(embed=help_embed)  # Sends the help_embed to the channel the command was called.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def start(ctx, time_wait):
    """
    Checks to make sure there isn't a euler loop task already running.
    If there isn't, creates a task, and adds it to the channel_loop dictionary.
    """

    if ctx.message.channel.id in channel_loop:  # Checks the dictionary for a channel id mating the one where the command is being called.
        await client.send_message(ctx.message.channel, "There is already a Project Euler loop in this channel.")
    else:  
        duration = time_wait[-1:]  # Sets the duration initial equal to the last letter of the provided argument.
        time_wait = str(time_wait).replace("d", "",).replace("h", "").replace("m", "").replace("s", "")  # Removes the last letter set by duration, which should leave a raw int.

        try:
            time_wait = int(time_wait)  # Converting int test, which should work if the command was called correctly.
            wait_time = await time_duration(client, ctx, duration, time_wait)  # Calls the time_duration function

            loop = LOOP.create_task(euler(ctx, wait_time))  # Create a new euler() task.
            channel_loop[ctx.message.channel.id] = loop  # Adds the task to the channel_loop dictionary under the channel.id

        except ValueError:  # If the argument did not pass the int(time_wait) test above:
            await client.send_message(ctx.message.channel, "Please input a valid time interval.")  # Tell them that they messed up.
            return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def euler(ctx, time_wait):
    """
    This function is more of a filler, in order to make the command a task, which allows us to cancel it with the `stop` command.
    """

    random_problem_order = random.sample(range(1, 654), 653)  # Creates a random sample of 653 numbers.

    for random_problem_number in random_problem_order:
        problem_embed = await problem(client, ctx, random_problem_number)  # Call the problem function with the random_problem_number.
        await client.send_message(ctx.message.channel, embed=problem_embed)  # Sends the embed returned.   
        await asyncio.sleep(int(time_wait))  # Await n amount of time before going to the next number.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def stop(ctx):
    """
    Function to stop the loop in that channel.
    """
    if ctx.message.channel.id in channel_loop:  # Checks if there is a loop in that channel:
        task_to_cancel = channel_loop[ctx.message.channel.id]  # Gets the task object.
        task_to_cancel.cancel()  # Cancels.
        await client.send_message(ctx.message.channel, "You have cancelled the loop in this channel.")  # Alert the user.
        del channel_loop[ctx.message.channel.id]  # Delete the channel loop entry.
    else:  # If there is no loop:
        await client.send_message(ctx.message.channel, "There is no loop in this channel.")  # Alert the user.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.command(pass_context=True)
async def getproblem(ctx, problem_id):
    """
    Command to get info about a problem based on its id.
    """
    problem_embed = await problem(client, ctx, problem_id)
    await client.send_message(ctx.message.channel, embed=problem_embed)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# keep_alive()  # Creates a server to keep the bot alive on repl.it
TOKEN = os.environ.get("token")  # Gets the token via environment variables (.env files on repl.it)
client.run(TOKEN)  # Runs the bot
