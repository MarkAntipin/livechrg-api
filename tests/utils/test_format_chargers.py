import pytest
import json

from src.services.stations import StationsServices

from src.api.routers.v1.models import Charger


class MockRecord(dict):
    """Mocking asyncpg.Record"""

    def __getattr__(self, item):
        return self[item]


@pytest.mark.parametrize("charger_rows, expected_output", [
    (
            # Test for Non-Duplicate Chargers Across Different Networks
            # Verifies that the function correctly processes a list of chargers without any duplicates,
            # each belonging to a different network.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1"])),
                MockRecord(network="Network2", ocpi_ids=json.dumps(["id2"])),
                MockRecord(network="Network3", ocpi_ids=json.dumps(["id3"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network2", ocpi_ids=["id2"]),
                Charger(network="Network3", ocpi_ids=["id3"])
            ]
    ),
    (
            # Test for Duplicate Chargers Within the Same Network
            # Ensures that the function correctly identifies and handles duplicate chargers within the same network,
            # returning only unique chargers.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1"])),
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1"])),
                MockRecord(network="Network2", ocpi_ids=json.dumps(["id2"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network2", ocpi_ids=["id2"])
            ]
    ),
    (
            # Test for Chargers with Different OCPI IDs in the Same Network
            # Checks if the function can handle multiple chargers under the same network,
            # each with a different OCPI ID, and treat them as unique entities.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1"])),
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id2"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network1", ocpi_ids=["id2"])
            ]
    ),
    (
            # Test for Chargers with the Same OCPI ID Across Different Networks
            # Verifies that the function treats chargers with the same OCPI ID
            # but different networks as unique chargers.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1"])),
                MockRecord(network="Network2", ocpi_ids=json.dumps(["id1"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network2", ocpi_ids=["id1"])
            ]
    ),
    (
            # Test for Chargers with Multiple OCPI IDs in the Same Network
            # Ensures that the function correctly splits chargers with multiple OCPI IDs
            # into separate charger entities under the same network.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1", "id2", "id3"])),
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1", "id2"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network1", ocpi_ids=["id2"]),
                Charger(network="Network1", ocpi_ids=["id3"])
            ]
    ),
    (
            # Test for Chargers with Multiple OCPI IDs Across Different Networks
            # Checks the function's ability to handle chargers with multiple OCPI IDs across different networks,
            # ensuring each OCPI ID is treated as a unique charger.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps(["id1", "id2"])),
                MockRecord(network="Network2", ocpi_ids=json.dumps(["id1", "id2"]))
            ],
            [
                Charger(network="Network1", ocpi_ids=["id1"]),
                Charger(network="Network1", ocpi_ids=["id2"]),
                Charger(network="Network2", ocpi_ids=["id1"]),
                Charger(network="Network2", ocpi_ids=["id2"])
            ]
    ),
    (
            # Test for Chargers with Empty OCPI IDs
            # Verifies that the function correctly handles cases where a charger has an empty list of OCPI IDs,
            # ensuring that it sets `ocpi_ids` to `None`.
            [
                MockRecord(network="Network1", ocpi_ids=json.dumps([]))
            ],
            [
                Charger(network="Network1", ocpi_ids=None)
            ]
    ),
    (
            # Test for Chargers with Missing OCPI IDs Field
            # Confirms that the function gracefully handles cases where the `ocpi_ids` field is missing from the charger data,
            # setting the `ocpi_ids` field of the resulting `Charger` object to `None`.
            [
                MockRecord(network="Network1")
            ],
            [
                Charger(network="Network1", ocpi_ids=None)
            ]
    ),
])
def test_format_chargers(charger_rows, expected_output):
    assert StationsServices._format_chargers(charger_rows) == expected_output
