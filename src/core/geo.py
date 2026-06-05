"""Geo utilities — coordinate-to-area-name mapping and distance calculations."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from geopy.distance import geodesic
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

# Known area mappings for common Indonesian property search locations.
# These map to the URL slugs used by various property websites.
BEKASI_AREAS: dict[str, tuple[float, float]] = {
    "bekasi-selatan": (-6.2607, 106.9894),
    "bekasi-barat": (-6.2350, 106.9650),
    "bekasi-timur": (-6.2486, 107.0181),
    "bekasi-utara": (-6.2100, 106.9900),
    "rawalumbu": (-6.2847, 107.0060),
    "pondok-gede": (-6.2900, 106.9100),
    "jatiasih": (-6.3100, 106.9600),
    "bantargebang": (-6.3300, 106.9900),
    "mustika-jaya": (-6.3200, 107.0200),
    "medan-satria": (-6.1900, 106.9700),
    "pondok-melati": (-6.2900, 106.9300),
    "jatisampurna": (-6.3500, 106.9200),
}


@dataclass
class AreaInfo:
    """Information about a geographic area relevant for property search."""

    name: str
    slug: str  # URL-safe name used in website paths
    latitude: float
    longitude: float
    distance_km: float  # Distance from search center


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the great-circle distance between two points (in km).

    Args:
        lat1: Latitude of point 1.
        lng1: Longitude of point 1.
        lat2: Latitude of point 2.
        lng2: Longitude of point 2.

    Returns:
        Distance in kilometers.
    """
    return geodesic((lat1, lng1), (lat2, lng2)).km


def find_areas_within_radius(
    center_lat: float,
    center_lng: float,
    radius_km: float,
    area_map: dict[str, tuple[float, float]] | None = None,
) -> list[AreaInfo]:
    """Find known areas within a given radius from the center point.

    Args:
        center_lat: Center point latitude.
        center_lng: Center point longitude.
        radius_km: Search radius in kilometers.
        area_map: Dictionary of area slugs to (lat, lng) coordinates.
                  Defaults to BEKASI_AREAS.

    Returns:
        List of AreaInfo objects within the radius, sorted by distance.
    """
    if area_map is None:
        area_map = BEKASI_AREAS

    results: list[AreaInfo] = []
    for slug, (lat, lng) in area_map.items():
        distance = haversine_distance(center_lat, center_lng, lat, lng)
        if distance <= radius_km:
            results.append(
                AreaInfo(
                    name=slug.replace("-", " ").title(),
                    slug=slug,
                    latitude=lat,
                    longitude=lng,
                    distance_km=round(distance, 2),
                )
            )

    results.sort(key=lambda a: a.distance_km)
    logger.info(
        "Found %d areas within %.1f km of (%.4f, %.4f)",
        len(results), radius_km, center_lat, center_lng,
    )
    return results


async def reverse_geocode(lat: float, lng: float) -> str | None:
    """Reverse geocode coordinates to get a human-readable location name.

    Uses Nominatim (OpenStreetMap) — free, no API key needed.

    Args:
        lat: Latitude.
        lng: Longitude.

    Returns:
        Location name string, or None if geocoding fails.
    """
    try:
        geolocator = Nominatim(user_agent="hargarumah-scraper/0.1")
        location = geolocator.reverse(f"{lat}, {lng}", language="id")
        if location:
            return str(location.address)
    except Exception as e:
        logger.warning("Reverse geocoding failed for (%.4f, %.4f): %s", lat, lng, e)
    return None
