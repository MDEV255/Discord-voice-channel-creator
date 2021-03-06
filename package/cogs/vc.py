import re
import discord
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands.errors import BotMissingPermissions, CommandNotFound
from package.function import current_time
from package.data import databaseDeo as db


class Vc(commands.Cog, name="Voice Channel"):
    def __init__(self, bot):
        self.bot = bot

    # event
    @commands.Cog.listener()
    async def on_ready(self):
        print("Voice Channel cog is ready")

    # Commands
    @commands.command(brief='Create a voice channel',
                      description='Create a voice channel that only certain role can speak')
    @commands.bot_has_permissions(read_messages=True,
                                  manage_messages=True,
                                  manage_channels=True,
                                  send_messages=True,
                                  view_channel=True,
                                  embed_links=True)
    async def create(self, ctx):
        i = await create_voice(ctx)
        if i:
            msg = i.get("msg")
            new_channel = i.get("new_channel")
            embed_var = discord.Embed(title="", description=f"""
                                    Vcc common
                                    Name: {i.get("channel_name")}
                                    Speaker: {i.get("mention_name")}
                                    Creator: {msg.author.mention}
    
                                    Started: {current_time()}
                                    """, color=0x0ae0fc)
            response_msg = await msg.channel.send(embed=embed_var)

            db.save_voice_channel(new_channel.id, msg.channel.id, response_msg.id)

            print(f"{current_time()} VC: a channel is created (created: 1, deleted: 0)")
            save(self, 1, 0)

    @commands.command(brief='Create a private voice channel',
                      description='Create a private voice channel that only certain role can speak and hear')
    @commands.bot_has_permissions(read_messages=True,
                                  manage_messages=True,
                                  manage_channels=True,
                                  send_messages=True,
                                  view_channel=True,
                                  embed_links=True)
    async def private(self, ctx):
        msg = ctx.message
        mention = msg.role_mentions + msg.mentions
        if mention:
            i = await create_voice(ctx)
            j = await create_text(ctx)
            if i and j:
                msg = i.get("msg")
                new_channel = i.get("new_channel")
                text_channel = j.get("new_channel")

                # set permission
                for q in i.get("mention"):
                    await new_channel.set_permissions(q, connect=True)
                    await text_channel.set_permissions(q, read_messages=True)
                await new_channel.set_permissions(ctx.guild.roles[0], connect=False)
                await text_channel.set_permissions(ctx.guild.roles[0], read_messages=False)

                embed_var = discord.Embed(title="", description=f"""
                                            Vcc private
                                            Name: {i.get("channel_name")}
                                            Speaker + Listener: {i.get("mention_name")}
                                            Creator: {msg.author.mention}
        
                                            Started: {current_time()}
                                            """, color=0x178fff)
                response_msg = await msg.channel.send(embed=embed_var)

                db.save_voice_channel(new_channel.id, msg.channel.id, response_msg.id)

                print(f"{current_time()} VC: a private channel is created (created: 1, deleted: 0)")
                save(self, 1, 0)
        else:
            embed_var = discord.Embed(title="", description=f"""
                                    {msg.author.mention}
                                    You need to ping a user to create a private channel, use "vc create" instead
                                    """, color=0xff0f0f)
            await msg.channel.send(embed=embed_var)
            return

    @commands.command(brief='Create a voice and text channel',
                      description='Create a voice channel that only certain role can speak')
    @commands.bot_has_permissions(read_messages=True,
                                  manage_messages=True,
                                  manage_channels=True,
                                  send_messages=True,
                                  view_channel=True,
                                  embed_links=True)
    async def text(self, ctx):
        i = await create_voice(ctx)
        q = await create_text(ctx)
        if i and q:
            msg = i.get("msg")
            new_channel = i.get("new_channel")
            embed_var = discord.Embed(title="", description=f"""Vcc text and voice
                                                                Name: {i.get("channel_name")}
                                                                Speaker: {i.get("mention_name")}
                                                                Creator: {msg.author.mention}
                                    
                                                                Started: {current_time()}
                                                                """, color=0x0ae0fc)
            response_msg = await msg.channel.send(embed=embed_var)
            db.save_voice_channel(new_channel.id, msg.channel.id, response_msg.id)
            db.save_text_channel(new_channel.id, q.get("new_channel").id)
            print(f"{current_time()} VC: a channel is created (created: 1, deleted: 0)")
            save(self, 1, 0)

    @commands.Cog.listener()
    async def on_voice_state_update(self, client, before, after):
        if before.channel is not None:
            result = db.get_channel(before.channel.id)
            if result:
                if not before.channel.members:
                    await before.channel.delete()

                    # delete text channel
                    tx_channel_id = result.get("tx_channel_id")
                    if tx_channel_id:
                        tx_channel = self.bot.get_channel(tx_channel_id)
                        await tx_channel.delete()

                    # edit message
                    msg_channel = self.bot.get_channel(result.get("msg_channel_id"))
                    response_msg = await msg_channel.fetch_message(result.get("response_msg_id"))
                    embeds = response_msg.embeds
                    if embeds:
                        description = embeds[0].description

                        embed_var = discord.Embed(title="", description=f"""
                        (deleted) {description} 
                        Ended: {current_time()}
                        """, color=0x129eb0)
                        await response_msg.edit(embed=embed_var)

                    db.delete_channel(before.channel.id)

                    print(f"{current_time()} VC: a channel is deleted (created: 0, deleted: 1)")
                    save(self, 0, 1)


