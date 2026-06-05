"""SQLite storage layer — async database operations for property listings."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import aiosqlite

from src.config.settings import DATA_DIR
from src.models.property import PropertyListing

logger = logging.getLogger(__name__)

DB_PATH = DATA_DIR / "hargarumah.db"

# SQL schema for the properties table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    price_idr INTEGER NOT NULL,
    url TEXT NOT NULL,
    scraped_at TEXT NOT NULL,
    address TEXT,
    city TEXT,
    district TEXT,
    latitude REAL,
    longitude REAL,
    property_type TEXT,
    listing_type TEXT,
    land_area_m2 REAL,
    building_area_m2 REAL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    floors INTEGER,
    garage INTEGER,
    certificate TEXT,
    condition TEXT,
    year_built INTEGER,
    description TEXT,
    images TEXT,  -- JSON array
    agent_name TEXT,
    agent_phone TEXT,
    distance_from_center_km REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_properties_source ON properties(source);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_district ON properties(district);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price_idr);
"""


class Database:
    """Async SQLite database for storing scraped property listings.

    Provides CRUD operations with automatic schema creation
    and deduplication on insert.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Open database connection and ensure schema exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        await self._db.executescript(CREATE_TABLE_SQL + CREATE_INDEX_SQL)
        await self._db.commit()
        logger.info("Database connected: %s", self.db_path)

    async def close(self) -> None:
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            logger.info("Database connection closed")

    async def save_listing(self, listing: PropertyListing) -> bool:
        """Save a property listing to the database (upsert).

        Args:
            listing: Validated PropertyListing to save.

        Returns:
            True if a new row was inserted, False if updated existing.
        """
        if not self._db:
            raise RuntimeError("Database not connected. Call connect() first.")

        data = listing.model_dump()
        data["scraped_at"] = data["scraped_at"].isoformat()
        data["images"] = json.dumps(data.get("images", []))

        # Remove computed fields (they're re-calculated on read)
        data.pop("price_per_m2_land", None)
        data.pop("price_per_m2_building", None)

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        update_set = ", ".join([f"{k} = excluded.{k}" for k in data if k != "id"])

        sql = f"""
            INSERT INTO properties ({columns})
            VALUES ({placeholders})
            ON CONFLICT(id) DO UPDATE SET {update_set}
        """

        cursor = await self._db.execute(sql, list(data.values()))
        await self._db.commit()

        is_insert = cursor.rowcount == 1
        logger.debug(
            "%s listing: %s (%s)",
            "Inserted" if is_insert else "Updated",
            listing.id,
            listing.source,
        )
        return is_insert

    async def save_many(self, listings: list[PropertyListing]) -> int:
        """Save multiple listings to the database.

        Args:
            listings: List of validated PropertyListing objects.

        Returns:
            Number of new listings inserted.
        """
        inserted = 0
        for listing in listings:
            if await self.save_listing(listing):
                inserted += 1
        logger.info("Saved %d listings (%d new)", len(listings), inserted)
        return inserted

    async def get_all_listings(self, source: str | None = None) -> list[dict]:
        """Retrieve all listings from the database.

        Args:
            source: Optional filter by source website name.

        Returns:
            List of listing dictionaries.
        """
        if not self._db:
            raise RuntimeError("Database not connected. Call connect() first.")

        if source:
            cursor = await self._db.execute(
                "SELECT * FROM properties WHERE source = ? ORDER BY scraped_at DESC",
                (source,),
            )
        else:
            cursor = await self._db.execute(
                "SELECT * FROM properties ORDER BY scraped_at DESC"
            )

        columns = [desc[0] for desc in cursor.description]
        rows = await cursor.fetchall()

        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Parse images JSON back to list
            if row_dict.get("images"):
                row_dict["images"] = json.loads(row_dict["images"])
            results.append(row_dict)

        return results

    async def count(self, source: str | None = None) -> int:
        """Count total listings in the database.

        Args:
            source: Optional filter by source website name.

        Returns:
            Number of listings.
        """
        if not self._db:
            raise RuntimeError("Database not connected. Call connect() first.")

        if source:
            cursor = await self._db.execute(
                "SELECT COUNT(*) FROM properties WHERE source = ?", (source,)
            )
        else:
            cursor = await self._db.execute("SELECT COUNT(*) FROM properties")

        result = await cursor.fetchone()
        return result[0] if result else 0

    async def __aenter__(self) -> Database:
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
