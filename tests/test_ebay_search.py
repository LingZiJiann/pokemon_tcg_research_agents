from unittest.mock import MagicMock, patch

import pytest

from src.tools.ebay_search import EbaySearch


class TestTitleContainsCondition:
    """Test suite for _title_contains_condition method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ebay_search = EbaySearch(api_key="test_key")

    def test_condition_found_in_title(self):
        """Test when condition is present in title."""
        result = self.ebay_search._title_contains_condition(
            "Charizard NM Pokemon Card", "NM"
        )
        assert result is True

    def test_condition_case_insensitive(self):
        """Test that condition matching is case-insensitive."""
        assert (
            self.ebay_search._title_contains_condition(
                "Charizard nm Pokemon Card", "NM"
            )
            is True
        )
        assert (
            self.ebay_search._title_contains_condition(
                "Charizard NM Pokemon Card", "nm"
            )
            is True
        )
        assert (
            self.ebay_search._title_contains_condition(
                "Charizard Nm Pokemon Card", "nM"
            )
            is True
        )

    def test_condition_not_found_in_title(self):
        """Test when condition is not present in title."""
        result = self.ebay_search._title_contains_condition(
            "Charizard Pokemon Card", "NM"
        )
        assert result is False

    def test_condition_at_beginning_of_title(self):
        """Test condition at the beginning of title."""
        result = self.ebay_search._title_contains_condition(
            "NM Charizard Pokemon Card", "NM"
        )
        assert result is True

    def test_condition_at_end_of_title(self):
        """Test condition at the end of title."""
        result = self.ebay_search._title_contains_condition(
            "Charizard Pokemon Card NM", "NM"
        )
        assert result is True

    def test_condition_as_whole_title(self):
        """Test when condition is the whole title."""
        result = self.ebay_search._title_contains_condition("NM", "NM")
        assert result is True

    def test_empty_title(self):
        """Test with empty title string."""
        result = self.ebay_search._title_contains_condition("", "NM")
        assert result is False

    def test_none_title(self):
        """Test with None title."""
        result = self.ebay_search._title_contains_condition("", "NM")
        assert result is False

    def test_various_conditions(self):
        """Test various common Pokemon card conditions."""
        test_cases = [
            ("Pikachu LP Pokemon", "LP", True),
            ("Blastoise MP card", "MP", True),
            ("Gengar HP damaged", "HP", True),
            ("Articuno DMG condition", "DMG", True),
            ("Alakazam PSA 10", "PSA 10", True),
            ("Charizard BGS 9.5 card", "BGS 9.5", True),
            ("Meowth NM-MT condition", "NM-MT", True),
        ]

        for title, condition, expected in test_cases:
            result = self.ebay_search._title_contains_condition(title, condition)
            assert result is expected, (
                f"Failed for title='{title}', condition='{condition}'"
            )


class TestParseListing:
    """Test suite for _parse_listing method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ebay_search = EbaySearch(api_key="test_key")

    def test_parse_listing_with_all_fields(self):
        """Test parsing listing with all fields present."""
        raw_result = {
            "link": "https://ebay.com/item/123",
            "title": "Charizard NM Pokemon Card",
            "price": {"extracted": 150.00},
            "sold_date": "2024-05-01",
        }

        parsed = self.ebay_search._parse_listing(raw_result)

        assert parsed["url"] == "https://ebay.com/item/123"
        assert parsed["title"] == "charizard nm pokemon card"
        assert parsed["price"] == 150.00
        assert parsed["sold_date"] == "2024-05-01"

    def test_parse_listing_with_missing_fields(self):
        """Test parsing listing with missing optional fields."""
        raw_result = {"link": "https://ebay.com/item/456", "title": "Blastoise LP Card"}

        parsed = self.ebay_search._parse_listing(raw_result)

        assert parsed["url"] == "https://ebay.com/item/456"
        assert parsed["title"] == "blastoise lp card"
        assert parsed["price"] is None
        assert parsed["sold_date"] is None

    def test_parse_listing_empty_price_dict(self):
        """Test parsing listing with empty price dictionary."""
        raw_result = {
            "link": "https://ebay.com/item/789",
            "title": "Meowth Raw Card",
            "price": {},
        }

        parsed = self.ebay_search._parse_listing(raw_result)

        assert parsed["price"] is None
