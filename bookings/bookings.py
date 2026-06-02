import datetime


class Booking:
    """
    Represents a booking in the hotel management system.

    Attributes:
        booking_id (int): Unique identifier for the booking.
        guest (Guest): The guest who made the booking.
        room (Room): The room assigned for the booking.
        check_in (date): Check-in date.
        check_out (date): Check-out date.
        status (str): Current status of the booking (e.g., confirmed, checked-in).
        paid (bool): Indicates whether the booking has been paid.
        installments (int): Number of installments chosen for payment.
    """

    def __init__(self, booking_id, guest, room, check_in, check_out, status='confirmed', paid=False, installments=1):
        """
        Initialize a Booking instance.

        Args:
            booking_id (int): Unique ID for the booking.
            guest (Guest): Guest object.
            room (Room): Room object.
            check_in (str or date): Check-in date.
            check_out (str or date): Check-out date.
            status (str, optional): Booking status. Default is 'confirmed'.
            paid (bool, optional): Payment status. Default is False.
            installments (int, optional): Number of installments. Default is 1.
        """
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in = self._to_date(check_in)
        self.check_out = self._to_date(check_out)
        self.status = status
        self.paid = paid
        self.installments = installments

    def _to_date(self, value):
        """
        Convert string to datetime.date if necessary.

        Args:
            value (str or date): Date value to normalize.

        Returns:
            date: Normalized date object.
        """
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()

    def to_dict(self):
        """
        Serialize booking data to dictionary format.

        Returns:
            dict: Booking attributes in dictionary form.
        """
        return {
            "booking_id": self.booking_id,
            "guest_id": self.guest.guest_id,
            "room_number": self.room.room_number,
            "check_in": self.check_in.strftime("%Y-%m-%d"),
            "check_out": self.check_out.strftime("%Y-%m-%d"),
            "status": self.status,
            "paid": self.paid,
            "installments": self.installments
        }

    def update_booking(self, check_in=None, check_out=None, room=None):
        """
        Update booking dates or room assignment.

        Args:
            check_in (str or date, optional): New check-in date.
            check_out (str or date, optional): New check-out date.
            room (Room, optional): New room to assign.
        """
        if check_in:
            self.check_in = self._to_date(check_in)
        if check_out:
            self.check_out = self._to_date(check_out)
        if room:
            self.room = room

    def update_status(self, new_status):
        """
        Change the booking status if valid.

        Args:
            new_status (str): New status value.

        Returns:
            bool: True if status is valid and updated, else False.
        """
        valid_statuses = {'confirmed', 'checked-in', 'checked-out', 'cancelled'}
        if new_status in valid_statuses:
            self.status = new_status
            return True
        return False

    def mark_as_paid(self, paid=True):
        """
        Update the booking's payment status.

        Args:
            paid (bool): New payment status.
        """
        self.paid = paid

    def calculate_nights(self):
        """
        Calculate the number of nights in the booking.

        Returns:
            int: Number of nights.
        """
        return (self.check_out - self.check_in).days

    def __str__(self):
        """
        Return a human-readable summary of the booking.

        Returns:
            str: Summary string.
        """
        return (
            f"Booking {self.booking_id}: Room {self.room.room_number}, Guest {self.guest.name}, "
            f"{self.check_in} to {self.check_out}, Status: {self.status}, "
            f"Paid: {'Yes' if self.paid else 'No'}, Installments: {self.installments}"
        )
