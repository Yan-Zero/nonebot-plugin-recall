import redis

from pydantic import BaseModel

from .config import withdraw_config

REDIS = redis.Redis.from_url(withdraw_config.redis_url)


class OriginMessage(BaseModel):
    message_id: str
    adapter_name: str
    channel_id: str | None
    follow_messages: list["FollowMessage"]


class FollowMessage(BaseModel):
    message_id: str
    adapter_name: str
    channel_id: str | None
    origin_message_id: str


async def get_follow_message(
    adapter_name: str, message_id: str, channel_id: str | None = None
) -> list[FollowMessage] | None:
    try:
        ret = REDIS.smembers(f"OriginMessage:{adapter_name}:{message_id}:{channel_id}")
    except Exception:
        ret = set()
    return [FollowMessage.model_validate_json(i) for i in ret]


async def save_message(
    adapter_name: str, origin_message_dict: dict[str, str], message_dict: dict[str, str]
) -> None:
    follow_message = FollowMessage(
        message_id=message_dict["message_id"],
        channel_id=origin_message_dict.get("channel_id"),
        adapter_name=adapter_name,
        origin_message_id=origin_message_dict["message_id"],
    )
    REDIS.sadd(
        f'OriginMessage:{adapter_name}:{origin_message_dict["message_id"]}:{origin_message_dict.get("channel_id")}',
        follow_message.model_dump_json(),
    )
    REDIS.expire(
        f'OriginMessage:{adapter_name}:{origin_message_dict["message_id"]}:{origin_message_dict.get("channel_id")}',
        withdraw_config.follow_withdraw_expire_time,
    )


async def clear_message():
    REDIS.delete(*REDIS.keys("OriginMessage:*"))
    REDIS.delete(*REDIS.keys("RECALL:*"))


async def recall_record(
    adapter_name: str, message_id: str, channel_id: str | None = None
) -> None:
    REDIS.set(
        f"RECALL:{adapter_name}:{message_id}:{channel_id}",
        1,
        ex=withdraw_config.follow_withdraw_expire_time,
    )


async def has_recalled(
    adapter_name: str, message_id: str, channel_id: str | None = None
) -> bool:
    return REDIS.get(f"RECALL:{adapter_name}:{message_id}:{channel_id}") is not None
