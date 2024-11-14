import enum


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    freezed = "freezed"
    deleted = "deleted"
    banned = "banned"

    def __str__(self) -> str:
        return self.value


class FreezeSteps(enum.Enum):
    yes = "yes"
    wait_yes = "wait_yes"
    no = "no"
    wait_no = "wait_no"

    def __str__(self) -> str:
        return self.value


class ReportStatus(enum.Enum):
    created = "created"
    at_work = "at_work"
    decided = "decided"
    cancelled = "cancelled"

    def __str__(self) -> str:
        return self.value
