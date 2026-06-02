import datetime
from datetime import date
from guests.guests import MemberGuest

from system.universal_factory import UniversalEntityFactory


class BookingService:
    """
    Handles all booking-related operations such as creation,
    updates, cancellations, cost calculation, and availability checking.
    """

    def __init__(self, booking_manager, guest_manager, room_manager, booking_data, guest_data, room_data, room_service):
        """
        Initialize the BookingService with dependencies.
        """
        self.booking_manager = booking_manager
        self.guest_manager = guest_manager
        self.room_manager = room_manager
        self.booking_data = booking_data
        self.guest_data = guest_data
        self.room_data = room_data
        self.room_service = room_service

    def _to_date(self, value):
        """Ensure value is a date object."""
        return value if isinstance(value, datetime.date) else datetime.datetime.strptime(value, "%Y-%m-%d").date()

    def validate_booking_dates(self, room_number, check_in, check_out, exclude_booking_id=None):
        """
        Validate date logic and check if the room is available.

        Args:
            room_number (int): Room number to validate.
            check_in (str or date): Check-in date.
            check_out (str or date): Check-out date.
            exclude_booking_id (int, optional): ID of a booking to exclude from availability check (useful for updates).

        Returns:
            tuple: (bool, str) - True and empty string if valid, False and message if not.
        """
        check_in_date = self._to_date(check_in)
        check_out_date = self._to_date(check_out)
        if check_in_date < date.today():
            return False, "Check-in date cannot be in the past."
        if check_out_date <= check_in_date:
            return False, "Check-out date must be after check-in date."
        is_available, message = self.check_room_availability(
            room_number, check_in_date, check_out_date, exclude_booking_id=exclude_booking_id
        )
        if not is_available:
            return False, message
        return True, ""

    def create_booking(self, booking_id, guest_id, room_number, check_in, check_out, installments=1):
        """
        Create a booking if data is valid.

        Args:
            booking_id (int): Unique ID for the booking.
            guest_id (int): ID of the guest making the booking.
            room_number (int): Number of the room to be booked.
            check_in (str): Check-in date in YYYY-MM-DD format.
            check_out (str): Check-out date in YYYY-MM-DD format.
            installments (int): Number of payment installments (default is 1).

        Returns:
            tuple: (Booking object or None, message str)
        """
        room = self.room_manager.get_room_by_id(room_number)
        if not room:
            return None, "Room not found."
        valid, msg = self.validate_booking_dates(room_number, check_in, check_out)
        if not valid:
            return None, msg
        guest = self.guest_manager.get_guest_by_id(guest_id)
        if not guest:
            return None, "Guest not found."
        check_in_date = self._to_date(check_in)
        check_out_date = self._to_date(check_out)
        booking = UniversalEntityFactory.create_booking(booking_id, guest, room, check_in_date, check_out_date,
                                                        installments=installments)
        self.booking_manager.add_booking(booking)

        if isinstance(guest, MemberGuest):
            guest.add_points((check_out_date - check_in_date).days)

        self.booking_data.save(self.booking_manager.to_dict())
        self.guest_data.save(self.guest_manager.to_dict())

        # Removed automatic invoice sending - invoice will only be sent when explicitly requested
        return booking, f"Booking created successfully with ID: {booking_id}"

    def view_bookings(self):
        """
        Return list of Booking objects currently in the system.
        Useful for internal logic and programmatic access.
        Returns:
            list[Booking] | str: List of bookings, or message if empty.
        """
        bookings = self.booking_manager.get_all_bookings()
        return bookings if bookings else "No bookings in the system."

    def get_all_bookings_text(self):
        """
        Return list of booking summaries as strings for display in CLI or testing.

        Returns:
            list[str]: List of string representations of each booking.
        """
        bookings = self.booking_manager.get_all_bookings()
        return [str(b) for b in bookings] if bookings else ["No bookings in the system."]

    def update_booking(self, booking_id, check_in=None, check_out=None, room_number=None, installments=None):
        """
        Update booking dates, room, or number of installments.

        Args:
            booking_id (int): The ID of the booking to update.
            check_in (str or date, optional): New check-in date.
            check_out (str or date, optional): New check-out date.
            room_number (int, optional): New room number.
            installments (int, optional): New number of installments.

        Returns:
            str: Status message indicating success or the type of failure.
        """
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found."
        new_check_in = self._to_date(check_in) if check_in else booking.check_in
        new_check_out = self._to_date(check_out) if check_out else booking.check_out
        room_to_use = self.room_manager.get_room_by_id(room_number) if room_number else booking.room
        if not room_to_use:
            return "Room not found."
        valid, msg = self.check_room_availability(
            room_to_use.room_number,
            new_check_in,
            new_check_out,
            exclude_booking_id=booking_id
        )
        if not valid:
            return msg
        # Apply updates
        booking.update_booking(new_check_in, new_check_out, room_to_use)
        if installments is not None:
            booking.installments = installments
        # Save changes
        self.room_data.save(self.room_manager.to_dict())
        self.booking_data.save(self.booking_manager.to_dict())
        return "Booking updated successfully."

    def cancel_booking(self, booking_id):
        """Cancel an existing booking."""
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found."
        booking.status = 'cancelled'
        self.booking_data.save(self.booking_manager.to_dict())
        return "Booking cancelled successfully."

    def update_booking_status(self, booking_id, new_status):
        """Update the booking's status field."""
        valid_statuses = {'confirmed', 'checked-in', 'checked-out', 'cancelled'}
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found."
        if new_status not in valid_statuses:
            return f"Invalid status. Choose from {valid_statuses}"
        if new_status == 'checked-out' and not booking.paid:
            return "Cannot check-out: Booking must be paid first."
        booking.status = new_status
        self.booking_data.save(self.booking_manager.to_dict())
        return "Booking status updated."

    def mark_booking_paid(self, booking_id, paid=True):
        """Mark booking as paid or unpaid."""
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found."
        booking.paid = paid
        self.booking_data.save(self.booking_manager.to_dict())
        return f"Booking marked as {'paid' if paid else 'unpaid'}."

    def calculate_booking_cost(self, booking_id):
        """Compute final cost for a booking with discounts and installments."""
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return None
        guest = booking.guest
        room = booking.room
        nights = (booking.check_out - booking.check_in).days
        base_total = nights * room.price
        discount_percent = guest.get_discount_percentage() + (5 if nights > 7 else 0)
        discount_amount = base_total * discount_percent / 100
        total = base_total - discount_amount
        installments = getattr(booking, "installments", 1)
        # Use the guest's service strategy for installment calculation (applies VIP 5% / Member 2% payment discount)
        if not guest.service_strategy:
            from system.universal_factory import UniversalEntityFactory
            guest.service_strategy = UniversalEntityFactory.create_guest_service_strategy(guest)
        payment_per_installment = guest.service_strategy.calculate_payment_per_installment(total, installments)
        return {
            "nights": nights,
            "price_per_night": room.price,
            "base_total": base_total,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "total_after_discount": total,
            "installments": installments,
            "payment_per_installment": payment_per_installment
        }

    def generate_invoice_text(self, booking_id):
        """Generate a detailed invoice for a booking."""
        booking = self.booking_manager.get_booking_by_id(booking_id)
        if not booking:
            return "Booking not found."
        cost = self.calculate_booking_cost(booking_id)
        guest = booking.guest
        room = booking.room
        lines = [
            "=" * 40,
            f"{'INVOICE':^40}",
            "=" * 40,
            f"Booking ID: {booking.booking_id}",
            f"Guest Name: {guest.name}",
            f"Guest Type: {guest.get_guest_type()}",
            f"Room Number: {room.room_number}",
            f"Room Type: {room.room_type}",
            f"Check-in: {booking.check_in}",
            f"Check-out: {booking.check_out}",
            f"Number of Nights: {cost['nights']}",
            "-" * 40,
            f"Price per Night: {cost['price_per_night']:.2f} ₪",
            f"Base Total: {cost['base_total']:.2f} ₪",
            f"Discount: {cost['discount_percent']}% (-{cost['discount_amount']:.2f} ₪)",
            f"Installments: {cost['installments']} payments",
            f"Each Payment: {cost['payment_per_installment']:.2f} ₪"
        ]
        if isinstance(guest, MemberGuest):
            lines.append(f"Member points: {guest.points}")

        lines += [
            "-" * 40,
            f"Total After Discount: {cost['total_after_discount']:.2f} ₪",
            f"Payment Status: {'Paid' if booking.paid else 'Unpaid'}",
            f"Booking Status: {booking.status}",
            "=" * 40
        ]
        return "\n".join(lines)

    def check_room_availability(self, room_number, check_in, check_out, exclude_booking_id=None):
        """
        Check if a room is available for a given date range, excluding a specific booking if provided.

        This method verifies that the specified room exists, is not under maintenance,
        and is not already booked for any overlapping dates. Canceled bookings and an optional
        excluded booking ID are ignored in the availability check.

        Args:
            room_number (int): The number of the room to check.
            check_in (str or datetime.date): Desired check-in date.
            check_out (str or datetime.date): Desired check-out date.
            exclude_booking_id (int, optional): Booking ID to ignore during the check (useful when updating a booking).

        Returns:
            tuple:
                - bool: True if the room is available, False otherwise.
                - str: Message explaining the result.
        """
        room = self.room_manager.get_room_by_id(room_number)
        if not room:
            return False, "Room not found."
        if room.status == 'maintenance':
            return False, "Room is under maintenance."
        desired_in = self._to_date(check_in)
        desired_out = self._to_date(check_out)
        for booking in self.booking_manager.get_bookings_by_room_id(room_number):
            if booking.status == "cancelled":
                continue
            if exclude_booking_id is not None and booking.booking_id == exclude_booking_id:

                continue
            if desired_in < booking.check_out and desired_out > booking.check_in:
                return False, "The room is not available for the selected dates."

        return True, "The room is available"
