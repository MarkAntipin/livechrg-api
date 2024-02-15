from datetime import datetime

from src.api.routers.v1.models import AddComment, Charger, Comment, Event


def _is_datetime_equal(dt_1: datetime, dt_2: datetime, threshold_second: int = 60) -> bool:
    return abs((dt_1 - dt_2).total_seconds()) < threshold_second


def _is_events_equal(event_1: Event, event_2: Event) -> bool:
    return (
        _is_datetime_equal(event_1.charged_at, event_2.charged_at)
        and event_1.source == event_2.source
        and event_1.name == event_2.name
        and event_1.is_problem == event_2.is_problem
    )


def _is_comments_equal(comment_1: Comment | AddComment, comment_2: Comment | AddComment) -> bool:
    return (
        _is_datetime_equal(comment_1.created_at, comment_2.created_at)
        and comment_1.text == comment_2.text
        and comment_1.source == comment_2.source
        and comment_1.user_name == comment_2.user_name
    )


def _is_chargers_equal(charger_1: Charger, charger_2: Charger) -> bool:
    # Directly address the scenario where both chargers have no ocpi_ids
    if charger_1.ocpi_ids is None and charger_2.ocpi_ids is None:
        return charger_1.network == charger_2.network
    # Proceed with comparison if both have ocpi_ids
    return (
        charger_1.network == charger_2.network
        and charger_1.ocpi_ids is not None
        and charger_2.ocpi_ids is not None
        and sorted(charger_1.ocpi_ids) == sorted(charger_2.ocpi_ids)
    )


def filter_events(old_events: list[Event], new_events: list[Event]) -> list[Event]:
    evens_to_add = []
    for new_event in new_events:
        for old_event in old_events:
            if _is_events_equal(old_event, new_event):
                break
        else:
            evens_to_add.append(new_event)

    return evens_to_add


def filter_comments(old_comments: list[Comment], new_comments: list[AddComment]) -> list[AddComment]:
    comments_to_add = []
    for new_comment in new_comments:
        for old_comment in old_comments:
            if _is_comments_equal(old_comment, new_comment):
                break
        else:
            comments_to_add.append(new_comment)

    return comments_to_add


def filter_chargers(old_chargers: list[Charger], new_chargers: list[Charger]) -> list[Charger]:
    chargers_to_add = []
    for new_charger in new_chargers:
        for old_charger in old_chargers:
            if _is_chargers_equal(old_charger, new_charger):
                break
        else:
            chargers_to_add.append(new_charger)

    return chargers_to_add
