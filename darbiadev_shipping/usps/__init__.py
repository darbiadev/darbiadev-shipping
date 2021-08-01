#!/usr/bin/env python

from darbiadev_usps.usps_services import USPSServices

from darbiadev_shipping.usps.helpers import parse_tracking_response


class USPSClient:
    """
    A class parsing USPS' responses.
    """

    def __init__(
            self,
            usps_auth: dict[str, str]
    ):
        self._client: USPSServices = USPSServices(**usps_auth)

    def track(
            self,
            tracking_number: str
    ):
        response = self._client.track(tracking_number=tracking_number)
        return parse_tracking_response(response)
