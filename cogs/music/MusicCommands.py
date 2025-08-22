import discord
from discord.ext import commands
import os
import yt_dlp
import traceback
import asyncio

AIRole = int(os.getenv("AIRole"))

SONGS_DIR = os.path.join(os.path.dirname(__file__), "songs")
os.makedirs(SONGS_DIR, exist_ok=True)

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    def get_tracks(self):
        tracks = []
        for file in os.listdir(SONGS_DIR):
            if file.endswith(".mp3"):
                try:
                    number, name_ext = file.split("_", 1)
                    name = os.path.splitext(name_ext)[0]
                    tracks.append((int(number), name, os.path.join(SONGS_DIR, file)))
                except ValueError:
                    continue
        return sorted(tracks, key=lambda x: x[0])

    @commands.command(name="sing", help="Play a track from the library", usage="sq!sing {track number}")
    async def sing(self, ctx: commands.Context, track_number: int):
        tracks = self.get_tracks()
        track = next((t for t in tracks if t[0] == track_number), None)

        if not track:
            await ctx.send("That is not a valid track, use `!singlist` for the available tracks.")
            return

        track_number, track_name, file_path = track

        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel!")
            return

        channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if vc is None:
            vc = await channel.connect()
            self.voice_clients[ctx.guild.id] = vc
        elif vc.channel != channel:
            await vc.move_to(channel)

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(file_path))

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track_name}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Enjoy the music!")

        await ctx.send(embed=embed)

        async def auto_disconnect(vc, timeout=60):
            await asyncio.sleep(timeout)
            if vc.is_connected() and not vc.is_playing():
                await vc.disconnect()
                self.voice_clients.pop(ctx.guild.id, None)

        if hasattr(vc, "disconnect_task") and not vc.disconnect_task.done():
            vc.disconnect_task.cancel()

        vc.disconnect_task = self.bot.loop.create_task(auto_disconnect(vc))

    @commands.command(name="singlist", help="List all of the tracks", usage="!singlist")
    async def singlist(self, ctx: commands.Context):
        tracks = self.get_tracks()
        if not tracks:
            await ctx.send("No tracks could be found in the library.")
            return

        items_per_page = 10
        total_pages = (len(tracks) + items_per_page - 1) // items_per_page

        def generate_embed(page_num):
            start_idx = (page_num - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_tracks = tracks[start_idx:end_idx]
            track_list = [f"**{t[0]}** - `{t[1]}`" for t in page_tracks]
            embed = discord.Embed(title="Track List", description="\n".join(track_list), color=discord.Color.blue())
            embed.set_footer(text=f"Page {page_num}/{total_pages}")
            return embed

        page_num = 1
        embed = generate_embed(page_num)
        message = await ctx.send(embed=embed)

        buttons = ["<:Left:1286702311661375519>", "<:Right:1286702326274592788>"]
        for button in buttons:
            await message.add_reaction(button)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in buttons and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)

                if str(reaction.emoji) == "<:Left:1286702311661375519>" and page_num > 1:
                    page_num -= 1
                elif str(reaction.emoji) == "<:Right:1286702326274592788>" and page_num < total_pages:
                    page_num += 1
                else:
                    continue

                embed = generate_embed(page_num)
                await message.edit(embed=embed)
                await message.remove_reaction(str(reaction.emoji), user)

            except asyncio.TimeoutError:
                break

    @commands.command(name="singadd", help="Add and download a new song", usage="sq!singadd <name> <YouTube URL>")
    @commands.has_role(AIRole)
    async def singadd(self, ctx: commands.Context, name: str, url: str):
        tracks = self.get_tracks()
        next_number = tracks[-1][0] + 1 if tracks else 1

        filename = f"{next_number}_{name}"
        file_path = os.path.join(SONGS_DIR, filename)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_path,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        embed = discord.Embed(
            title="🎵 New Song Added!",
            description=f"**{name}** has been added and downloaded.",
            timestamp=ctx.message.created_at,
            color=discord.Color.green()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(name="Track Number", value=next_number, inline=True)
        embed.add_field(name="Added by", value=ctx.author.display_name, inline=True)
        embed.set_footer(text=ctx.guild.name if ctx.guild else "")

        await ctx.send(embed=embed)

    @commands.command(name="singremove", help="Remove a song from the library", usage="sq!singremove <track number>")
    @commands.has_role(AIRole)
    async def singremove(self, ctx: commands.Context, track_number: int):
        tracks = self.get_tracks()
        track = next((t for t in tracks if t[0] == track_number), None)

        if not track:
            await ctx.send("Such track number does not exist.")
            return

        _, track_name, file_path = track

        os.remove(file_path)
        await ctx.send(f"✅ Removed track **{track_name}** successfully.")

        embed = discord.Embed(
            title="🗑️ Song Removed",
            description=f"**{track_name}** has been removed.",
            timestamp=ctx.message.created_at,
            color=discord.Color.red()
        )
        embed.add_field(name="Track Number", value=track_number, inline=True)
        embed.add_field(name="Removed by", value=ctx.author.display_name, inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))
