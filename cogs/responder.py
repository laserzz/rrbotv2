import discord
import asyncio
import aiosqlite
from discord.ext import commands

class Responder(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    rcmd = discord.SlashCommandGroup(name="responder", description="responder commands")

    @rcmd.command(description="sets up responder.")
    @commands.has_permissions(manage_guild=True)
    async def rsetup(self, ctx, trigger_msg, response, channel:discord.TextChannel):
        async with self.bot.db.cursor() as cur:
            await cur.execute("INSERT INTO responder (guild, channel, trigger, response) VALUES (?, ?, ?, ?)", (ctx.guild.id, channel.id, trigger_msg, response))
        await self.bot.db.commit()
        await ctx.respond(f"Responder set up in {channel.mention} <3")

    @rcmd.command(description="removes all responders from a channel.")
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, channel:discord.TextChannel):
        async with self.bot.db.cursor() as cur:
            await cur.execute("DELETE FROM responder WHERE channel = ?", (channel.id,))
        await ctx.respond(f"Responder at {channel.mention} deleted <3")

    @discord.Cog.listener()
    async def on_ready(self):
        setattr(self.bot, "db", await aiosqlite.connect("main.sqlite"))
        await asyncio.sleep(1)
        async with self.bot.db.cursor() as cur:
            await cur.execute("CREATE TABLE IF NOT EXISTS responder (guild INTEGER, channel INTEGER, trigger TEXT, response TEXT)")
        await self.bot.db.commit()

    @discord.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.cursor() as cur:
            try:
                await cur.execute(
                    "SELECT guild, channel, trigger, response FROM responder WHERE guild = ? AND channel = ?",
                    (message.guild.id, message.channel.id)
                )
                results = await cur.fetchall()

                if results is None:
                    return

                for res in results:
                    if res[1] == message.channel.id and res[2].lower() == message.content.lower():
                        return await message.channel.send(res[3])
            except: return

def setup(bot):
    bot.add_cog(Responder(bot))