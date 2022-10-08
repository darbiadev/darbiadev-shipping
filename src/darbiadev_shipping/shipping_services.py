"""shipping_services"""

from __future__ import annotations

import importlib
import re
from enum import Enum, auto


class CarrierEnum(Enum):
    """An enum of shipping carriers"""

    UPS = auto()
    FEDEX = auto()
    USPS = auto()


class Carrier:  # pylint: disable=too-few-public-methods
    """A shipping carrier"""

    def __init__(
        self,
        name: str,
        client_package: str,
        client_class: str,
        auth_dict: dict[str, str],
    ) -> None:
        self.name: str = name

        try:
            module = importlib.import_module(client_package)
            class_ = getattr(module, client_class)
            self.client = class_(**auth_dict)
        except ImportError as error:
            raise ImportError(f"Install {client_package.split('.')[0]} for {name} support") from error


class CarrierRegistrar:  # pylint: disable=too-few-public-methods
    """A registrar for carriers"""

    def __init__(self) -> None:
        self.carriers: dict[CarrierEnum, Carrier] = {}

    def register_carrier(
        self,
        carrier_enum: CarrierEnum,
        name: str,
        client_package: str,
        client_class: str,
        auth_dict: dict[str, str] | None,
    ) -> None:
        """Register carrier in the registrar"""

        if auth_dict is not None:
            self.carriers.update(
                {
                    carrier_enum: Carrier(
                        name=name,
                        client_package=client_package,
                        client_class=client_class,
                        auth_dict=auth_dict,
                    )
                }
            )


class ShippingServices:
    """
    A class wrapping multiple shipping carrier API wrapping packages, providing a higher level multi carrier package.
    """

    def __init__(
        self,
        ups_auth: dict[str, str] | None = None,
        fedex_auth: dict[str, str] | None = None,
        usps_auth: dict[str, str] | None = None,
    ):
        auth_dicts: list[dict[str, str]] = [value for key, value in locals().items() if key.endswith("_auth")]
        at_least_one_carrier_enabled = any(value is not None for value in auth_dicts)
        if not at_least_one_carrier_enabled:
            raise ValueError("No carriers are enabled. Please enable at least one carrier to use this package.")

        self.carrier_registrar = CarrierRegistrar()

        self.carrier_registrar.register_carrier(
            carrier_enum=CarrierEnum.UPS,
            name="UPS",
            client_package="darbiadev_ups",
            client_class="UPSServices",
            auth_dict=ups_auth,
        )

        self.carrier_registrar.register_carrier(
            carrier_enum=CarrierEnum.FEDEX,
            name="FedEx",
            client_package="darbiadev_fedex.fedex_services",
            client_class="FedExServices",
            auth_dict=fedex_auth,
        )

        self.carrier_registrar.register_carrier(
            carrier_enum=CarrierEnum.USPS,
            name="USPS",
            client_package="darbiadev_usps.usps_services",
            client_class="USPSServices",
            auth_dict=usps_auth,
        )

    def _get_carrier_from_registrar(
        self,
        carrier_enum: CarrierEnum | None = None,
    ) -> Carrier:
        """Get a carrier from the registrar"""

        if carrier_enum is not None:
            carrier = self.carrier_registrar.carriers.get(carrier_enum, None)
            if carrier is None:
                raise ValueError(f"{carrier_enum} is not enabled.")
        else:
            carrier = list(self.carrier_registrar.carriers.values())[0]

        if carrier is None:
            raise ValueError("No suitable carrier found")

        return carrier

    def guess_carrier(self, tracking_number: str) -> CarrierEnum | None:
        """
        Guess which carrier a tracking number belongs to

        Parameters
        ----------
        tracking_number
            The tracking number to guess a carrier for.

        Returns
        -------
        CarrierEnum|None
            The carrier the tracking number belongs to.
        """

        for carrier_enum, carrier in self.carrier_registrar.carriers.items():
            if re.match(carrier.client.TRACKING_REGEX, tracking_number):
                return carrier_enum

        return None

    def track(
        self,
        tracking_number: str,
        carrier_enum: CarrierEnum | None = None,
    ) -> dict:
        """Get details for tracking number"""

        if carrier_enum is None:
            carrier_enum = self.guess_carrier(tracking_number)

        if carrier_enum is None:
            raise ValueError(f"Unable to guess carrier for tracking number {tracking_number}")

        client = self._get_carrier_from_registrar(carrier_enum=carrier_enum).client

        return client.track(tracking_number=tracking_number)

    def validate_address(
        self,
        street_lines: list[str],
        city: str,
        state: str,
        postal_code: str,
        country: str,
        carrier_enum: CarrierEnum | None = None,
    ):
        """Validate an address"""

        client = self._get_carrier_from_registrar(carrier_enum=carrier_enum).client

        return client.validate_address(
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
        carrier_enum: CarrierEnum | None = None,
    ):
        """Get estimated time in transit information"""

        client = self._get_carrier_from_registrar(carrier_enum=carrier_enum).client

        return client.time_in_transit(
            from_state=from_state,
            from_postal_code=from_postal_code,
            from_country=from_country,
            to_state=to_state,
            to_postal_code=to_postal_code,
            to_country=to_country,
            weight=weight,
        )
