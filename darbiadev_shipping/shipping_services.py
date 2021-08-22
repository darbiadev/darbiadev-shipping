#!/usr/bin/env python

import re
from enum import Enum, auto
from typing import Optional, Union


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

        if ups_auth is None and fedex_auth is None and usps_auth is None:
            raise ValueError('No clients are enabled. Please enable at least one client to use this package.')

    def _get_carrier_client(
            self,
            carrier: Optional[Carrier] = None,
    ) -> Union['UPSServices', 'FedExServices', 'USPSServices']:
        client = None

        if carrier is None:
            clients = [self.ups_client, self.fedex_client, self.usps_client]
            client = next((client for client in clients if client is not None), None)

        elif carrier == Carrier.UPS:
            if self.ups_client is None:
                raise ValueError('UPS is not enabled.')
            client = self.ups_client

        elif carrier == Carrier.FEDEX:
            if self.fedex_client is None:
                raise ValueError('FedEx is not enabled.')
            client = self.fedex_client

        elif carrier == Carrier.USPS:
            if self.usps_client is None:
                raise ValueError('USPS is not enabled.')
            client = self.usps_client

        if client is None:
            raise ValueError('No suitable client found')

        return client

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

    def validate_address(
            self,
            street_lines: list[str],
            city: str,
            state: str,
            postal_code: str,
            country: str,
            carrier: Optional[Carrier] = None
    ):
        """Validate an address"""

        return self._get_carrier_client(
            carrier=carrier
        ).validate_address(
            street_lines=street_lines,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )

    def time_in_transit(
            self,
            from_state: str,
            from_postal_code: str,
            from_country: str,
            to_state: str,
            to_postal_code: str,
            to_country: str,
            weight: str,
            carrier: Optional[Carrier] = None
    ):
        """Get estimated time in transit information"""

        return self._get_carrier_client(
            carrier=carrier
        ).time_in_transit(
            from_state=from_state,
            from_postal_code=from_postal_code,
            from_country=from_country,
            to_state=to_state,
            to_postal_code=to_postal_code,
            to_country=to_country,
            weight=weight,
        )
