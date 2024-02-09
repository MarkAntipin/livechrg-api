import pytest

from src.utils.calculate_average_rating import calculate_average_rating


@pytest.mark.parametrize(
    'comments_rating, expected_average_rating',
    [
        ([], None),
        ([1], 10.0),
        ([-1], 1.0),
        ([1, -1], 5.5),
        ([1, 1, 1, 1, 1], 10.0),
        ([-1, -1, -1, -1, -1], 1.0),
    ]
)
def test_calculate_average_rating(comments_rating: list[int], expected_average_rating: float | None) -> None:
    # act
    average_rating = calculate_average_rating(comments_rating)

    # assert
    assert average_rating == expected_average_rating