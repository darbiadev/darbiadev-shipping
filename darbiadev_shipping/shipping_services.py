#!/usr/bin/env python

import re
from typing import Optional

from darbiadev_shipping.fedex import FedExClient
from darbiadev_shipping.ups import UPSClient
from darbiadev_shipping.usps import USPSClient


class ShippingServices:
    """
    A class wrapping multiple packages
    """

    def __init__(
            self,
            ups_auth: Optional[dict[str, str]] = None,
            fedex_auth: Optional[dict[str, str]] = None,
            usps_auth: Optional[dict[str, str]] = None
    ):
        self.ups_client: Optional[UPSClient] = UPSClient(ups_auth) if ups_auth is not None else None
        self.fedex_client: Optional[FedExClient] = FedExClient(fedex_auth) if fedex_auth is not None else None
        self.usps_client: Optional[USPSClient] = USPSClient(usps_auth) if fedex_auth is not None else None

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
            raise ValueError(f'Invalid Service: {service}')
