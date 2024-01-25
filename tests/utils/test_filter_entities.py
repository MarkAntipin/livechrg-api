
from src.utils.filter_entities import (
    AddComment,
    Charger,
    Comment,
    Event,
    filter_chargers,
    filter_comments,
    filter_events,
)


def test_filter_events() -> None:
    # arrange
    old_events = [
        Event(
            charged_at='2021-01-01 00:00:54',
            source='plugshare',
            name='Tesla',
            is_problem=False
        )
    ]
    new_events = [
        Event(
            charged_at='2021-01-01 00:00:00',
            source='plugshare',
            name='Tesla',
            is_problem=False
        ),
        # another name
        Event(
            charged_at='2021-01-01 00:00:00',
            source='plugshare',
            name='honda',
            is_problem=False
        ),
    ]

    events_to_add = [
        Event(
            charged_at='2021-01-01 00:00:00',
            source='plugshare',
            name='honda',
            is_problem=False
        )
    ]

    # act
    result = filter_events(old_events, new_events)

    # assert
    assert result == events_to_add


def test_filter_comments() -> None:
    # arrange
    old_comments = [
        Comment(
            text='text',
            created_at='2021-01-01 00:00:54',
            source='plugshare',
        )
    ]
    new_comments = [
        AddComment(
            text='text',
            created_at='2021-01-01 00:00:00',
            source='plugshare',
        ),
        # another datetime
        AddComment(
            text='text',
            created_at='2022-01-01 00:00:00',
            source='plugshare',
        ),
    ]

    comments_to_add = [
        AddComment(
            text='text',
            created_at='2022-01-01 00:00:00',
            source='plugshare',
        )
    ]

    # act
    result = filter_comments(old_comments, new_comments)

    # assert
    assert result == comments_to_add


def test_filter_chargers() -> None:
    # arrange
    old_chargers = [
        Charger(
            network='network',
            ocpi_ids=['id_1', 'id_2']
        )
    ]
    new_chargers = [
        # same but different order of ocpi_ids; should be equal
        Charger(
            network='network',
            ocpi_ids=['id_2', 'id_1']
        ),
        # another network
        Charger(
            network='network_2',
            ocpi_ids=['id_1', 'id_2']
        ),
    ]

    chargers_to_add = [
        Charger(
            network='network_2',
            ocpi_ids=['id_1', 'id_2']
        ),
    ]

    # act
    result = filter_chargers(old_chargers, new_chargers)

    # assert
    assert result == chargers_to_add
