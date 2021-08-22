# darbiadev-shipping

A package wrapping multiple shipping carrier API wrapping packages, providing a higher level multi carrier package.

Documentation is hosted [here](https://darbiadev.github.io/darbiadev-shipping/)

Example usage:
```python
from darbiadev_shipping import ShippingServices

client = ShippingServices(
    ups_auth={
        'base_url': '',
        'username': '',
        'password': '',
        'access_license_number': '',
    },
    fedex_auth={
        'web_service_url': '',
        'key': '',
        'password': '',
        'account_number': '',
        'meter_number': '',
    },
    usps_auth={
        'base_url': '',
        'user_id': '',
        'password': '',
    }
)

print(client.track('1Z5338FF0107231059'))
```
