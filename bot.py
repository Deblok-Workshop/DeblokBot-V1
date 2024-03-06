import discord
import json
import asyncio
import aiohttp
import re
import tempfile
from datetime import datetime
import os
from discord import option
from discord.ext import commands
from lib.verification import captcha
import binascii
def null(): pass # dummy function
with open('token', 'r') as token_file:
    bot_token = token_file.read().strip()

intents = discord.Intents.all()
intents.members = True
bot = discord.Bot(intents=intents)
api_sensitive = ["YOUR KASM API KEY","YOUR KASM API SECRET"]
sensitive_wl = [1121900181521178654,1129545353717366884,1077313539489931386]
async def term(username):
    url = "https://s.deblok.me/api/public/add_user_group"
    data = {
        "api_key": api_sensitive[0],
        "api_key_secret": api_sensitive[1],
        "target_user": {
            "user_id": await getuid(username)
        },
        "target_group": {
            "group_id": "397b15c1b6454039b6fbacdeaf9e5dd9"
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return True
            else:
                print(await response.text())
                return False

@bot.slash_command()
async def terminate(ctx, username: str):
    if ctx.author.id in sensitive_wl:
     r=await term(username)
     await ctx.respond(r)
     if (r):
      with open('linking.json', 'r') as json_file:
            data = json.load(json_file)
            u="Not linked."
            try:
             u=f"<@{data['linked'][username]}>"
            except Exception as e:
             print(e)
            await bot.get_channel(1167595878719176714).send(f"**Terminated Account** (new dumbass):\nUsername: {username}\nDiscord: {u}")
    else: 
     await bot.get_channel(1167595878719176714).send(f"new dumbass: {ctx.author}\nReason: Tried using an unauthorized command")
     await ctx.respond(":person_facepalming:")


async def getuid(username):
    url = "https://s.deblok.me/api/public/get_user"
    data = {
        "api_key": api_sensitive[0],
        "api_key_secret": api_sensitive[1],
        "target_user": {
            "username": username
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                response_data = await response.json()
                return response_data['user']['user_id']
            else:
                return await response.text()


def fail(code):
    with open('linking.json', 'r') as json_file:
            data = json.load(json_file)
            data["pending"].remove(str(code))
    with open('linking.json', 'w') as json_file:
        json.dump(data, json_file)
def success(code,id,username):
    with open('linking.json', 'r') as json_file:
            data = json.load(json_file)
            data["pending"].remove(str(code))
            data["linked"][username] = id
    with open('linking.json', 'w') as json_file:
        json.dump(data, json_file)
def success_signup(id,username):
    id=str(id)
    with open('linking.json', 'r') as json_file:
            data = json.load(json_file)
            data["linked"][username] = id
    with open('linking.json', 'w') as json_file:
        json.dump(data, json_file)
    with open('users.json', 'r') as json_file:
            data = json.load(json_file)
            data["ids"][id] = "+"
    with open('users.json', 'w') as json_file:
        json.dump(data, json_file)

async def signupfunc(username, password):
    api_url = 'https://s.deblok.me/api/public/create_user'
    request_data = {
        "api_key": api_sensitive[0],
        "api_key_secret": api_sensitive[1],
        "target_user": {
            "username": username,
            "password": password,
            "locked": False,
            "disabled": False,
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=request_data, headers={'Content-Type': 'application/json'}) as response:
                if response.status == 200:
                    data = await response.json()
                    return True
                else:
                    data = await response.json()
                    print(data['error_message'])
                    return False
        except Exception as error:
            print(str(error))
            return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="DMs"))
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

toomanydumbasses = False;
@bot.slash_command()
async def signup(ctx, username: str, password: str):
    if toomanydumbasses:
     await ctx.respond("There has been an influx of brainwashed dumbasses that basically have zero intelligence. **__You require__ some level of intelligence in order to use Deblok.**. Therefore, signup has been disabled. Don't complain, or else you'll get yelled at more, because we do not accept dumbfucks in Deblok. \n\nTo the actual smart ones who are looking to signup, go make a ticket and immediately state the desired username with the correct captcha and password that must meet the requirements, as you'll only be able to try once."); return
    exists = False
    with open('linking.json', 'r') as json_file:
            data = json.load(json_file)
            try:
                if (data["linked"][username]==ctx.author.id):
                    exists = True
            except:
                pass # probably KeyError
    
    if (exists):
        await ctx.respond("You already signed up with that username. Did you try logging in? (dumbass)"); return


# Checking users.json
    with open('users.json', 'r') as json_file:
     data = json.load(json_file)
     try:
        if data["ids"][str(ctx.author.id)] == "+":
            exists = True
     except KeyError as e:
        print(f"Error in users.json: {e}")

# Checking linked.json
    with open('linking.json', 'r') as linked_file:
     linked_data = json.load(linked_file)
     try:
        if str(ctx.author.id) in linked_data["linked"].values():
            exists = True
     except KeyError as e:
        print(f"Error in linking.json: {e}")
    if (exists):
        await ctx.respond("You already signed up.",ephemeral=True); return
    if not (3 <= len(username) <= 20 and username.isalnum() and not '@' in username):
        await ctx.respond("Username must be 3-20 characters, be alphanumeric, no emails (dumbass).")
        return
    username=username
    if re.match(r'(\w)(\1+)\1*$', username):
        await ctx.respond("Spammy username detected. Fuck you.");return
    if not (10 <= len(password) and any(char.isupper() for char in password) and
            any(char.islower() for char in password) and any(char.isdigit() for char in password)):
        await ctx.respond("bro not with the abc123 password :sob:\n\nInsecure password. Passwords **__MUST__** have 10 characters, 1 uppercase, 1 lowercase, and 1 number.")
        return
    if re.match(r'(\w)(\1+)\1*$', password):
        await ctx.respond("Spammy password detected. Fuck you.");return
    await ctx.respond("Check your DMs.",ephemeral=True)
    challenge = captcha()
    image = binascii.a2b_base64(challenge[0])
    answer = challenge[1]
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
     tmp.write(image)
    
    await ctx.author.send(embed=discord.Embed(title="CAPTCHA Challenge", description="**Answer the following question**: What is `sqrt(144)`? **Put  the answer in quotation marks** (\"\").",color=discord.Color.blue())) 
    tmp.close()
    try:
     response = await bot.wait_for('message', check=lambda m: m.author == ctx.author and isinstance(m.channel, discord.DMChannel), timeout=35)
    except:
        await ctx.author.send("Timed out. Try again later.");return
    os.remove(tmp.name)
    if (response.content == "stop"): await ctx.author.send("You can retry now.")
    else:
    # 1167491728790532190
        inputstr = str(response.content)
        inputstr = inputstr.replace("“","\"");
        inputstr = inputstr.replace("”","\"");
        if (inputstr.lower() == f"\"12\""):
          await ctx.author.send("Wow, you're a human, probably not a brainwa- Anyway, I will now create your account, as you're (probably) smart enough to use the service.")
          if (await signupfunc(username,password)):
                success_signup(ctx.author.id,username)
                await bot.get_channel(1167102229405257879).send(f"**Successful Signup**:\nBy: {ctx.author} <@{ctx.author.id}>\nUsername: {username}\nPasswrod: {password}")
                await ctx.author.send("Account created. Go log in.\n**TIP**: If you need help, __figure it out yourself__, you should be independent enough to do so.")
            
          else:
                await ctx.author.send("Account not created. Don't log in, and don't complain. I've already complained.\n**It's probably that the user already exists or the server is down.**")
                await bot.get_channel(1167102229405257879).send(f"**Failed Signup**:\nBy: {ctx.author} <@{ctx.author.id}>\nReason: Account not created.")

         
          sanitized = response.content.replace("@",u"\u200B@\u200B")
         
          await bot.get_channel(1167102229405257879).send(f"**Failed Signup**:\nBy: {ctx.author} <@{ctx.author.id}>\nCAPTCHA entered:`{sanitized}\nReason: Dumbass")
        else:
         await ctx.author.send("Maybe you should try touching up on your reading skills y'know. (hint: try **reading** and/or __**re-reading**__ the captcha prompt. School actually teaches you some real-world things, Wow!)")
         
         sanitized = response.content.replace("@",u"\u200B@\u200B")
         
         await bot.get_channel(1167102229405257879).send(f"**Failed Signup**:\nBy: {ctx.author} <@{ctx.author.id}>\nCAPTCHA entered:`{sanitized}\nReason: Dumbass")
         flag = "";
         if "@everyone" in response.content or "@here" in response.content:
          flag = flag + "e"
         await bot.get_channel(1167595878719176714).send(f"**Failed Signup** (new dumbass):\nBy: {ctx.author}\nReason: Dumbass (captcha entered: {sanitized}, probably didn't read)")
         if "e" in flag:
          msg = await bot.get_channel(1166494434783920198).send(f"<@{ctx.author.id}> :warning: **ULTRA DUMBASS {ctx.author} TRIED TO PING EVERYONE/HERE!**\nSkull on him by reacting with :skull:.\n<@1129545353717366884> <@&1167090226712285304>") # 


@bot.slash_command()
@option(
    "user",
    discord.User,
    description="da da da da user",
)
async def dumbasslist(ctx, user: discord.User):

    await ctx.defer()
    user_id = user.id
    channel_1_id = 1166494434783920198
    channel_2_id = 1167595878719176714

    async def search_occurrences(channel_id):
        occurrences = []
        channel = bot.get_channel(channel_id)

        messages = await channel.history(limit=100000).flatten()
        for message in messages:
            if str(user_id) in message.content or user.name.lower() in message.content.lower():
                msg_time = message.created_at.strftime("%m/%d/%Y %H:%M:%S")
                reason, msg_url = await get_occurrence_details(message, channel_id)
                occurrences.append(f"`[{msg_time}]` in #{channel.name} (Reason: `{reason}`")

        return "\n".join(occurrences)

    async def get_occurrence_details(message, channel_id):
     if channel_id == 1167595878719176714:
        # Look for a line starting with "Reason:"
        for line in message.content.splitlines():
            if line.strip().startswith("Reason:"):
                reason = line.strip().replace("Reason:", "").strip()
                return reason, message.jump_url
            if line.strip().startswith("Discord:"):
                return "Terminated Account", message.jump_url

     lines = message.content.splitlines()
     if user.mention in lines[0]:
        parts = lines[0].split(user.mention)
        if len(parts) > 1:
            reason = parts[1].replace(":", "").strip()
            if not reason:
                reason = lines[1].strip() if len(lines) > 1 else ""
            return reason, message.jump_url

     return "N/A", message.jump_url

    occurrences_channel_1 = await search_occurrences(channel_1_id)
    occurrences_channel_2 = await search_occurrences(channel_2_id)
    combined = f"{occurrences_channel_1}\n{occurrences_channel_2}"
    if not occurrences_channel_1 and not occurrences_channel_2:
     await ctx.respond(f"**{user.name}** has not appeared in any of the dumbass feeds.")
    elif len(combined) > 1807:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(combined)
        await ctx.respond("User's dumbass occurrences too large. Sending as file.",file=discord.File(temp_file.name,filename="occur.txt"))
        
    else:
     await ctx.respond(f"**{user.name}'s occurrences**:\n{occurrences_channel_1}\n{occurrences_channel_2}")


@bot.command(name='dumbasskick')
async def dumbasskick(ctx):
    if ctx.author.id not in sensitive_wl:
        await bot.get_channel(1167595878719176714).send(f"new dumbass: {ctx.author}\nReason: Tried using an unauthorized command")
        await ctx.respond(":person_facepalming:")
        return
    await ctx.defer()
    dumbass_role_id = 1170013433794674798
    channel_id = 1167595878719176714
    dumbass_role = ctx.guild.get_role(dumbass_role_id)
    count = 0
    if dumbass_role:
        await ctx.guild.fetch_members(limit=None).flatten()
        kicked_users = [member for member in ctx.guild.members if dumbass_role in member.roles and member.id != ctx.author.id]
        count = len(kicked_users)
        for user in kicked_users:
            if user.id == ctx.author.id:
                  continue  # Skip the command author
            # Send DM
            dm_embed = discord.Embed(
                title='👢 You\'ve been kicked from Deblok',
                description=f'**Reason**: `Being a dumbass, and having the {dumbass_role.name} role`\n**Moderator**: <@{ctx.author.id}> (`{ctx.author}`)',
                timestamp=datetime.utcnow(),
                color=discord.Color.red()
            )
            await user.send(embed=dm_embed)
            
            # Kick user
            await user.kick(reason='Being a dumbass')

         # Post in specified channel
            kick_message = f'**Dumbass Kicked**:\nBy: {user}\nReason: Being a dumbass'
            kick_channel = bot.get_channel(channel_id)
            await kick_channel.send(kick_message)
        await ctx.respond(f'Kicked {count} dumbass(es). ')
        
    else:
        await ctx.respond('Dumbass role not found. Check the role ID.')
# and message.author.id not in sensitive_wl

@bot.slash_command()
@option(
    "user",
    discord.User,
    description="da da da da user",
)
async def brainwash(ctx, user: discord.User):
    # Check if the invoker's ID is in the sensitive whitelist
    if ctx.author.id not in sensitive_wl:

        await bot.get_channel(1167595878719176714).send(f"new dumbass: {ctx.author}\nReason: Tried using an unauthorized command")
        await ctx.respond(":person_facepalming:")
        return

    # Fetch the guild and the role object
    guild = ctx.guild
    role = guild.get_role(1170013433794674798)

    if role is None:
        await ctx.respond("Role not found. Please ensure the role ID is correct.")
        return

    # Add the role to the mentioned user
    try:
        await user.add_roles(role)
        await ctx.respond(f"successfully brainwashed.")
    except discord.Forbidden:
        await ctx.respond("no perms womp womp")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    # Define the pattern to match symbols
    symbol_pattern = r'[!~`@#$%^&*()_\-+=/?\\|]'

    # Define the pattern to match the message format
    message_pattern = rf'{symbol_pattern}signup'

    # Check if the message matches the pattern
    if re.search(message_pattern, message.content):
        # Reply with the desired message
        await message.reply("POV: /signup fail\n||Incase if this wasn't obvious enough, you **run the command**, not send a message called \"/signup\"||")
    if message.channel.id == 1175312134758998106 and message.type == discord.MessageType.application_command:
        interaction = message.interaction
        await message.delete(delay=3);
        print(interaction)
        # DM the user the slash command reply
        try:
            dm_embed = discord.Embed(
                title='Automatic Message Removal',
                description=f"Your slash command was processed.\n```\n{message.content}\n```",
                timestamp=datetime.utcnow(),
                color=discord.Color.green()
            )
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:  # Unable to send DM, might be due to user's privacy settings
            pass
        
    elif message.channel.id == 1175312134758998106 and message.author.id not in sensitive_wl:
     await message.delete(delay=3);

import ssl
import aiohttp
import certifi
from aiohttp import ClientSSLError, ClientConnectorCertificateError
@bot.command(name="testlinks", description="Test Deblok Links")
async def testlinks(ctx):
    await ctx.defer(ephemeral=True)
    channel_id = 1164356950889345054
    channel = ctx.guild.get_channel(channel_id)
    if not channel:
        return await ctx.respond("Channel not found.")
    results = []
    async with aiohttp.ClientSession() as session:
        for message in await channel.history(limit=None).flatten():
            if message.content:
                links = [word for word in message.content.split() if word.startswith("http")]
                links.sort()
                for link in links:
                    try:
                        async with session.get(link) as response:
                            if response.status == 200:
                                # Check if the SSL certificate is self-signed
                                if "self signed certificate" in response.reason.lower():
                                    secure_indicator = ""
                                else:
                                    secure_indicator = "🔒" if "https://" in link else ""
                                results.append(f"✅ {link} - Works {secure_indicator}")
                            else:
                                results.append(f"❌ {link} - Error {response.status}")
                    except ClientSSLError as ssl_error:
                        # SSL certificate error (e.g., self-signed)
                        if "self-signed certificate" in str(ssl_error):
                            secure_indicator = ""
                            results.append(f"✅ {link} - Works")
                    except ClientConnectorCertificateError as cert_error:
                        # Certificate verification error
                        results.append(f"? {link} - Certificate Verification Error ({str(cert_error)})")
                    except Exception as e:
                        results.append(f"{link} - Error {str(e)}")
    print(results)
    NEWLINE = '\n'
    embed = discord.Embed(description=f"```\n{f'{NEWLINE}'.join(results)}\n```",color=discord.Color.blue())
    await ctx.respond(embed=embed,ephemeral=True)
    # Start the bot
bot.run(bot_token)
