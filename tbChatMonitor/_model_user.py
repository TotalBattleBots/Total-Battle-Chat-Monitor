import threading
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List


class Player(SQLModel, table=True):
    user_id: str = Field(primary_key=True, index=True)
    clan_id: str
    name: str
    chat_user_id: str


class PlayerIdManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(PlayerIdManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def decode_user_id(cls, user_id: str) -> [int, int]:
        # Ensure the string is of even length

        # Extract the first byte
        if len(user_id) == 10:
            first_byte_str = user_id[:2]
        else:
            first_byte_str = user_id[:1]
        creation_kingdom = int(first_byte_str, 16)

        # Extract the remaining bytes
        remaining_bytes_str = user_id[2:]
        kingdom_player_number = int(remaining_bytes_str, 16)

        return int(creation_kingdom), int(kingdom_player_number)

    @classmethod
    def encode_user_id(cls, creation_kingdom: int, kingdom_player_number: int) -> str:
        # Convert creation_kingdom to a 2-character hexadecimal string
        creation_kingdom_hex = f"{creation_kingdom:02x}"

        # Convert kingdom_player_number to a hexadecimal string, zero-padded to 8 characters
        kingdom_player_number_hex = f"{kingdom_player_number:08x}"

        # Concatenate the two strings
        user_id = creation_kingdom_hex + kingdom_player_number_hex

        return user_id

    def __init__(self, database_url: str = "sqlite:///./tob_player_id_v2.db"):
        if not hasattr(self, 'engine'):
            self.engine = create_engine(database_url)
            self.init_db()

    def init_db(self):
        SQLModel.metadata.create_all(self.engine)

    def add_entry(self, user_id: str, clan_id: str, name: str, chat_user_id: str):

        with PlayerIdManager._lock, Session(self.engine) as session:
            user = session.get(Player, user_id)
            if user:
                if user.clan_id != clan_id or user.name != name:
                    print(f"Update entry for {user_id} - {name} - {clan_id} - {chat_user_id}")
                user.clan_id = clan_id
                user.name = name
            else:
                print(f"Add entry for {user_id} - {clan_id} - {name} - {chat_user_id}")
                user = Player(user_id=user_id, clan_id=clan_id, name=name, chat_user_id=chat_user_id)
                session.add(user)
            session.commit()

    def query_users(self, name: Optional[str] = None, clan_id: Optional[str] = None) -> List[Player]:
        with Session(self.engine) as session:
            query = select(Player)
            if name:
                query = query.where(Player.name == name)
            if clan_id:
                query = query.where(Player.clan_id == clan_id)
            results = session.exec(query).all()
            return results

    def get_player_by_id(self, user_id: str) -> Optional[Player]:
        with Session(self.engine) as session:
            user = session.get(Player, user_id)
            if not user:
                user = Player()
                user.clan_id = "UNK"
                user.name = "UNK"
                user.user_id = user_id
                user.chat_user_id = "site1:0"
            return user
