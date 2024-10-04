import sys

if __name__ == "__main__":
    sys.path.append(".")

import asyncio
import time
import traceback

import hikari
import lightbulb
import _journal
from _group_chats import get_all_group_chat_messages, format_group_message
from search_chats import search_chats, display_chat
from player_database import PlayerIdManager
from player_database import display_user as pm_display_user
from extract_bank_caravans import get_caravans_xls
import jsonpickle
import os
import threading
from _journal_monitor import dump_journal as _dump_journal
import json

c_dict = {}
c_dict_initialized = False
c_dict_initialized_lock = threading.Lock()
c_dict_lock = threading.Lock()
chat_save_file = "chat_list_data.json"

bot_config = {
    "authorized_channels": [

    ],
    "DISCORD_TOKEN": "",
    "PANOPTICON_ROLE_ID": 1
}


def save_state():
    open(chat_save_file, "w").write(jsonpickle.dumps(c_dict))


def load_state():
    global c_dict, c_dict_initialized

    print("!!! c_dict loading. ")
    if os.path.exists(chat_save_file):
        try:
            with c_dict_lock:
                c_dict = jsonpickle.loads(open(chat_save_file, "r").read())

            with c_dict_initialized_lock:
                c_dict_initialized = True
        except Exception:
            pass
    print("!!! c_dict loaded")


class PanopticonBotHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context: lightbulb.Context) -> None:
        commands_string = """
 `journal` - retreive a journal by the journal entry id.
 `dump_chat` - dump the contexts of a group chat to a downloadable text file.
 `chat_search` - find a chat or chats based on the user, their clan, or a sub-string in the chat name.
"""
        await context.respond(commands_string)

    async def send_plugin_help(self, context: lightbulb.Context, plugin: lightbulb.Plugin):
        # Override this method to change the message sent when the help command
        # argument is the name of a plugin.
        await context.respond("Not Implemented")

    async def send_command_help(self, context: lightbulb.Context, command: lightbulb.Command):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command.
        await context.respond("Not Implemented")

    async def send_group_help(self, context: lightbulb.Context, group):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command group.
        await context.respond("Not Implemented")

    async def object_not_found(self, context: lightbulb.Context, obj):
        await context.respond("Object not found.")


# Override this method to change the message sent when help is
# requested for an object that does not exist


def _save_config_to_file():
    global bot_config

    open("_panopticon_bot_config.json", 'w').write(json.dumps(bot_config, indent=4))


def _load_config_from_file():
    global bot_config

    with open("_panopticon_bot_config.json", "r") as f:
        _config: dict = json.load(f)
        bot_config = _config


_load_config_from_file()


def split_string_on_newline(s, max_bytes=1900):
    # Convert the string to bytes
    s_bytes = s.encode('utf-8')

    # List to store the split strings
    result = []

    # Starting index for each split
    start = 0

    while start < len(s_bytes):
        # If the remaining string is shorter than max_bytes, append it to the result and break
        if len(s_bytes) - start <= max_bytes:
            result.append(s_bytes[start:].decode('utf-8'))
            break

        # Find the end index for the current split
        end = start + max_bytes

        # Backtrack to the last newline
        while end > start and s_bytes[end] != ord('\n'):
            end -= 1

        # If we didn't find a newline, just split at max_bytes
        if end == start:
            end = start + max_bytes

        # Append the split string to the result
        result.append(s_bytes[start:end].decode('utf-8'))

        # Move the start index to the next character after the newline
        start = end + 1 if s_bytes[end] == ord('\n') else end

    return result


bot = lightbulb.BotApp(token=bot_config['DISCORD_TOKEN'], intents=hikari.Intents.ALL_UNPRIVILEGED)
bot.help_command = PanopticonBotHelp(bot)


@bot.listen(hikari.ShardReadyEvent)
async def ready_listener(_):
    print("The bot is ready!")


