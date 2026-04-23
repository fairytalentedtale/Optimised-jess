"""Spawn rate command cog for Pokemon bot"""
import csv
import io
import discord
import aiohttp
from discord.ext import commands
from typing import Optional, Dict
from utils import find_pokemon_by_name_flexible, load_pokemon_data, normalize_pokemon_name

SPAWN_RATE_CSV_URL = (
    "https://gist.github.com/WitherredAway/1bc525b05f4cd52555a2a18c331e0cf9"
    "/raw/46e8b05f6e6db482a7ede98cf25948c7546e01f2/pokemon_chances.csv"
)

# Module-level cache so we only fetch once per bot session
_spawn_rate_cache: Optional[Dict[str, dict]] = None


async def fetch_spawn_rates() -> Dict[str, dict]:
    """
    Fetch and cache the spawn-rate CSV from the gist.
    Returns a dict keyed by lowercased Pokemon name:
        {
            "geodude": {"dex": "74", "name": "Geodude", "chance": "1/225", "chance_pct": "0.4449%"},
            ...
        }
    """
    global _spawn_rate_cache
    if _spawn_rate_cache is not None:
        return _spawn_rate_cache

    async with aiohttp.ClientSession() as session:
        async with session.get(SPAWN_RATE_CSV_URL) as response:
            response.raise_for_status()
            text = await response.text(encoding="utf-8")

    reader = csv.DictReader(io.StringIO(text))
    data: Dict[str, dict] = {}
    for row in reader:
        raw_name = row.get("Pokemon", "").strip()
        if not raw_name:
            continue
        key = normalize_pokemon_name(raw_name).lower()
        data[key] = {
            "dex": row.get("Dex", "").strip(),
            "name": raw_name,
            "chance": row.get("Chance", "").strip(),
            "chance_pct": row.get("Chance percentage", "").strip(),
        }

    _spawn_rate_cache = data
    return data


def find_spawn_rate(search_name: str, spawn_data: Dict[str, dict]) -> Optional[dict]:
    """
    Look up spawn data for a Pokemon name.
    Tries exact normalized match first, then falls back to checking
    whether the search term is a substring of any key (useful for
    accented / alternate-language names resolved via utils).
    """
    normalized = normalize_pokemon_name(search_name).lower()
    return spawn_data.get(normalized)


class SpawnRate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pokemon_data = load_pokemon_data()

    @commands.command(name="spawnrate", aliases=["sr"])
    async def spawnrate(self, ctx: commands.Context, *, pokemon_name: str = None):
        """
        Show the spawn rate for a Pokemon.

        Usage:
            p!spawnrate geodude
            p!sr Flabébé
            p!sr (Japanese/other language name)
        """
        if not pokemon_name:
            await ctx.send(
                "Please provide a Pokemon name. Example: `p!sr geodude`"
            )
            return

        async with ctx.typing():
            # --- Resolve the canonical English name via utils ---
            matched_pokemon = find_pokemon_by_name_flexible(
                pokemon_name, self.pokemon_data
            )

            if matched_pokemon:
                # Use the canonical English name stored in pokemondata.json
                canonical_name = matched_pokemon["name"]
            else:
                # Fallback: just use what the user typed (normalized)
                canonical_name = pokemon_name.strip()

            # --- Fetch (or use cached) spawn data ---
            try:
                spawn_data = await fetch_spawn_rates()
            except Exception as e:
                await ctx.send(
                    f"❌ Failed to fetch spawn rate data: `{e}`\nPlease try again later."
                )
                return

            # --- Look up by canonical name ---
            entry = find_spawn_rate(canonical_name, spawn_data)

            # If not found by canonical name, try the original user input as well
            if entry is None and canonical_name.lower() != pokemon_name.strip().lower():
                entry = find_spawn_rate(pokemon_name.strip(), spawn_data)

            if entry is None:
                await ctx.send(
                    f"❌ No spawn rate data found for **{canonical_name}**. "
                    "It may not spawn in the wild."
                )
                return

            # --- Build the embed ---
            dex_num = entry["dex"]
            display_name = entry["name"]
            chance = entry["chance"]
            chance_pct = entry["chance_pct"]

            embed = discord.Embed(
                title=f"Spawn Rate — {display_name}",
                color=discord.Color.green(),
            )
            embed.add_field(name="Pokédex #", value=f"#{dex_num}", inline=True)
            embed.add_field(name="Spawn Chance", value=chance, inline=True)
            embed.add_field(name="Percentage", value=chance_pct, inline=True)

            # Show the searched name in footer if it differs (e.g. alt-language input)
            if pokemon_name.strip().lower() != display_name.lower():
                embed.set_footer(text=f'Searched: "{pokemon_name.strip()}"')

            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SpawnRate(bot))
