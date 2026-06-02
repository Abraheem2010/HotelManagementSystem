import datetime


class ReportService:
    """
    Service class for generating management reports related to guests,
    bookings, and room usage within the hotel system.
    """

    def __init__(self, guest_manager, room_manager, booking_manager, booking_service):
        """
        Initialize the report service with required managers and booking service.

        Args:
            guest_manager: Manages guest data.
            room_manager: Manages room data.
            booking_manager: Manages booking data.
            booking_service: Provides cost calculation and availability logic.
        """
        self.guest_manager = guest_manager
        self.room_manager = room_manager
        self.booking_manager = booking_manager
        self.booking_service = booking_service

    def view_guest_booking_history(self, guest_id):
        """
        Retrieve the booking history for a specific guest.

        Args:
            guest_id (int): The guest's unique identifier.

        Returns:
            tuple: (guest_name, list of bookings) or ("Guest not found.", None)
        """
        guest = self.guest_manager.get_guest_by_id(guest_id)
        if not guest:
            return None, "Guest not found."

        bookings = self.booking_manager.get_bookings_by_guest_id(guest_id)
        return guest.name, bookings if bookings else []

    def search_bookings_by_date(self, search_date):
        """
        Find bookings that include a specific date within their stay.

        Args:
            search_date (str): The date to search (format YYYY-MM-DD).

        Returns:
            tuple: (search_date, list of bookings) or (None, error message)
        """
        try:
            search_dt = datetime.datetime.strptime(search_date, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Use YYYY-MM-DD."

        matches = []
        for booking in self.booking_manager.get_all_bookings():
            check_in = booking.check_in
            check_out = booking.check_out
            if isinstance(check_in, str):
                check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
            if isinstance(check_out, str):
                check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()

            if check_in <= search_dt <= check_out:
                matches.append(booking)

        return search_date, matches

    def search_bookings_by_guest(self, guest_name):
        """
        Search for bookings by partial or full guest name.

        Args:
            guest_name (str): Name to search for.

        Returns:
            tuple: (guest_name, list of matching bookings)
        """
        matches = [
            booking for booking in self.booking_manager.get_all_bookings()
            if guest_name.lower() in booking.guest.name.lower()
        ]
        return guest_name, matches

    def view_discounts_applied(self):
        """
        Generate a list of bookings where discounts were applied.

        Returns:
            list: Each entry contains booking ID, guest details,
                  discount amount, and total after discount.
        """
        results = []

        for booking in self.booking_manager.get_all_bookings():
            guest = booking.guest
            discount = guest.get_discount_percentage()
            if discount > 0:
                cost_info = self.booking_service.calculate_booking_cost(booking.booking_id)
                if cost_info:
                    results.append({
                        "booking_id": booking.booking_id,
                        "guest_name": guest.name,
                        "guest_type": guest.get_guest_type(),
                        "discount_percent": cost_info["discount_percent"],
                        "discount_amount": cost_info["discount_amount"],
                        "total_after_discount": cost_info["total_after_discount"],
                    })

        return results

    def view_room_status_report(self):
        """
        Retrieve a list of all rooms and their current status.

        Returns:
            list: List of Room objects.
        """
        return self.room_manager.get_all_rooms()

    def view_upcoming_bookings(self):
        """
        Retrieve all bookings that start in the future.

        Returns:
            list: Bookings with check-in dates after today.
        """
        today = datetime.date.today()
        return [
            booking for booking in self.booking_manager.get_all_bookings()
            if isinstance(booking.check_in, datetime.date) and booking.check_in > today
        ]

    def view_occupancy_rate(self):
        """
        Calculate the current hotel occupancy rate.

        Returns:
            float: Percentage of rooms that are occupied.
        """
        rooms = self.room_manager.get_all_rooms()
        total_rooms = len(rooms)
        if total_rooms == 0:
            return 0.0

        today = datetime.date.today()
        occupied_count = 0

        for booking in self.booking_manager.get_all_bookings():
            # Check if booking is currently active (guest is checked in)
            if (booking.status == 'checked-in' and
                    booking.check_in <= today <= booking.check_out):
                occupied_count += 1

        return (occupied_count / total_rooms) * 100
