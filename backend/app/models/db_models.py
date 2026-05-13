from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    follower = "follower"
    leader = "leader"
    admin = "admin"


class BinanceEnvironment(StrEnum):
    testnet = "testnet"
    production = "production"


class BotStatus(StrEnum):
    stopped = "stopped"
    starting = "starting"
    running = "running"
    pausing = "pausing"
    paused = "paused"
    stopping = "stopping"
    error = "error"


class SourceType(StrEnum):
    leader_connected = "leader_connected"
    official_copy_api = "official_copy_api"
    manual_signal = "manual_signal"


class SignalAction(StrEnum):
    OPEN = "OPEN"
    INCREASE = "INCREASE"
    PARTIAL_CLOSE = "PARTIAL_CLOSE"
    CLOSE = "CLOSE"
    UPDATE_SL = "UPDATE_SL"
    UPDATE_TP = "UPDATE_TP"

