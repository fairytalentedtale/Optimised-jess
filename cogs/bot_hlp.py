"""Help commands"""
import discord
from discord import app_commands
from discord.ext import commands
from config import EMBED_COLOR, BOT_PREFIX

class Help(commands.Cog):
    """Help and information commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h"])
    async def help_command(self, ctx, category: str = None):
        """Show help information

        Categories: collection, category, hunt, settings, prediction, starboard, helpful, incense, captcha, owner, all
        """
        prefix = BOT_PREFIX[0]  # Use first prefix for examples

        # Check if user is owner
        is_owner = await self.bot.is_owner(ctx.author)

        if not category:
            # Main help embed
            embed = discord.Embed(
                title="📚 Poketwo Helper Bot - Help",
                description=f"Use `{prefix}help <category>` for detailed information about a category\nUse `{prefix}help all` to see all commands at once",
                color=EMBED_COLOR
            )

            embed.add_field(
                name="📦 Collection",
                value=f"`{prefix}help collection` - Manage your Pokemon collection",
                inline=False
            )

            embed.add_field(
                name="🗂️ Category",
                value=f"`{prefix}help category` - Bulk collection management with categories",
                inline=False
            )

            embed.add_field(
                name="✨ Shiny Hunt",
                value=f"`{prefix}help hunt` - Set up shiny hunting",
                inline=False
            )

            embed.add_field(
                name="🔷 Type & Region Pings",
                value=f"`{prefix}help pings` - Get pinged by Pokemon type or region",
                inline=False
            )

            embed.add_field(
                name="⚙️ Settings",
                value=f"`{prefix}help settings` - Configure bot settings",
                inline=False
            )

            embed.add_field(
                name="🔮 Prediction",
                value=f"`{prefix}help prediction` - Manual Pokemon prediction",
                inline=False
            )

            embed.add_field(
                name="⭐ Starboard",
                value=f"`{prefix}help starboard` - Configure starboard channels",
                inline=False
            )

            embed.add_field(
                name="🔍 Helpful Commands",
                value=f"`{prefix}help helpful` - Spawn rates, shiny rates & hint solver",
                inline=False
            )

            embed.add_field(
                name="🔥 Incense",
                value=f"`{prefix}help incense` - Manage Poketwo incense sessions",
                inline=False
            )

            embed.add_field(
                name="🔐 Captcha",
                value=f"`{prefix}help captcha` - Captcha alert configuration",
                inline=False
            )

            if is_owner:
                embed.add_field(
                    name="👑 Owner",
                    value=f"`{prefix}help owner` - Bot owner commands",
                    inline=False
                )

            embed.add_field(
                name="ℹ️ About",
                value=f"`{prefix}about` - Bot information and stats",
                inline=False
            )

            embed.add_field(
                name="🏓 Ping",
                value=f"`{prefix}ping` - Check bot latency",
                inline=False
            )

            embed.set_footer(text=f"Bot Prefix: {', '.join(BOT_PREFIX)}")

            await ctx.reply(embed=embed, mention_author=False)
            return

        category = category.lower()

        # Collection category
        if category in ["collection", "cl", "collect"]:
            embed = discord.Embed(
                title="📦 Collection Commands",
                description="Manage your Pokemon collection for this server. Get pinged when Pokemon you collect spawn!",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}cl add <pokemon>`",
                value=(
                    "Add Pokemon to your collection\n"
                    f"**Aliases:** `{prefix}collection add`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}cl add Pikachu`\n"
                    f"• `{prefix}cl add Pikachu, Charizard, Mewtwo`\n"
                    f"• `{prefix}cl add Furfrou all` (adds all Furfrou variants)"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cl remove <pokemon>`",
                value=(
                    "Remove Pokemon from your collection\n"
                    f"**Aliases:** `{prefix}collection remove`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}cl remove Pikachu`\n"
                    f"• `{prefix}cl remove Pikachu, Charizard`\n"
                    f"• `{prefix}cl remove Furfrou all` (removes all Furfrou variants)\n"
                    f"• `{prefix}cl remove all Furfrou` (same as above)"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cl list`",
                value=(
                    "View your collection in a paginated embed with buttons\n"
                    f"**Aliases:** `{prefix}collection list`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cl raw`",
                value=(
                    "View your collection as comma-separated text (sends as .txt file if large)\n"
                    f"**Aliases:** `{prefix}collection raw`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cl clear`",
                value=(
                    "⚠️ Clear your entire collection\n"
                    f"**Aliases:** `{prefix}collection clear`"
                ),
                inline=False
            )

            embed.add_field(
                name="💡 How It Works",
                value=(
                    "• When a Pokemon you collect spawns, you get pinged!\n"
                    "• If you add `Furfrou`, you get pinged for all Furfrou variants\n"
                    "• If you add `Furfrou all`, all variants are explicitly added to your collection"
                ),
                inline=False
            )

        # Category commands
        elif category in ["category", "cat", "categories"]:
            embed = discord.Embed(
                title="🗂️ Category Commands",
                description="Bulk collection management with categories. Admins create categories, users add them to their collection!",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}cat add <categories>`",
                value=(
                    "Add Pokemon from categories to your collection\n"
                    f"**Aliases:** `{prefix}category add`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}cat add Rares`\n"
                    f"• `{prefix}cat add Rares, Regionals, Gigantamax`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cat remove <categories>`",
                value=(
                    "Remove Pokemon from categories from your collection\n"
                    f"**Aliases:** `{prefix}category remove`\n"
                    f"**Example:** `{prefix}cat remove Rares`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cat list`",
                value=(
                    "View all server categories with Pokemon counts\n"
                    f"**Aliases:** `{prefix}category list`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}cat info <name>`",
                value=(
                    "View Pokemon in a specific category (paginated)\n"
                    f"**Aliases:** `{prefix}category info`\n"
                    f"**Example:** `{prefix}cat info Rares`"
                ),
                inline=False
            )

            embed.add_field(
                name="📝 Admin Commands",
                value=(
                    f"`{prefix}cat create <name> <pokemon>` - Create a category\n"
                    f"**Example:** `{prefix}cat create Rares articuno, moltres, zapdos`\n\n"
                    f"`{prefix}cat edit <name> <pokemon>` - Edit a category (replaces all Pokemon)\n"
                    f"**Example:** `{prefix}cat edit Rares marshadow, lugia`\n\n"
                    f"`{prefix}cat addpokemon <name> <pokemon>` - Add Pokemon to an existing category\n"
                    f"**Aliases:** `{prefix}cat addpoke`\n"
                    f"**Example:** `{prefix}cat addpokemon Rares hoopa, marshadow`\n\n"
                    f"`{prefix}cat removepokemon <name> <pokemon>` - Remove specific Pokemon from a category\n"
                    f"**Aliases:** `{prefix}cat removepoke`\n"
                    f"**Example:** `{prefix}cat removepokemon Rares hoopa`\n\n"
                    f"`{prefix}cat delete <name>` - Delete a category\n"
                    f"**Example:** `{prefix}cat delete Rares`"
                ),
                inline=False
            )

            embed.add_field(
                name="💡 How It Works",
                value=(
                    "• Admins create categories with Pokemon lists\n"
                    "• Users can add entire categories to their collection at once\n"
                    "• Supports `all` variants: `furfrou all` or `all furfrou`\n"
                    "• Category names are case-insensitive and can have spaces"
                ),
                inline=False
            )

        # Shiny Hunt category
        elif category in ["hunt", "sh", "shiny"]:
            embed = discord.Embed(
                title="✨ Shiny Hunt Commands",
                description="Set up shiny hunting to get pinged when your target Pokemon spawns!",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}sh`",
                value=(
                    "Check your current shiny hunt\n"
                    f"**Aliases:** `{prefix}hunt`, `{prefix}shinyhunt`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}sh <pokemon>`",
                value=(
                    "Start hunting a Pokemon\n"
                    f"**Aliases:** `{prefix}hunt <pokemon>`, `{prefix}shinyhunt <pokemon>`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}sh Pikachu`\n"
                    f"• `{prefix}sh unown a, unown b, unown c`\n"
                    f"• `{prefix}sh Furfrou all` (hunt all Furfrou variants)"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}sh clear`",
                value=(
                    "Stop hunting (also accepts `none` or `stop`)\n"
                    f"**Aliases:** `{prefix}hunt clear`, `{prefix}shinyhunt clear`"
                ),
                inline=False
            )

            embed.add_field(
                name="💡 Note",
                value="You can hunt one or more Pokemon(if they all belong to same dex) at a time per server!",
                inline=False
            )

        # Settings category
        elif category in ["settings", "setting", "config", "afk"]:
            embed = discord.Embed(
                title="⚙️ Settings Commands",
                description="Configure bot settings for your server and personal preferences",
                color=EMBED_COLOR
            )

            embed.add_field(
                name="👤 User Settings",
                value="",
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}afk`",
                value=(
                    "Toggle pings using interactive buttons — **4 toggles available:**\n"
                    f"**Aliases:** `{prefix}away`\n"
                    "🟢 **Green** = Pings ON  •  🔴 **Red** = Pings OFF\n"
                    "• **ShinyHunt** — shiny hunt pings\n"
                    "• **Collection** — collection pings\n"
                    "• **TypePings** — type-based pings\n"
                    "• **RegionPings** — region-based pings\n"
                    "*AFK status is global across all servers*"
                ),
                inline=False
            )

            embed.add_field(
                name="🛠️ Server Settings",
                value="",
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}server-settings`",
                value=(
                    "View all current server settings\n"
                    f"**Aliases:** `{prefix}ss`, `{prefix}ssettings`, `{prefix}serversettings`\n"
                    "Shows: Rare Role, Regional Role, Best Name, Only-Pings status, Captcha Alert Channel"
                ),
                inline=False
            )

            embed.add_field(
                name="📝 Admin Commands",
                value="",
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}rare-role @role`",
                value=(
                    "Set role to ping for rare Pokemon (Legendary/Mythical/Ultra Beast)\n"
                    f"**Aliases:** `{prefix}rr`, `{prefix}rarerole`\n"
                    f"**Example:** `{prefix}rare-role @Rare Hunters`\n"
                    f"Use `{prefix}rare-role none` to clear"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}regional-role @role`",
                value=(
                    "Set role to ping for regional Pokemon\n"
                    f"**Aliases:** `{prefix}regrole`, `{prefix}regional`, `{prefix}regionrole`\n"
                    f"**Example:** `{prefix}regional-role @Regional`\n"
                    f"Use `{prefix}regional-role none` to clear"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}toggle <feature>`",
                value=(
                    "Toggle server features on/off\n"
                    f"**Examples:**\n"
                    f"• `{prefix}toggle best_name` — Enable/disable the Shortest Name line in predictions\n"
                    f"• `{prefix}toggle only_pings` — Enable/disable only-pings mode\n\n"
                    f"**`only_pings`:** When enabled, predictions are only sent when there are active collectors, hunters, or ping roles. "
                    f"Also accessible via `{prefix}only-pings true/false`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}captcha-channel [#channel]`",
                value=(
                    "Set the channel where users get pinged when Pokétwo asks them to verify\n"
                    f"**Aliases:** `{prefix}captchachannel`, `{prefix}setcaptcha`\n"
                    f"• `{prefix}captcha-channel #alerts` — set the captcha alert channel\n"
                    f"• `{prefix}captcha-channel` (no args) — clear and **disable** captcha alerts\n"
                    "When a captcha is detected the bot pings the user with a **Verify** button linking to their captcha URL.\n"
                    "Same user won't be re-pinged within 5 minutes if another captcha appears"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}clear-pings [@user | user_id]`",
                value=(
                    "Clear all ping data (collections, shiny hunts, type pings, region pings) for this server\n"
                    f"**Aliases:** `{prefix}clearpings`, `{prefix}clearserverpings`, `{prefix}resetpings`\n"
                    "• No argument → clears **all users** in the server (confirm/cancel buttons)\n"
                    "• With @user or user ID → clears only that user\n"
                    "⚠️ Requires server owner, administrator, or bot owner"
                ),
                inline=False
            )

        # Type & Region Pings category
        elif category in ["pings", "ping", "typepings", "regionpings", "tp", "rp"]:
            embed = discord.Embed(
                title="🔷 Type & Region Ping Commands",
                description="Get pinged whenever a Pokemon of a specific type or from a specific region spawns!",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}tp`",
                value=(
                    "Open the interactive **Type Pings** menu with toggle buttons\n"
                    f"**Aliases:** `{prefix}typepings`, `{prefix}typeping`\n"
                    "🟢 Green = enabled  •  ⚫ Grey = disabled\n"
                    "All 18 types available: Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}tp <types>`",
                value=(
                    "Directly toggle one or more types without opening the menu\n"
                    f"**Examples:**\n"
                    f"• `{prefix}tp bug` — toggle Bug\n"
                    f"• `{prefix}tp bug grass fire` — toggle Bug, Grass and Fire at once\n"
                    "If a type was OFF it turns ON, if it was ON it turns OFF"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}rp`",
                value=(
                    "Open the interactive **Region Pings** menu with toggle buttons\n"
                    f"**Aliases:** `{prefix}regionpings`, `{prefix}regionping`\n"
                    "🟢 Green = enabled  •  ⚫ Grey = disabled\n"
                    "All 9 regions available: Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Paldea"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}rp <regions>`",
                value=(
                    "Directly toggle one or more regions without opening the menu\n"
                    f"**Examples:**\n"
                    f"• `{prefix}rp kanto` — toggle Kanto\n"
                    f"• `{prefix}rp kanto johto hoenn` — toggle multiple regions at once"
                ),
                inline=False
            )

            embed.add_field(
                name="🔕 AFK for Type/Region Pings",
                value=(
                    f"Use `{prefix}afk` and click the **TypePings** or **RegionPings** button\n"
                    "to temporarily suppress these pings globally across all servers"
                ),
                inline=False
            )

            embed.add_field(
                name="💡 How It Works",
                value=(
                    "• Type and region settings are **per-server** — set them separately in each server\n"
                    "• When a Pokemon spawns, the bot checks its types/region against your preferences\n"
                    "• You'll be mentioned in the prediction output under **Type Pings** or **Region Pings**\n"
                    "• Uses `data/typeandregions.csv` for accurate type/region data"
                ),
                inline=False
            )

        # Prediction category
        elif category in ["prediction", "predict", "pred"]:
            embed = discord.Embed(
                title="🔮 Prediction Commands",
                description="Manually predict Pokemon from images or view auto-detection info",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}predict <image_url>`",
                value=(
                    "Predict Pokemon from image URL\n"
                    f"**Aliases:** `{prefix}pred`, `{prefix}p`\n"
                    f"**Example:** `{prefix}predict https://...`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}predict` (reply to message)",
                value=(
                    "Reply to a message with an image to predict it\n"
                    f"**Example:** Reply to image with `{prefix}predict`"
                ),
                inline=False
            )

            embed.add_field(
                name="🤖 Auto-Detection",
                value=(
                    "The bot automatically predicts Poketwo spawns and shows:\n"
                    "```\n"
                    "Charizard: 94.21%\n"
                    "Shortest Name: Glurak       ← if enabled\n"
                    "Rare Ping: @role\n"
                    "Regional Pings: @role\n"
                    "Shiny Hunters: @user\n"
                    "Collectors: @user\n"
                    "Type Pings: @user\n"
                    "Region Pings: @user\n"
                    "```"
                ),
                inline=False
            )

            embed.add_field(
                name="📊 Dual Model System",
                value=(
                    "Bot uses two AI models for accuracy:\n"
                    "• **Primary model** (224×224) — runs on every spawn\n"
                    "• **Secondary model** (224×224) — runs in parallel; used when primary confidence < 94%\n"
                    "• If primary ≥ **94%** → primary result is used\n"
                    "• If secondary ≥ **90%** → secondary result is used\n"
                    "• If both are below threshold → primary result is used as fallback\n"
                    "• Some Pokémon always prefer the secondary model result"
                ),
                inline=False
            )

        # Starboard category
        elif category in ["starboard", "star", "log"]:
            embed = discord.Embed(
                title="⭐ Starboard Commands",
                description="Configure automatic logging of rare catches, hatches, and unboxes to dedicated channels",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}starboard-settings`",
                value=(
                    "View current starboard channel configuration"
                ),
                inline=False
            )

            embed.add_field(
                name="📺 Channel Configuration (Admin Only)",
                value="",
                inline=False
            )

            embed.add_field(
                name="Starboard For All",
                value=(
                    f"`{prefix}starboard-all #channel` - All catches, hatches, unboxes\n"
                    f"Use `none` instead of #channel to remove"
                ),
                inline=False
            )

            embed.add_field(
                name="General Channels",
                value=(
                    f"`{prefix}starboard-catch #channel` - All catches\n"
                    f"`{prefix}starboard-egg #channel` - All egg hatches\n"
                    f"`{prefix}starboard-unbox #channel` - All box openings\n"
                    f"Use `none` instead of #channel to remove"
                ),
                inline=False
            )

            embed.add_field(
                name="Specific Criteria Channels",
                value=(
                    f"`{prefix}starboard-shiny #channel` - Shiny catches/hatches/unboxes\n"
                    f"`{prefix}starboard-gigantamax #channel` - Gigantamax catches/hatches/unboxes\n"
                    f"`{prefix}starboard-highiv #channel` - High IV (≥90%)\n"
                    f"`{prefix}starboard-lowiv #channel` - Low IV (≤10%)\n"
                    f"`{prefix}starboard-missingno #channel` - MissingNo catches\n"
                    f"`{prefix}starboard-milestone #channel` - Milestone catches (1000th etc)\n"
                    f"Use `none` instead of #channel to remove"
                ),
                inline=False
            )

            embed.add_field(
                name="🔍 Manual Checking (Admin Only)",
                value=(
                    f"`{prefix}catchcheck` - Manually check a catch message\n"
                    f"`{prefix}eggcheck` - Manually check an egg hatch\n"
                    f"`{prefix}unboxcheck` - Manually check a box opening\n"
                    "Use by replying to a message or providing message ID"
                ),
                inline=False
            )

            embed.add_field(
                name="📋 What Gets Logged?",
                value=(
                    "• **Shiny** catches/hatches/unboxes\n"
                    "• **Gigantamax** catches/hatches/unboxes\n"
                    "• **High IV** (≥90%) or **Low IV** (≤10%)\n"
                    "• **MissingNo** catches\n"
                    "• **Combinations** (e.g., Shiny + High IV)\n\n"
                    "Note: A Pokemon meeting multiple criteria will be sent to multiple channels!"
                ),
                inline=False
            )

        # Helpful commands
        elif category in ["helpful", "util", "utils", "tools"]:
            embed = discord.Embed(
                title="🔍 Helpful Commands",
                description="Useful utility commands for Pokétwo players",
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}spawnrate <pokemon>` / `{prefix}sr <pokemon>`",
                value=(
                    "Show the wild spawn rate for a Pokémon\n"
                    f"**Aliases:** `{prefix}sr`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}sr geodude`\n"
                    f"• `{prefix}sr Garchomp`\n"
                    "Also available as a slash command: `/spawnrate`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}shinyrate [chain] [target%]` / `{prefix}shr`",
                value=(
                    "Show per-encounter shiny rates at a given chain, or calculate what chain you need to hit a target chance — both with and without Shiny Charm\n"
                    f"**Aliases:** `{prefix}shr`\n"
                    f"**Examples:**\n"
                    f"• `{prefix}shr` — show usage + rates at chain 0\n"
                    f"• `{prefix}shr 50` — shiny rates at chain 50\n"
                    f"• `{prefix}shr 89%` — chain needed for 89% per-encounter chance\n"
                    f"• `{prefix}shr 50 89%` — both at once\n"
                    "Also available as a slash command: `/shinyrate`"
                ),
                inline=False
            )

            embed.add_field(
                name="🔎 Hint Solver (Automatic)",
                value=(
                    "When Pokétwo sends a hint message, the bot automatically replies with the matching Pokémon name(s)\n"
                    "• Supports hints in **all languages** (English, Japanese, etc.)\n"
                    "• If multiple Pokémon match, all candidates are listed\n"
                    "• No command needed — just wait for Pokétwo's hint!"
                ),
                inline=False
            )

        # Owner commands
        elif category in ["owner", "admin", "botowner"]:
            if not is_owner:
                await ctx.reply("❌ This category is only available to the bot owner.", mention_author=False)
                return

            embed = discord.Embed(
                title="👑 Owner Commands",
                description="Bot owner only commands for global settings",
                color=0xFFD700  # Gold color
            )

            embed.add_field(
                name=f"`{prefix}loadmodel`",
                value=(
                    "Download (if needed) and load the AI prediction models into RAM\n"
                    f"**Aliases:** `{prefix}lm`, `{prefix}modelload`, `{prefix}startmodel`\n"
                    "Run this before starting an incense session\n"
                    "⚠️ Increases memory usage significantly"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}unloadmodel`",
                value=(
                    "Unload the AI prediction models from RAM\n"
                    f"**Aliases:** `{prefix}um`, `{prefix}modelunload`, `{prefix}stopmodel`\n"
                    "Run this after finishing an incense session to free memory"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}reloadmodel`",
                value=(
                    "Force re-download the latest models from GitHub and reload into RAM\n"
                    f"**Aliases:** `{prefix}rm`, `{prefix}modelreload`, `{prefix}refreshmodel`\n"
                    "Use this when model files have been updated on GitHub"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}modelstatus`",
                value=(
                    "Show current model load state, RAM usage, and prediction stats\n"
                    f"**Aliases:** `{prefix}ms`, `{prefix}modelinfo`, `{prefix}modelsinfo`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}reloadsr`",
                value=(
                    "Force-reload the spawn rate data from the remote CSV\n"
                    "Useful after the spawn rate sheet has been updated"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}set-low-prediction-channel #channel`",
                value=(
                    "Set global channel for low confidence predictions (< 90%)\n"
                    f"**Aliases:** `{prefix}setlowpred`, `{prefix}lowpredchannel`\n"
                    f"**Example:** `{prefix}set-low-prediction-channel #low-predictions`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}set-secondary-model-channel #channel`",
                value=(
                    "Set global channel for secondary model logs\n"
                    f"**Aliases:** `{prefix}setsecondary`, `{prefix}secondarychannel`\n"
                    f"**Example:** `{prefix}set-secondary-model-channel #secondary-logs`\n"
                    "Logs when the secondary model is used for predictions"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}starboard-set-global-catch #channel`",
                value=(
                    "Set global catch starboard channel (across all servers)\n"
                    f"**Aliases:** `{prefix}sbsetglobalcatch`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}starboard-set-global-egg #channel`",
                value=(
                    "Set global egg starboard channel (across all servers)\n"
                    f"**Aliases:** `{prefix}sbsetglobalegg`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}starboard-set-global-unbox #channel`",
                value=(
                    "Set global unbox starboard channel (across all servers)\n"
                    f"**Aliases:** `{prefix}sbsetglobalunbox`"
                ),
                inline=False
            )

        # Incense commands
        elif category in ["incense", "inc", "incenses"]:
            embed = discord.Embed(
                title="🔥 Incense Commands",
                description=(
                    "Automatically restricts Poketwo the moment an Incense is purchased "
                    "in a monitored category channel — so your spawns stay exclusive."
                ),
                color=EMBED_COLOR
            )

            embed.add_field(
                name="⚙️ Setup  *(Manage Server)*",
                value=(
                    f"`{prefix}inc toggle` — Enable/disable the incense watcher\n"
                    f"`{prefix}inc cat add SPAWN1 SPAWN2` — Add multiple categories to monitor\n"
                    f"`{prefix}inc cat add \"Incense 1\" \"Incense 2\"` — Names with spaces use quotes\n"
                    f"`{prefix}inc cat remove <name>` — Stop monitoring a category\n"
                    f"`{prefix}inc cat list` — View all monitored categories & channel counts"
                ),
                inline=False
            )

            embed.add_field(
                name="⏸️ Pause  *(Manage Channels)*",
                value=(
                    f"`{prefix}inc pause` / `{prefix}inc p` — Pause **this** channel\n"
                    f"`{prefix}inc pause all` / `{prefix}inc p all` — Pause ALL monitored categories\n"
                    f"`{prefix}incense pause` also works"
                ),
                inline=False
            )

            embed.add_field(
                name="▶️ Resume  *(Manage Channels)*",
                value=(
                    f"`{prefix}inc resume` / `{prefix}inc r` — Resume **this** channel\n"
                    f"`{prefix}inc resume all` / `{prefix}inc r all` — Resume ALL paused channels\n"
                    f"`{prefix}incense resume` also works"
                ),
                inline=False
            )

            embed.add_field(
                name="📋 Status",
                value=f"`{prefix}inc list` — View paused and active channels across monitored categories",
                inline=False
            )

            embed.add_field(
                name="🤖 How It Works",
                value=(
                    "• Poketwo sends `You purchased an Incense for X shards!`\n"
                    "• Bot instantly restricts Poketwo in **that specific channel** only\n"
                    "• `pause all` / `resume all` operates at the **category level** for speed\n"
                    f"• Use `{prefix}inc help` for a quick in-chat reference"
                ),
                inline=False
            )

        # Captcha commands
        elif category in ["captcha", "cap", "verify"]:
            embed = discord.Embed(
                title="🔐 Captcha Commands",
                description=(
                    "Automatically alerts users in a designated channel when Pokétwo asks them to verify. "
                    "Feature is disabled per-server until a captcha channel is set."
                ),
                color=EMBED_COLOR
            )

            embed.add_field(
                name=f"`{prefix}captcha-channel #channel`",
                value=(
                    "Set the channel where captcha alerts will be sent **(Admin only)**\n"
                    f"**Aliases:** `{prefix}captchachannel`, `{prefix}setcaptcha`\n"
                    f"**Example:** `{prefix}captcha-channel #alerts`"
                ),
                inline=False
            )

            embed.add_field(
                name=f"`{prefix}captcha-channel` (no arguments)",
                value=(
                    "Clear the captcha channel and **disable** captcha alerts for this server **(Admin only)**"
                ),
                inline=False
            )

            embed.add_field(
                name="🤖 How It Works",
                value=(
                    "• Bot watches every channel for Pokétwo's captcha message\n"
                    "• When detected, pings the flagged user in the captcha alert channel\n"
                    "• Alert includes a **Verify** button linking directly to their captcha URL\n"
                    "• **5-minute cooldown** per user — won't re-ping within 5 minutes for repeated detections\n"
                    "• If no captcha channel is set, the feature is silently disabled"
                ),
                inline=False
            )

        # All commands
        elif category in ["all", "commands"]:
            embed = discord.Embed(
                title="📚 All Commands",
                description="Complete list of all bot commands",
                color=EMBED_COLOR
            )

            embed.add_field(
                name="📦 Collection",
                value=(
                    f"`{prefix}cl add` • `{prefix}cl remove` • `{prefix}cl list`\n"
                    f"`{prefix}cl raw` • `{prefix}cl clear`"
                ),
                inline=False
            )

            embed.add_field(
                name="🗂️ Category",
                value=(
                    f"`{prefix}cat add` • `{prefix}cat remove` • `{prefix}cat list` • `{prefix}cat info`\n"
                    f"**Admin:** `{prefix}cat create` • `{prefix}cat edit` • `{prefix}cat delete`\n"
                    f"**Admin:** `{prefix}cat addpokemon` • `{prefix}cat removepokemon`"
                ),
                inline=False
            )

            embed.add_field(
                name="✨ Shiny Hunt",
                value=f"`{prefix}sh` • `{prefix}sh <pokemon>` • `{prefix}sh clear`",
                inline=False
            )

            embed.add_field(
                name="🔷 Type & Region Pings",
                value=(
                    f"`{prefix}tp` • `{prefix}tp <types>`\n"
                    f"`{prefix}rp` • `{prefix}rp <regions>`"
                ),
                inline=False
            )

            embed.add_field(
                name="⚙️ Settings",
                value=(
                    f"`{prefix}afk` • `{prefix}server-settings`\n"
                    f"`{prefix}clear-pings [@user]`\n"
                    f"**Admin:** `{prefix}rare-role` • `{prefix}regional-role` • `{prefix}toggle best_name` • `{prefix}toggle only_pings`\n"
                    f"**Admin:** `{prefix}captcha-channel [#channel]`"
                ),
                inline=False
            )

            embed.add_field(
                name="🔮 Prediction",
                value=f"`{prefix}predict`",
                inline=False
            )

            embed.add_field(
                name="⭐ Starboard Settings",
                value=(
                    f"`{prefix}starboard-settings` • `{prefix}starboard-all`\n"
                    f"`{prefix}starboard-catch/egg/unbox`\n"
                    f"`{prefix}starboard-shiny/gigantamax/highiv/lowiv/milestone/missingno`"
                ),
                inline=False
            )

            embed.add_field(
                name="🔍 Helpful",
                value=(
                    f"`{prefix}sr <pokemon>` • `{prefix}shr [chain] [target%]`\n"
                    "Hint solver (automatic — no command needed)"
                ),
                inline=False
            )

            embed.add_field(
                name="🔥 Incense",
                value=(
                    f"`{prefix}inc toggle` • `{prefix}inc cat add/remove/list`\n"
                    f"`{prefix}inc pause [all]` • `{prefix}inc resume [all]` • `{prefix}inc list`"
                ),
                inline=False
            )

            embed.add_field(
                name="🔐 Captcha",
                value=f"**Admin:** `{prefix}captcha-channel [#channel]`",
                inline=False
            )

            embed.add_field(
                name="🔍 Starboard Manual Check",
                value=f"`{prefix}catchcheck` • `{prefix}eggcheck` • `{prefix}unboxcheck`",
                inline=False
            )

            if is_owner:
                embed.add_field(
                    name="👑 Owner",
                    value=(
                        f"`{prefix}loadmodel` • `{prefix}unloadmodel` • `{prefix}reloadmodel`\n"
                        f"`{prefix}modelstatus` • `{prefix}reloadsr`\n"
                        f"`{prefix}set-low-prediction-channel`\n"
                        f"`{prefix}set-secondary-model-channel`\n"
                        f"`{prefix}starboard-set-global-catch/egg/unbox`"
                    ),
                    inline=False
                )

            embed.add_field(
                name="ℹ️ Info",
                value=f"`{prefix}help` • `{prefix}about` • `{prefix}ping`",
                inline=False
            )

        else:
            await ctx.reply(
                f"❌ Unknown category: `{category}`\n"
                f"Available categories: `collection`, `category`, `hunt`, `pings`, `settings`, `prediction`, `starboard`, `helpful`, `incense`, `captcha`, {'`owner`, ' if is_owner else ''}`all`\n"
                f"Use `{prefix}help` to see the main help menu.",
                mention_author=False
            )
            return

        embed.set_footer(text=f"Bot Prefix: {', '.join(BOT_PREFIX)}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="about")
    async def about_command(self, ctx):
        """Show bot information and statistics"""
        prefix = BOT_PREFIX[0]

        embed = discord.Embed(
            title="ℹ️ About Pokemon Helper Bot",
            description="A comprehensive Pokemon collection and prediction bot for Poketwo",
            color=EMBED_COLOR
        )

        embed.add_field(
            name="✨ Key Features",
            value=(
                "• 📦 **Collection Management** - Track and get pinged for Pokemon you collect\n"
                "• 🗂️ **Category System** - Bulk add Pokemon to collection\n"
                "• ✨ **Shiny Hunting** - Get notified when your hunt target spawns\n"
                "• 🔷 **Type & Region Pings** - Get pinged by Pokemon type or region\n"
                "• 🔮 **Dual Model Prediction** - Automatically identifies Poketwo spawns\n"
                "• ⭐ **Starboard Logging** - Log rare catches, hatches, and unboxes\n"
                "• 🎯 **Smart Pings** - Collectors, hunters, type, region, and role-based pings\n"
                "• 🔕 **AFK Mode** - Disable pings when you're away\n"
                "• 🏷️ **Best Name** - Optionally show shortest known name per prediction"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {sum(g.member_count for g in self.bot.guilds)}\n"
                f"**Commands:** {len(self.bot.commands)}"
            ),
            inline=True
        )

        embed.add_field(
            name="⚙️ Technical",
            value=(
                f"**Prefix:** {', '.join(BOT_PREFIX)}\n"
                f"**Library:** discord.py\n"
                f"**Database:** MongoDB\n"
                f"**AI Models:** Dual CNN (224×224 primary + 224×224 secondary)"
            ),
            inline=True
        )

        embed.add_field(
            name="🚀 Getting Started",
            value=f"Use `{prefix}help` to see all available commands and features!",
            inline=False
        )

        embed.add_field(
            name="🔗 Quick Links",
            value=(
                f"• `{prefix}help collection` - Set up your collection\n"
                f"• `{prefix}help category` - Bulk collection management\n"
                f"• `{prefix}help starboard` - Configure starboard logging\n"
                f"• `{prefix}afk` - Manage your ping preferences"
            ),
            inline=False
        )

        embed.set_footer(text=f"Made with ❤️ for the Poketwo community")

        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="ping", aliases=["latency", "pong"])
    async def ping_command(self, ctx):
        """Check bot's latency"""
        import time

        # Measure API latency
        api_latency = round(self.bot.latency * 1000)

        # Measure response time
        start = time.perf_counter()
        message = await ctx.reply("🏓 Pinging...", mention_author=False)
        end = time.perf_counter()
        response_time = round((end - start) * 1000)

        # Update with full info
        embed = discord.Embed(
            title="🏓 Pong!",
            color=EMBED_COLOR
        )

        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Response Time", value=f"{response_time}ms", inline=True)

        # Status indicator
        if api_latency < 100:
            status = "🟢 Excellent"
        elif api_latency < 200:
            status = "🟡 Good"
        elif api_latency < 300:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"

        embed.add_field(name="Status", value=status, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")

        await message.edit(content=None, embed=embed)

    @commands.command(name="commands", aliases=["cmds"])
    async def commands_command(self, ctx):
        """Quick alias to show all commands"""
        await ctx.invoke(self.help_command, category="all")

    # ------------------------------------------------------------------
    # Slash Commands  (registered automatically with the cog)
    # ------------------------------------------------------------------
    @app_commands.command(name="help", description="Show help information for the bot")
    @app_commands.describe(category="Category: collection, category, hunt, pings, settings, prediction, starboard, helpful, incense, captcha, all")
    async def slash_help(self, interaction: discord.Interaction, category: str = None):
        ctx = await commands.Context.from_interaction(interaction)
        await self.help_command(ctx, category=category)

    @app_commands.command(name="about", description="Show bot information and statistics")
    async def slash_about(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.about_command(ctx)

    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.ping_command(ctx)


async def setup(bot):
    await bot.add_cog(Help(bot))
