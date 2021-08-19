#!/usr/bin/env python

import re
from enum import Enum, auto
from typing import Optional


class Carrier(Enum):
    """An enum of shipping carriers"""
    UPS = auto()
    FEDEX = auto()
    USPS = auto()


def guess_carrier(
        tracking_number: str
) -> Optional[Carrier]:
    """
    Guess which carrier a tracking number belongs to

    Parameters
    ----------
    tracking_number
        The tracking number to guess a carrier for.

    Returns
    -------
    Optional[Carrier]
        The carrier the tracking number belongs to.
    """

    if re.compile(r'1Z\d*').match(tracking_number):
        return Carrier.UPS

    if re.compile(r'\d{12}').match(tracking_number):
        return Carrier.FEDEX

    return None


class ShippingServices:
    """A class wrapping multiple shipping carrier API wrapping packages, providing a higher level multi carrier package."""

    def __init__(
            self,
            ups_auth: Optional[dict[str, str]] = None,
            fedex_auth: Optional[dict[str, str]] = None,
            usps_auth: Optional[dict[str, str]] = None
    ):
        self.ups_client = None
        self.fedex_client = None
        self.usps_client = None

        if ups_auth is not None:
            try:
                from darbiadev_ups.ups_services import UPSServices
                self.ups_client = UPSServices(**ups_auth)
            except ImportError as error:
                raise ImportError('Install darbiadev-ups for UPS support') from error

        if fedex_auth is not None:
            try:
                from darbiadev_fedex.fedex_services import FedExServices
                self.fedex_client = FedExServices(**fedex_auth)
            except ImportError as error:
                raise ImportError('Install darbiadev-fedex for FedEx support') from error

        if usps_auth is not None:
            try:
                from darbiadev_usps.usps_services import USPSServices
                self.usps_client = USPSServices(**usps_auth)
            except ImportError as error:
                raise ImportError('Install darbiadev-usps for USPS support') from error

    def _get_carrier_client(self, carrier: Carrier):
        if carrier == Carrier.UPS:
            if self.ups_client is None:
                raise ImportError('UPS is not enabled.')
            return self.ups_client

        elif carrier == Carrier.FEDEX:
            if self.fedex_client is None:
                raise ImportError('FedEx is not enabled.')
            return self.fedex_client

        elif carrier == Carrier.USPS:
            if self.usps_client is None:
                raise ImportError('USPS is not enabled.')
            return self.usps_client

    def track(
            self,
            tracking_number: str,
            carrier: Optional[Carrier] = None
    ) -> dict[str, ...]:
        """Get details for tracking number"""

        if carrier is None:
            carrier = guess_carrier(tracking_number)

        if carrier is None:
            raise ValueError(f'Unable to guess carrier for tracking number {tracking_number}')

        return self._get_carrier_client(carrier=carrier).track(tracking_number=tracking_number)
