#!/usr/bin/env python
"""client tests"""

import pytest

from darbiadev_shipping import ShippingServices


def test_no_clients_enabled():
    """error if no clients available"""
    with pytest.raises(ValueError):
        ShippingServices()
