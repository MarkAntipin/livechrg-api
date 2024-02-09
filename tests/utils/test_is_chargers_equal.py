import pytest
from src.utils.filter_entities import (
    Charger,
    _is_chargers_equal
)


# Sample chargers for testing
charger1 = Charger(network="Network1", ocpi_ids=["ocpi1", "ocpi2"])
charger2 = Charger(network="Network2", ocpi_ids=["ocpi1", "ocpi2"])
charger3 = Charger(network="Network1", ocpi_ids=["ocpi1", "ocpi2"])  # Duplicate of charger1
charger4 = Charger(network="Network3", ocpi_ids=None)
charger5 = Charger(network="Network1", ocpi_ids=["ocpi1", "ocpi3"])
charger6 = Charger(network="Network1", ocpi_ids=None)


@pytest.mark.parametrize("test_charger1, test_charger2, expected_result", [
    # Same network, same ocpi_ids
    (charger1, charger3, True),
    # Same network, different ocpi_ids
    (charger1, charger5, False),
    # Different network, same ocpi_ids
    (charger1, charger2, False),
    # Different network, new charger ocpi_ids=None
    (charger1, charger4, False),
    # Same network, new charger ocpi_ids=None
    (charger1, charger6, False),
    # Same network, both chargers ocpi_ids=None
    (charger4, charger4, True),
    # Different network, existing charger ocpi_ids=None
    (charger4, charger3, False)
])
def test_is_chargers_equal(test_charger1, test_charger2, expected_result):
    assert _is_chargers_equal(test_charger1, test_charger2) == expected_result
