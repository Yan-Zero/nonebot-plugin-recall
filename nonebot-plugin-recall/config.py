from typing import List, Literal

from nonebot import get_plugin_config
from pydantic import BaseModel

ADAPtER_NAME = Literal["OneBot V11", "OneBot V12", "QQ Guild", "Discord", "Kaiheila"]


class Config(BaseModel):
    follow_withdraw_all: bool = True
    follow_withdraw_interval: float = 0.5
    follow_withdraw_enable_adapters: List[ADAPtER_NAME] = [
        "OneBot V11",
        "OneBot V12",
        # "QQ Guild",
        # "Discord",
        # "Kaiheila",
    ]
    follow_withdraw_bot_blacklist: List[str] = []
    follow_withdraw_plugin_blacklist: List[str] = []
    follow_withdraw_when_message_has_recall: bool = True
    follow_withdraw_expire_time: int = 10 * 60

    redis_url: str = "redis://localhost/1"


withdraw_config = get_plugin_config(Config)
