"""Optional boundary only; checkout and Stripe SDK integration are deliberately excluded."""
from .mock import MockBillingProvider


class StripeCompatibleProvider(MockBillingProvider):
    name = "stripe-compatible"
