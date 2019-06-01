import aiohttp
import asyncio
import discord
from html2text import html2text

async def problem(client, ctx, problem_id):
    """
    Takes in a problem_id, and returns a problem embed with all the necessary info.
    """
    try:
        problem_id = int(problem_id)  # Tries to convert problem_id to an int, which should work if the interval provided is formatted correctly.
    except ValueError:  # If the argument provided is not formatted correctly (ie did not pass the int(time_wait) test), then:
        await client.send_message(ctx.message.channel, "Please make sure that you asking for a problem number, not a problem name")  # Tell them that they messed up
        return

    problem_link = "https://projecteuler.net/problem={}".format(problem_id)  # Create a problem link via the problem id.

    async with aiohttp.ClientSession() as session:  # Creats a client session for the function calling.
        problem_info = await fetch(session, problem_link)   # Fetches the link
        problem_info = html2text(problem_info)  # Converts it to text

    problem_title = str(problem_info.split("##")[1]).split("![]")[0]  # Splits the data to get the title of the problem.
    problem_info = str(problem_info.split(str(problem_id))[1]).replace("Project Euler: [Copyright Information](copyright) | [Privacy Policy](privacy)", "")  # Splits the data to get the raw info about the problem 

    problem_embed = discord.Embed(
        title="Problem {}: {}".format(problem_id, problem_title),
        description=problem_info,
        colour=discord.Colour.blue(),
        url=problem_link
    )  # Discord embed with the problem title, number, info, and url.
        
    return problem_embed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def fetch(session, url):
    """
    Fetches the raw text of a link.
    """
    async with session.get(url) as response:
        return await response.text()
