from decimal import Decimal

import pytest

from app.domain import average_rating, can_publish_text_review, is_public_review_state, normalize_name, validate_rating


def test_normalize_name():
    assert normalize_name("  QuietLine Over-Ear Headphones! ") == "quietline over ear headphones"


def test_average_rating():
    assert average_rating([5, 4, 5]) == Decimal("4.7")
    assert average_rating([]) is None


def test_validate_rating():
    with pytest.raises(ValueError):
        validate_rating(0)


def test_publish_rules():
    assert is_public_review_state("published")
    assert not is_public_review_state("draft")
    assert not can_publish_text_review(title="x", body="", rating=5)
    assert can_publish_text_review(title="x", body="ok", rating=4)
