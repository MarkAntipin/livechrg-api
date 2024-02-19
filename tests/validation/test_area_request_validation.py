import pytest
from pydantic import ValidationError

from src.api.routers.v1.models import AreaRequest


def test_valid_area_request() -> None:
    area_request = AreaRequest(sw_lat=-10, sw_lon=-10, ne_lat=10, ne_lon=10)
    assert area_request.sw_lat == -10
    assert area_request.sw_lon == -10
    assert area_request.ne_lat == 10
    assert area_request.ne_lon == 10


def test_w_is_not_lower_left_than_ne() -> None:
    with pytest.raises(ValidationError):
        AreaRequest(sw_lat=10, sw_lon=10, ne_lat=-10, ne_lon=-10)


def test_invalid_lat() -> None:
    with pytest.raises(ValidationError):
        AreaRequest(sw_lat=-100, sw_lon=-100, ne_lat=100, ne_lon=100)


def test_invalid_lon() -> None:
    with pytest.raises(ValidationError):
        AreaRequest(sw_lat=0, sw_lon=0, ne_lat=0, ne_lon=200)


def test_invalid_type() -> None:
    with pytest.raises(ValidationError):
        AreaRequest(sw_lat='invalid', sw_lon='invalid', ne_lat='invalid', ne_lon='invalid')
