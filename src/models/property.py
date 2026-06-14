"""Property listing data model — the canonical representation of a scraped property."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, Field, computed_field, field_validator


class PropertyListing(BaseModel):
    """Pydantic model for a single property listing.

    All scraped property data must be validated through this model
    before being stored or exported. See docs/data-schema.md for
    the full field specification.
    """

    # --- Required fields ---
    id: str = Field(..., description="Unique identifier (source_listingId)")
    source: str = Field(..., description="Source website name")
    title: str = Field(..., description="Listing title")
    price_idr: int = Field(..., ge=0, description="Price in IDR (full number)")
    url: str = Field(..., description="Full URL to the listing page")
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this listing was scraped (UTC)",
    )

    # --- Location fields ---
    address: str | None = Field(default=None, description="Full address string")
    city: str | None = Field(default=None, description="City name")
    district: str | None = Field(default=None, description="District/Kecamatan")
    latitude: float | None = Field(default=None, description="Listing latitude")
    longitude: float | None = Field(default=None, description="Listing longitude")

    # --- Property details ---
    property_type: str | None = Field(default=None, description="rumah, apartemen, dll")
    listing_type: str | None = Field(default=None, description="dijual, disewa")
    land_area_m2: float | None = Field(default=None, ge=0, description="Land area (m²)")
    building_area_m2: float | None = Field(default=None, ge=0, description="Building area (m²)")
    bedrooms: int | None = Field(default=None, ge=0, description="Number of bedrooms")
    bathrooms: int | None = Field(default=None, ge=0, description="Number of bathrooms")
    floors: int | None = Field(default=None, ge=0, description="Number of floors")
    garage: int | None = Field(default=None, ge=0, description="Car spaces")
    certificate: str | None = Field(default=None, description="SHM, HGB, etc.")
    condition: str | None = Field(default=None, description="baru, bekas")
    year_built: int | None = Field(default=None, description="Year built")

    # --- Additional info ---
    description: str | None = Field(default=None, description="Full description text")
    images: list[str] = Field(default_factory=list, description="Image URLs")
    agent_name: str | None = Field(default=None, description="Listing agent name")
    agent_phone: str | None = Field(default=None, description="Agent phone number")

    # --- Distance (set after scraping, during processing) ---
    distance_from_center_km: float | None = Field(default=None, description="Distance from search center")

    # --- Price abbreviation patterns ---
    _PRICE_PATTERNS: ClassVar[dict[str, int]] = {
        "triliun": 1_000_000_000_000,
        "t": 1_000_000_000_000,
        "miliar": 1_000_000_000,
        "milyar": 1_000_000_000,
        "m": 1_000_000_000,
        "juta": 1_000_000,
        "jt": 1_000_000,
    }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def price_per_m2_land(self) -> float | None:
        """Calculate price per m² of land area."""
        if self.price_idr and self.land_area_m2 and self.land_area_m2 > 0:
            return round(self.price_idr / self.land_area_m2, 2)
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def price_per_m2_building(self) -> float | None:
        """Calculate price per m² of building area."""
        if self.price_idr and self.building_area_m2 and self.building_area_m2 > 0:
            return round(self.price_idr / self.building_area_m2, 2)
        return None

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        """Strip and normalize whitespace in title."""
        return " ".join(v.split()).strip()

    @field_validator("property_type")
    @classmethod
    def normalize_property_type(cls, v: str | None) -> str | None:
        """Normalize property type to lowercase."""
        if v is None:
            return None
        return v.lower().strip()

    @staticmethod
    def parse_indonesian_price(price_text: str) -> int:
        """Parse Indonesian price text to an integer value in IDR.

        Handles formats like:
        - "Rp 850 Jt" → 850_000_000
        - "Rp 1,2 M" → 1_200_000_000
        - "Rp 850.000.000" → 850_000_000
        - "1.2 Miliar" → 1_200_000_000

        Args:
            price_text: Raw price string from a listing.

        Returns:
            Price as integer in IDR.

        Raises:
            ValueError: If the price text cannot be parsed.
        """
        if not price_text:
            raise ValueError("Empty price text")

        # Remove "Rp", currency symbols, and whitespace normalization
        cleaned = price_text.lower().strip()
        cleaned = re.sub(r"rp\.?\s*", "", cleaned)
        cleaned = cleaned.strip()

        # Check for abbreviation-based format (e.g., "850 jt", "1,2 m")
        for abbr, multiplier in PropertyListing._PRICE_PATTERNS.items():
            pattern = rf"([\d.,]+)\s*{re.escape(abbr)}"
            match = re.search(pattern, cleaned)
            if match:
                val_str = match.group(1)
                if val_str.count(".") == 1 and val_str.count(",") == 0:
                    # Single dot is decimal separator
                    num_str = val_str
                else:
                    num_str = val_str.replace(".", "").replace(",", ".")
                return int(float(num_str) * multiplier)

        # Try direct number format (e.g., "850.000.000" or "850000000")
        num_str = re.sub(r"[^\d.]", "", cleaned)
        # Indonesian thousand separators use dots
        if num_str.count(".") >= 2:
            num_str = num_str.replace(".", "")
        if num_str:
            return int(float(num_str))

        raise ValueError(f"Cannot parse price: '{price_text}'")
