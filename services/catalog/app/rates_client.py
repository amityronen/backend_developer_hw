import logging
from decimal import Decimal

import requests

from app.config import get_settings

logger = logging.getLogger("catalog.rates")


def fetch_usd_rate() -> Decimal | None:
    """Return the ILS->USD rate, or None when the provider cannot be reached."""
    url = f"{get_settings().rates_url}/rates"
    try:
        response = requests.get(url, params={"base": "ILS"})
        response.raise_for_status()
        return Decimal(response.json()["rates"]["USD"])
    except (requests.RequestException, KeyError, ValueError) as exc:
        logger.warning("rates lookup failed: %s", exc)
        return None
