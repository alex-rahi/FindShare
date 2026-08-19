import re
from decimal import ROUND_HALF_UP, Decimal

SUPPORTED_CURRENCIES = frozenset({"USD", "CAD", "EUR", "GBP"})


def normalize_name(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def average_rating(scores: list[int]) -> Decimal | None:
    if not scores:
        return None
    for score in scores:
        validate_rating(score)
    total = sum(Decimal(score) for score in scores)
    return (total / Decimal(len(scores))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def rating_distribution(scores: list[int]) -> dict[int, int]:
    dist = {star: 0 for star in range(1, 6)}
    for score in scores:
        if score not in dist:
            raise ValueError("rating must be between 1 and 5")
        dist[score] += 1
    return dist


def validate_rating(score: int) -> None:
    if score < 1 or score > 5:
        raise ValueError("rating must be between 1 and 5")


def is_public_review_state(state: str) -> bool:
    return state == "published"


def can_publish_text_review(*, title: str, body: str, rating: int | None) -> bool:
    return bool(title.strip()) and bool(body.strip()) and rating is not None and 1 <= rating <= 5
