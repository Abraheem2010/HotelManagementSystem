"""Unit tests for GuestServiceStrategy implementations (VIP, Member, Regular)."""

import unittest
import contextlib
import io

from guests.guest_service_strategy import (
    VIPGuestServiceStrategy,
    MemberGuestServiceStrategy,
    RegularGuestServiceStrategy,
)


class DummyGuest:
    """Minimal guest stub."""

    def __init__(self, guest_id, contact, points=0):
        self.guest_id = guest_id
        self.contact = contact
        self.points = points


# ------------------------- VIP ------------------------- #
class TestVIPGuestServiceStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = VIPGuestServiceStrategy()
        self.guest = DummyGuest(1, "vip@example.com")

    def test_discount_percentage(self):
        self.assertEqual(self.strategy.get_discount_percentage(self.guest), 20.0)

    def test_payment_per_installment(self):
        total, installments = 1000, 5
        expected = (total * 0.95) / installments  # extra 5% VIP discount
        self.assertAlmostEqual(
            self.strategy.calculate_payment_per_installment(total, installments),
            expected,
        )

    def test_service_description(self):
        self.assertIn("VIP", self.strategy.get_service_description())

    def test_send_invoice_prints(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.strategy.send_invoice(self.guest, "Invoice Text")
        out = buf.getvalue()
        self.assertIn("VIP Personal Service", out)
        self.assertIn("Invoice Text", out)


# ----------------------- Member ------------------------ #
class TestMemberGuestServiceStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MemberGuestServiceStrategy()
        self.guest = DummyGuest(2, "mem@example.com", points=50)

    def test_discount_percentage_with_points(self):
        self.assertEqual(self.strategy.get_discount_percentage(self.guest), 15.0)

    def test_discount_percentage_cap(self):
        rich_guest = DummyGuest(3, "rich@example.com", points=300)  # capped at 25%
        self.assertEqual(self.strategy.get_discount_percentage(rich_guest), 25.0)

    def test_payment_per_installment(self):
        total, installments = 500, 2
        expected = (total * 0.98) / installments  # 2% discount
        self.assertAlmostEqual(
            self.strategy.calculate_payment_per_installment(total, installments),
            expected,
        )

    def test_service_description(self):
        desc = self.strategy.get_service_description().lower()
        self.assertIn("member", desc)
        self.assertIn("points", desc)

    def test_send_invoice_includes_points(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.strategy.send_invoice(self.guest, "Invoice Text")
        self.assertIn("loyalty points", buf.getvalue())


# ----------------------- Regular ----------------------- #
class TestRegularGuestServiceStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = RegularGuestServiceStrategy()
        self.guest = DummyGuest(4, "reg@example.com")

    def test_discount_percentage(self):
        self.assertEqual(self.strategy.get_discount_percentage(self.guest), 0.0)

    def test_payment_per_installment(self):
        total, installments = 300, 3
        expected = total / installments
        self.assertEqual(
            self.strategy.calculate_payment_per_installment(total, installments),
            expected,
        )

    def test_service_description(self):
        self.assertIn("Regular", self.strategy.get_service_description())

    def test_send_invoice_standard(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.strategy.send_invoice(self.guest, "Invoice Text")
        self.assertIn("Standard Service", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
