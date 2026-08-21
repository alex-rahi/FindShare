from decimal import Decimal

import pytest

from app.domain import (
    assumed_monthly_cost,
    average_rating,
    can_publish_text_review,
    is_public_review_state,
    normalize_money,
    normalize_name,
    validate_rating,
)


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
    assert not is_public_review_state("archived")
    assert not can_publish_text_review(title="x", body="", rating=5)
    assert can_publish_text_review(title="x", body="ok", rating=4)


def test_normalize_money():
    assert normalize_money(Decimal("12.345")) == Decimal("12.35")
    assert normalize_money(None) is None
    with pytest.raises(ValueError):
        normalize_money(Decimal("-1"))
    with pytest.raises(ValueError):
        normalize_money(Decimal("10000001"))


def test_assumed_monthly_cost_is_arithmetic_only():
    assert assumed_monthly_cost(active_users=10, cost_per_active_user=Decimal("1.25")) == Decimal("12.50")
    with pytest.raises(ValueError):
        assumed_monthly_cost(active_users=-1, cost_per_active_user=Decimal("1"))
