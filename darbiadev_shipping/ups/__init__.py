#!/usr/bin/env python

from darbiadev_ups.ups_services import UPSServices

from darbiadev_shipping.ups.helpers import parse_tracking_response


class UPSClient:
    """
    A class parsing UPS' responses.
    """

    def __init__(
            self,
            ups_auth: dict[str, str]
    ):
        self._client: UPSServices = UPSServices(**ups_auth)

    def track(
            self,
            tracking_number: str
    ):
        response = self._client.track(tracking_number=tracking_number)
        return parse_tracking_response(response)
