from abc import ABC, abstractmethod


class GuestServiceStrategy(ABC):
    """
    Unified strategy for all guest services - discounts, payments, and invoice delivery.
    Replaces DiscountStrategy, PaymentStrategy, and DeliveryStrategy patterns.
    """

    @abstractmethod
    def get_discount_percentage(self, guest):
        """Calculate discount percentage for the guest."""
        pass

    @abstractmethod
    def calculate_payment_per_installment(self, total_price, installments):
        """Calculate payment per installment (including additional payment discounts)."""
        pass

    @abstractmethod
    def send_invoice(self, guest, invoice_text):
        """Send invoice to guest contact."""
        pass

    @abstractmethod
    def get_service_description(self):
        """Get description of services provided to this guest type."""
        pass


class VIPGuestServiceStrategy(GuestServiceStrategy):
    """Full service strategy for VIP guests."""

    def get_discount_percentage(self, guest):
        """VIP guests receive a fixed 20% discount."""
        return 20.0

    def calculate_payment_per_installment(self, total_price, installments):
        """VIP guests get additional 5% discount on payment."""
        vip_price = total_price * 0.95  # Additional 5% VIP payment discount
        return vip_price / installments

    def send_invoice(self, guest, invoice_text):
        """VIP personalized invoice delivery service."""
        print(f"📧 VIP Personal Service: Sending invoice to {guest.contact}")
        print("🎁 VIP Benefits and perks included")
        print(invoice_text)

    def get_service_description(self):
        return "VIP: 20% discount + premium payment terms + personal service"


class MemberGuestServiceStrategy(GuestServiceStrategy):
    """Service strategy for member guests with loyalty points."""

    def get_discount_percentage(self, guest):
        """Member discount based on loyalty points: 10% base + points/10, max 25%."""
        return min(25.0, 10.0 + guest.points // 10)

    def calculate_payment_per_installment(self, total_price, installments):
        """Member guests get additional 2% payment discount."""
        member_price = total_price * 0.98  # Additional 2% member payment discount
        return member_price / installments

    def send_invoice(self, guest, invoice_text):
        """Member service with points information."""
        print(f"📧 Member Service: Sending invoice to {guest.contact}")
        print(f"🏆 Your current loyalty points: {guest.points}")
        print(invoice_text)

    def get_service_description(self):
        return "Member: Points-based discount + installment options + priority service"


class RegularGuestServiceStrategy(GuestServiceStrategy):
    """Basic service strategy for regular guests."""

    def get_discount_percentage(self, guest):
        """Regular guests receive no discount."""
        return 0.0

    def calculate_payment_per_installment(self, total_price, installments):
        """Regular guests pay full price divided by installments."""
        return total_price / installments

    def send_invoice(self, guest, invoice_text):
        """Standard invoice delivery for regular guests."""
        print(f"📧 Standard Service: Sending invoice to {guest.contact}")
        print(invoice_text)

    def get_service_description(self):
        return "Regular: Standard pricing + basic service"