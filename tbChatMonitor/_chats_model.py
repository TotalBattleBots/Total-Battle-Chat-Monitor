import time
from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel, create_engine, Relationship, Session
import os
import time

from _tb_message_api import list_chats, list_users_in_chat


class ChatMemberLink(SQLModel, table=True):
    chat_id: Optional[int] = Field(default=None, foreign_key="tbchat.id", primary_key=True)
    player_id: Optional[int] = Field(default=None, foreign_key="tbplayer.id", primary_key=True)


class ClanChatLink(SQLModel, table=True):
    clan_id = Optional[int] = Field(default=None, foreign_key="tbclans.id")
    chat_id = Optional[int] = Field(default=None, foreign_key="tbchat.id")


class TBChat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    last_seen: str
    created_by: int
    channel_url: str = Field(unique=True)
    last_message_time: str = Field(default="0")
    members: List["TBPlayer"] = Relationship(back_populates="chats", link_model=ChatMemberLink)
    clans: List["TBClans"] = Relationship(back_populates="chats", link_model=ClanChatLink)


class TBPlayer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    clan: Optional[str]
    chats: List[TBChat] = Relationship(back_populates="members", link_model=ChatMemberLink)


class TBClans(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    clan_trigraph: str = Field(index=True)
    chats: List[TBChat] = Relationship(back_populates="clans", link_model=ChatMemberLink)


class TBChatMembers(SQLModel, table=True):
    player_id: int = Field(default=None, foreign_key="tbplayer.id", primary_key=True)
    chat_id: int = Field(default=None, foreign_key="tbchat.id", primary_key=True)
    last_seen_time: str


class TBChatClans(SQLModel, table=True):
    clan_id: int = Field(default=None, foreign_key="tbclans.id", primary_key=True)
    chat_id: int = Field(default=None, foreign_key='tbchat.id', primary_key=True)
    last_seen_time: str


class TBChatDb:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TBChat, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.chat_database = 'tb_chats.db'
        self.chat_engine = f"sqlite://{self.chat_database}"
        self._engine = create_engine(self.chat_engine)
        if not os.path.exists(self.chat_database):
            SQLModel.metadata.create_all(self._engine)

    def _insert_or_update_chat(self, chat: Dict):
        update_time = time.time()
        chat_name = chat['name']
        chat_url = chat['channel_url']
        chat_created = chat['created_at']
        created_by = chat['created_by']['user_id']
        last_message = chat.get('last_message', {})
        last_message_time = last_message.get('created_at', 0)

        # Query users for a chat:
        chat_members = list_users_in_chat(chat_url)

        # Now see if a chat exists with that name.



    def query_members_in_chat(self, chat_path):
        pass

    def scan_index_chats_by_pattern(self, chat_patterns: List[str]):
        for pattern in chat_patterns:
            chats = list_chats(pattern)

        c_dict = {}
        # reduce duplicates from the patterns
        for chat in chats:
            c_dict[chat['name']] = chat

        for c_name in c_dict.keys():
            self._insert_or_update_chat(c_dict[c_name])
