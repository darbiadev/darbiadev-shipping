#!/usr/bin/env python

import datetime
from typing import Tuple, Union

from benedict import benedict

tracking_url = 'https://wwwapps.ups.com/WebTracking/processInputRequest?TypeOfInquiryNumber=T&InquiryNumber1={tracking_number}'


def parse_tracking_response(response: dict) -> dict:
    data: benedict = benedict(response)

    if result := data.get('TrackResponse.Shipment.Package'):
        return_value = {
            # '_original': response,
            'shipment_references': set(dct['Value'] for dct in (data.get('TrackResponse.Shipment.ReferenceNumber') or [])),
            'packages': dict()
        }

        if not isinstance(result, list):
            result = [result]
        packages: list[dict] = [benedict(r) for r in result]

        for package in packages:
            return_value['packages'][package.get('TrackingNumber')] = {
                'status': package.get('Activity[0].Status.Description'),
                'references': [dct['Value'] for dct in (package.get('ReferenceNumber') or [])]
            }

        return_value['shipment_references'] = list(return_value['shipment_references'])
        return return_value
    elif error := data.get('Fault.detail.Errors.ErrorDetail.PrimaryErrorCode'):
        return {'external_error': error}
    else:
        return {'error': 'unknown response', 'full_response': data}


def validation_fields(av):
    av = benedict(av)
    result = {
        'status': None,
        'classification': '',
        'street_address': '',
        'region': ''
    }

    try:
        if 'ups.address_validation' not in av:
            result['street_address'] = 'SYSTEM ERROR'
            result['region'] = 'Failed to validate address'
            return result

        av = benedict(av['ups.address_validation'])
        if 'response.errors' in av:
            result['street_address'] = 'ERROR(S) VALIDATING ADDRESS'
            result['region'] = [error.get('message') for error in av['response.errors']]
            return result

        if 'XAVResponse.NoCandidatesIndicator' in av:
            result['street_address'] = 'Address unknown'
            result['region'] = 'No candidates'
            return result

        if (av.get('XAVResponse.AddressClassification.Description') or '') == 'Unknown':
            result['street_address'] = 'Address unknown'
            result['region'] = 'No candidates'
            return result

        result['classification'] = av.get('XAVResponse.Candidate.AddressClassification.Description') or 'Unknown'

        candidates = av['XAVResponse.Candidate']
        if not isinstance(candidates, list):
            candidates = [candidates]
        first_candidate = benedict(candidates[0])

        result['classification'] = first_candidate.get('AddressClassification.Description') or 'Unknown'

        street_address = first_candidate['AddressKeyFormat.AddressLine']
        if isinstance(street_address, list):
            result['street_address'] = ' '.join(street_address)
        else:
            result['street_address'] = street_address

        result['region'] = first_candidate['AddressKeyFormat.Region']
        if 'ValidAddressIndicator' in av['XAVResponse']:
            result['status'] = 'Valid'
        return result

    except KeyError:
        result['street_address'] = 'SYSTEM ERROR'
        result['region'] = 'Failed to validate address'
        return result


def time_in_transit(self) -> Union[Tuple[None, list], Tuple[str, list]]:
    tit = benedict(self.custom or dict())
    alert = tit.get('ups.transit_time.TimeInTransitResponse.Response.Alert.Description')
    results = []
    if 'ups.transit_time.TimeInTransitResponse.TransitResponse.ServiceSummary' not in tit:
        return alert, results
    else:
        services = tit.get('ups.transit_time.TimeInTransitResponse.TransitResponse.ServiceSummary')
        for service in services:
            service = benedict(service)

            service_name = service.get('Service.Description')

            d = service.get('EstimatedArrival.Pickup.Date')
            t = service.get('EstimatedArrival.Pickup.Time')
            pickup_time = datetime.datetime.strptime(d + t, '%Y%m%d%H%M%S')

            d = service.get('EstimatedArrival.Arrival.Date')
            t = service.get('EstimatedArrival.Arrival.Time')
            arrival_time = datetime.datetime.strptime(d + t, '%Y%m%d%H%M%S')

            business_days_in_transit = service.get('EstimatedArrival.BusinessDaysInTransit')
            day_of_week = service.get('EstimatedArrival.DayOfWeek')
            customer_center_cutoff = datetime.datetime.strptime(
                service.get('EstimatedArrival.CustomerCenterCutoff'), '%H%M%S').time()

            results.append({
                'service_name': service_name,
                'pickup_time': pickup_time,
                'arrival_time': arrival_time,
                'business_days_in_transit': business_days_in_transit,
                'day_of_week': day_of_week,
                'customer_center_cutoff': customer_center_cutoff
            })

    return alert, results
