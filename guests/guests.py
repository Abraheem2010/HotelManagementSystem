def _get_factory():
    from system.universal_factory import UniversalEntityFactory
    return UniversalEntityFactory


class Guest:
    """
    Represents a generic guest in the hotel system.

    Uses composition to apply discount and payment strategies through GuestServiceStrategy.
    """

    def __init__(self, guest_id, name, contact, status="regular", points=0):
        """
        Initialize a Guest object.

        Args:
            guest_id (int): Unique identifier for the guest.
            name (str): Guest's full name.
            contact (str): Contact information.
            status (str): Guest type ("regular", "vip", "member").
            points (int): Loyalty points (for member guests).
        """
        self.guest_id = guest_id
        self.name = name
        self.contact = contact
        self.status = status.lower()
        self.points = points

        # Service strategy will be created externally when needed
        self.service_strategy = None  # Will be set by UniversalEntityFactory when needed

    def _ensure_strategy(self):
        if not self.service_strategy:
            self.service_strategy = _get_factory().create_guest_service_strategy(self)

    def calculate_payment(self, base_price, installments=1):
        """
        Calculate final payment using service strategy.

        Args:
            base_price (float): Base price before discounts.
            installments (int): Number of installments for payment.

        Returns:
            float: Payment amount per installment.
        """
        self._ensure_strategy()
        return self.service_strategy.calculate_payment_per_installment(base_price, installments)

    def get_final_price(self, base_price):
        """
        Apply discount and return final price.

        Args:
            base_price (float): Original price before discount.

        Returns:
            float: Final price after applying discount.
        """
        self._ensure_strategy()
        discount_percent = self.service_strategy.get_discount_percentage(self)
        return base_price * (1 - discount_percent / 100)

    def explain_discount(self):
        """
        Return textual explanation of the discount and services applied.

        Returns:
            str: Description of guest services and discounts.
        """
        self._ensure_strategy()
        return self.service_strategy.get_service_description()

    def add_points(self, nights):
        """
        Add loyalty points (used only for member guests).

        Args:
            nights (int): Number of nights stayed to calculate points.
        """
        if self.status == "member":
            self.points += nights * 10

    def get_guest_type(self):
        """
        Return guest type as string.

        Returns:
            str: Capitalized guest type.
        """
        return self.status.capitalize()

    def to_dict(self):
        """
        Return a dictionary representation of the guest.

        Returns:
            dict: Guest data as dictionary.
        """
        data = {
            "guest_id": self.guest_id,
            "name": self.name,
            "contact": self.contact,
            "guest_type": self.get_guest_type(),
        }
        if self.status == "member":
            data["points"] = self.points
        return data

    def update_guest(self, name=None, contact=None):
        """
        Update name or contact info.

        Args:
            name (str, optional): New name for the guest.
            contact (str, optional): New contact information.
        """
        if name:
            self.name = name
        if contact:
            self.contact = contact

    def get_discount_percentage(self):
        """
        Return the guest's discount percentage as float.

        Returns:
            float: Discount percentage for this guest type.
        """
        self._ensure_strategy()
        return self.service_strategy.get_discount_percentage(self)

    def send_invoice(self, invoice_text):
        """
        Send invoice to guest using their service strategy.

        Args:
            invoice_text (str): The invoice content to send.
        """
        self._ensure_strategy()
        self.service_strategy.send_invoice(self, invoice_text)

    def __str__(self):
        """
        String representation of the guest.

        Returns:
            str: Formatted guest information.
        """
        return f"{self.get_guest_type()} Guest {self.guest_id}: {self.name}, Contact: {self.contact}"


# ------------------------------
# Subclasses to demonstrate inheritance and polymorphism
# ------------------------------

class VIPGuest(Guest):
    """
    Subclass representing a VIP guest with premium services.
    """

    def __init__(self, guest_id, name, contact):
        """
        Initialize a VIP guest.

        Args:
            guest_id (int): Unique identifier for the guest.
            name (str): Guest's full name.
            contact (str): Contact information.
        """
        super().__init__(guest_id, name, contact, status="vip")


class MemberGuest(Guest):
    """
    Subclass representing a member guest with loyalty points.
    """

    def __init__(self, guest_id, name, contact, points=0):
        """
        Initialize a member guest.

        Args:
            guest_id (int): Unique identifier for the guest.
            name (str): Guest's full name.
            contact (str): Contact information.
            points (int): Initial loyalty points.
        """
        super().__init__(guest_id, name, contact, status="member", points=points)


class RegularGuest(Guest):
    """
    Subclass representing a regular guest with standard services.
    """

    def __init__(self, guest_id, name, contact):
        """
        Initialize a regular guest.

        Args:
            guest_id (int): Unique identifier for the guest.
            name (str): Guest's full name.
            contact (str): Contact information.
        """
        super().__init__(guest_id, name, contact, status="regular")