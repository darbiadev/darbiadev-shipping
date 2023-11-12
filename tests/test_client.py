"""Test client module."""

import pytest

from darbiadev_shipping import ShippingServices


def test_no_clients_enabled():
    """Ensure that ShippingServices raises ValueError when no clients are enabled."""
    with pytest.raises(ValueError):
        ShippingServices()