@bot.command()
@lightbulb.option("journal_id", "Journal Entry ID")
@lightbulb.option("show_attacker", "Display Attacker Information", required=False, type=bool)
@lightbulb.command("debug_journal", "Get A Journal Entry with debug information.")
@lightbulb.implements(lightbulb.SlashCommand)
async def debug_journal(ctx: lightbulb.Context) -> None:
    """
    Command to log a journal entry.
    """

    if (ctx.channel_id in bot_config.get('authorized_channels', []) and
            bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
        await ctx.respond(f"Fetching journal {ctx.options.journal_id}")
        message_text = json.dumps(_journal.get_journal_data_by_id(j_id=int(ctx.options.journal_id)), indent=4)
        if message_text:
            hf = hikari.files.Bytes(message_text, f"journal_debug-{ctx.options.journal_id}-{time.time()}.txt")
            await ctx.respond(hf)
        else:
            await ctx.respond(f"No Journal entry found.")
    else:
        await ctx.respond("Not Authorized")


@bot.command()
@lightbulb.option("journal_id", "Journal Entry ID")
@lightbulb.option("player_id", "player's ID")
@lightbulb.command("delete_journal", "Ninja Delete a Journal Entry")
@lightbulb.implements(lightbulb.SlashCommand)
async def delete_journal(ctx: lightbulb.Context) -> None:
    """
    Command to Delete a journal Entry
    Args:
        ctx: Context structure for hikari lightbulb

    Returns: None

    """
    try:
        journal_int = int(ctx.options.journal_id)
    except ValueError:
        await ctx.respond(f"Invalid Journal ID: {ctx.options.journal_id}")
        return

    if (ctx.channel_id in bot_config.get('authorized_channels', []) and
            bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
        await ctx.respond(f"Fetching journal {ctx.options.journal_id}")
        response_msg = _journal.delete_journal_entry(player_id=ctx.options.player_id,
                                                     j_id=int(ctx.options.journal_id))
        if 'error' in response_msg:
            await ctx.respond(f"Failed to delete journal entry {ctx.options.journal_id} from user.")
        else:
            await ctx.respond(f"Successfully deleted journal entry {ctx.options.journal_id} from "
                              f"journal {ctx.options.player_id}")
    else:
        await ctx.respond("Not Authorized")


@bot.command()
@lightbulb.option("journal_id", "Journal Entry ID")
@lightbulb.option("show_attacker", "Display Attacker Information", required=False, type=bool)
@lightbulb.command("journal", "Get A Journal Entry")
@lightbulb.implements(lightbulb.SlashCommand)
async def journal(ctx: lightbulb.Context) -> None:
    """
    Command to log a journal entry.
    """

    try:
        journal_int = int(ctx.options.journal_id)
    except ValueError:
        await ctx.respond(f"Invalid Journal ID: {ctx.options.journal_id}")
        return

    if (ctx.channel_id in bot_config.get('authorized_channels', []) and
            bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
        await ctx.respond(f"Fetching journal {ctx.options.journal_id}")
        response_msg = _journal.format_journal(journal_entry=int(ctx.options.journal_id),
                                               full=True,
                                               show_attacker=True)
    else:
        response_msg = "Not Authorized"

    response_lines = split_string_on_newline(response_msg)
    for line in response_lines:
        try:
            await ctx.respond(f"```{line}```")
        except Exception as e:
            traceback.print_exc()
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{str(e)}")


@bot.command()
@lightbulb.option("player_id", "Channel Path")
@lightbulb.option("days", "Channel Path")
@lightbulb.command("dump_caravans", "Dump a chat")
@lightbulb.implements(lightbulb.SlashCommand)
async def dump_caravans(ctx: lightbulb.Context) -> None:
    if (ctx.channel_id in bot_config.get('authorized_channels', []) and
            bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
        player_id = ctx.options.player_id
        days = int(ctx.options.days)

        if days > 14 or days < 1:
            await ctx.respond("Invalid Days value. Must be between 1 and 14. ")

        pm = PlayerIdManager()
        player_info = pm.get_player_by_id(player_id)

        await ctx.respond(f"...processing caravan dump request of {player_info.name} for the past {days} days."
                          " This may take quite a while.")
        loop = asyncio.get_event_loop()
        message_text = await loop.run_in_executor(None, lambda: thread_dump_caravans(days, player_id))
        if message_text:
            hf = hikari.files.Bytes(message_text, f"{player_info.name}-{days}-{time.time()}.txt")
            await ctx.respond(hf)
        else:
            await ctx.respond(f"No caravans were found within the timeframe for {player_info.name}")

    else:
        await ctx.respond("Not Authorized.")


def thread_dump_caravans(days, player_id):
    result = get_caravans_xls(player_id=player_id, days=days)
    return result


@bot.command()
@lightbulb.option("channel_path", "Channel Path")
@lightbulb.command("dump_group_messages", "Dump a chat")
@lightbulb.implements(lightbulb.SlashCommand)
async def dump_group_messages(ctx: lightbulb.Context) -> None:
    if (ctx.channel_id in bot_config.get('authorized_channels', []) and
            bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
        await ctx.respond(f"...processing chat dump of {ctx.options.channel_path}")

        loop = asyncio.get_event_loop()
        messages = await loop.run_in_executor(None, lambda: get_all_group_chat_messages(
            chat_path=ctx.options.channel_path))
        message_text = b""
        for message in messages:
            message_text += format_group_message(message).encode('utf-8') + "\n\r".encode('utf-8')

        hf = hikari.files.Bytes(message_text, f"{ctx.options.channel_path}-{time.time()}.txt")
        await ctx.respond(hf)
    else:
        await ctx.respond("Not Authorized.")


@bot.command()
@lightbulb.option("chat_name", "chat name to search for", required=False)
@lightbulb.option("clan_id", "clan trigraph to search for", required=False)
@lightbulb.option("player_name", "player name to search for", required=False)
@lightbulb.command("chat_search", "search chat database for players")
@lightbulb.implements(lightbulb.SlashCommand)
async def chat_search(ctx: lightbulb.Context) -> None:
    try:
        if (ctx.channel_id in bot_config.get('authorized_channels', []) and
                bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
            is_ready = False

            if ctx.options.player_name is None and ctx.options.clan_id is None and ctx.options.chat_name is None:
                await ctx.respond("At least one option must be provided.")
                return

            with c_dict_initialized_lock:
                is_ready = c_dict_initialized

            if is_ready:
                await ctx.respond("Searching.  Please wait.")
                output_message = ""
                results = search_chats(search_nick_name=ctx.options.player_name,
                                       search_clan_name=ctx.options.clan_id,
                                       search_channel_name=ctx.options.chat_name)

                for result in results:
                    output_message += display_chat(result)

                output_message.replace("\n", "\r\n")
                output_message = output_message.encode('utf-8')
                hf = hikari.files.Bytes(output_message, f"chat_search-{time.time()}.txt")
                await ctx.respond(hf)
            else:
                await ctx.respond("...database still initializing.  Try again in a few minutes.")
        else:
            await ctx.respond("Not Authorized.")
    except Exception as e:
        print(f"Exception occured: {str(e)}")
        await ctx.respond("Error")


@bot.command()
@lightbulb.option("player_id", "Channel Path")
@lightbulb.option("days", "Channel Path", required=False, type=int)
@lightbulb.option("entries", "number of entries", required=False, type=int)
@lightbulb.command("dump_journal", "Dump a chat")
@lightbulb.implements(lightbulb.SlashCommand)
async def dump_journal(ctx: lightbulb.Context) -> None:
    try:
        days = ctx.options.days if ctx.options.days else 1
        max_entries = ctx.options.entries if ctx.options.entries else 100
        player_id = ctx.options.player_id

        if (ctx.channel_id in bot_config.get('authorized_channels', []) and
                bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
            pm = PlayerIdManager()
            player_info = pm.get_player_by_id(player_id)
            await ctx.respond(f"Fetching journal for [{player_info.clan_id}] {player_info.name}")

            loop = asyncio.get_event_loop()

            results = await loop.run_in_executor(None, lambda: _dump_journal(player_id=player_id,
                                                                             days=days,
                                                                             max_entries=max_entries,
                                                                             csv_output=False))

            results.replace("\n", "\r\n")
            output_message = results.encode('utf-8')
            hf = hikari.files.Bytes(output_message,
                                    f"journal-dump-{player_info.clan_id}-{player_info.name}-{time.time()}.txt")
            await ctx.respond(hf)
        else:
            await ctx.respond("Not Authorized.")
    except Exception as e:
        print(f"Exception occured: {str(e)}")
        traceback.print_exc()
        await ctx.respond("Error")


@bot.command()
@lightbulb.option("name", "Name, case sensitive")
@lightbulb.command("player_list", "list players and their ids")
@lightbulb.implements(lightbulb.SlashCommand)
async def player_list(ctx: lightbulb.Context) -> None:
    player_name = ctx.options.name
    result_message = ""
    try:
        if (ctx.channel_id in bot_config.get('authorized_channels', []) and
                bot_config['PANOPTICON_ROLE_ID'] in ctx.member.role_ids):
            pm = PlayerIdManager()

            for one_user in pm.query_users(name=player_name):
                result = pm_display_user(one_user)
                if result:
                    result_message += result + "\n"
                    print(result)

            if result_message:
                response_lines = split_string_on_newline(result_message)
                for line in response_lines:
                    await ctx.respond("```" + line + "```")
            else:
                await ctx.respond("No Results returned. ")
        else:
            await ctx.respond("Not Authorized.")
    except Exception as e:
        print(f"Exception occured: {str(e)}")
        traceback.print_exc()
        await ctx.respond("Error")


def bot_main():
    thread = threading.Thread(target=load_state)
    thread.start()
    bot.run()


if __name__ == "__main__":
    bot_main()
