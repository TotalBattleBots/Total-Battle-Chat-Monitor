from _clan_chat import post_clan_messages
from _kingdom_chat import post_kingdom_messages
from _group_chats import post_group_chats
from _bot_core import bot_main
from _journal_monitor import post_journals
import time
import random
import threading


def thread_post_clan_messages():
    while True:
        try:
            post_clan_messages()
        except Exception:
            time.sleep(5)

        time.sleep(random.randint(120, 300))


def thread_post_kingdom_messages():
    while True:
        try:
            post_kingdom_messages()
        except Exception:
            time.sleep(5)

        time.sleep(random.randint(30, 120))


def thread_post_group_chats():
    while True:
        try:
            post_group_chats()
        except Exception:
            time.sleep(5)

        time.sleep(random.randint(120, 300))


def thread_bot():
    bot_main()


def thread_post_journals():
    while True:
        try:
            post_journals()
        except Exception:
            time.sleep(5)

        time.sleep(random.randint(5, 15))



if __name__ == '__main__':
    clan_thread = threading.Thread(target=thread_post_clan_messages)
    kingdom_thread = threading.Thread(target=thread_post_kingdom_messages)
    group_thread = threading.Thread(target=thread_post_group_chats)
    bot_thread = threading.Thread(target=thread_bot)
    journal_thread = threading.Thread(target=thread_post_journals)

    clan_thread.start()
    kingdom_thread.start()
    group_thread.start()
    journal_thread.start()
    bot_thread.start()

    while True:
        time.sleep(random.randint(60, 120))
