#!/usr/bin/env python

import re
from typing import Optional


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
            except ImportError as e:
                raise ImportError('Install darbiadev-ups for UPS support') from e

        if fedex_auth is not None:
            try:
                from darbiadev_fedex.fedex_services import FedExServices
                self.fedex_client = FedExServices(**fedex_auth)
            except ImportError as e:
                raise ImportError('Install darbiadev-fedex for FedEx support') from e

        if usps_auth is not None:
            try:
                from darbiadev_usps.usps_services import USPSServices
                self.usps_client = USPSServices(**usps_auth)
            except ImportError as e:
                raise ImportError('Install darbiadev-usps for USPS support') from e

    def guess_service(
            self,
            tracking_number: str
    ) -> Optional[str]:
        ups_pattern = re.compile(r'1Z\d*')
        if ups_pattern.match(tracking_number):
            return 'ups'
        return None

    def track(
            self,
            tracking_number: str,
            service: Optional[str] = None
    ) -> dict[str, str]:
        if service is None:
            service = self.guess_service(tracking_number)

        if service == 'ups':
            return self.ups_client.track(tracking_number)
        elif service == 'fedex':
            return self.fedex_client.track(tracking_number)
        elif service == 'usps':
            return self.usps_client.track(tracking_number)
        else:
            raise ValueError(f'Invalid service: {service}')