async def create_voice(ctx):
    msg = ctx.message
    mention = msg.role_mentions + msg.mentions
    mention_list = []

    if mention:  # @role
        if check_in_role(msg.author.id, msg.role_mentions):
            # create channel
            channel_name = await get_channel_name(msg)
            new_channel = await msg.channel.category.create_voice_channel(channel_name)

            # setting permission
            for i in mention:
                await new_channel.set_permissions(i, speak=True)
                mention_list.append(i.mention)
            mention_name = ", ".join(mention_list)

            await new_channel.set_permissions(ctx.guild.roles[0], speak=False)
        else:  # not member of @role
            embed_var = discord.Embed(title="", description=f"""
                        {msg.author.mention}
                        You are not a member of that role,
                        Please ping another role or people
                        """, color=0xff0f0f)
            await msg.channel.send(embed=embed_var)
            return
    else:  # only text
        channel_name = await get_channel_name(msg)
        if channel_name == "":
            channel_name = "created by Vcc"
        new_channel = await msg.channel.category.create_voice_channel(channel_name)
        mention_name = "everyone"

    mention.append(msg.author)
    if ctx.author.voice:
        await ctx.author.move_to(new_channel)

    return {"msg": msg, "new_channel": new_channel, "mention": mention, "channel_name": channel_name,
            "mention_name": mention_name}


async def create_text(ctx):
    msg = ctx.message
    mention = msg.role_mentions + msg.mentions

    if mention:  # @role
        if check_in_role(msg.author.id, msg.role_mentions):
            # create channel
            channel_name = await get_channel_name(msg)
            new_channel = await msg.channel.category.create_text_channel(channel_name)

            # setting permission
            for i in mention:
                await new_channel.set_permissions(i, send_messages=True)

            await new_channel.set_permissions(ctx.guild.roles[0], send_messages=False)
        else:  # not member of @role
            embed_var = discord.Embed(title="", description=f"""
                        {msg.author.mention}
                        You are not a member of that role,
                        Please ping another role or people
                        """, color=0xff0f0f)
            await msg.channel.send(embed=embed_var)
            return
    else:  # only text
        channel_name = await get_channel_name(msg)
        if channel_name == "":
            channel_name = "created by Vcc"
        new_channel = await msg.channel.category.create_text_channel(channel_name)

    return {"new_channel": new_channel}


async def get_channel_name(msg):
    channel_name = " ".join(msg.clean_content.split(" ")[2:])
    if len(channel_name) > 100:
        embed_var = discord.Embed(title="", description=f"""
                                            {msg.author.mention}
                                            Channel name is too long (Max: 100 characters)
                                            """, color=0xff0f0f)
        await msg.channel.send(embed=embed_var)
    return channel_name


def save(self, created, deleted):
    server_count = len(self.bot.guilds)
    db.stats_save(server_count, created, deleted)


def check_in_role(user_id, role):
    role_member = []
    for i in role:
        for q in i.members:
            role_member.append(q.id)

        if user_id not in role_member:
            return False

    return True


def setup(bot):
    bot.add_cog(Vc(bot))
