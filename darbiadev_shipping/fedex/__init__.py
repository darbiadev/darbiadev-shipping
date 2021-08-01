#!/usr/bin/env python

from darbiadev_fedex.fedex_services import FedExServices

from darbiadev_shipping.fedex.helpers import parse_tracking_response


class FedExClient:
    """
    A class parsing FedEx's responses.
    """

    def __init__(
            self,
            fedex_auth: dict[str, str]
    ):
        self._client: FedExServices = FedExServices(**fedex_auth)

    def track(
            self,
            tracking_number: str
    ):
        response = self._client.track(tracking_number=tracking_number)
        return parse_tracking_response(response)
