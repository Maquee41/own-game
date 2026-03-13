import enum


class MatchStatus(enum.StrEnum):
    WAITING = 'waiting'
    ACTIVE = 'active'
    FINISHED = 'finished'
    CANCELLED = 'cancelled'


class RoomStatus(enum.StrEnum):
    IDLE = 'idle'
    LOBBY = 'lobby'
    CONFIRMATION = 'confirmation'
    IN_ROUND = 'in_round'
    FINISHED = 'finished'
