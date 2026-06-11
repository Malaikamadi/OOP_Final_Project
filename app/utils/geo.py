import math
from typing import Optional


EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance (km) between two GPS coordinates
    using the Haversine formula.
    """
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def filter_by_radius(clinics, user_lat: float, user_lon: float, radius_km: float):
    """
    Filter a list of clinic ORM objects by GPS radius and attach
    a `distance_km` attribute to each result.

    Returns a list of (clinic, distance_km) tuples sorted by distance ascending.
    """
    results = []
    for clinic in clinics:
        if clinic.latitude is None or clinic.longitude is None:
            continue
        dist = haversine_distance(
            user_lat, user_lon, float(clinic.latitude), float(clinic.longitude)
        )
        if dist <= radius_km:
            results.append((clinic, dist))

    results.sort(key=lambda x: x[1])
    return results
