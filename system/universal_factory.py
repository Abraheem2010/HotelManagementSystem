from guests.guests import VIPGuest, MemberGuest, RegularGuest
from rooms.rooms import Room
from bookings.bookings import Booking
from guests.guest_service_strategy import (
    VIPGuestServiceStrategy,
    MemberGuestServiceStrategy,
    RegularGuestServiceStrategy
)
import datetime


class UniversalEntityFactory:
    """
    Unified factory for creating all system entities.
    Replaces BookingFactory, RoomFactory, GuestFactory,
    DiscountStrategyFactory, and PaymentStrategyFactory.
    """

    @staticmethod
    def create_guest(guest_id, name, contact, guest_type="regular", points=0):
        """
        Create a Guest object based on the guest type.

        Args:
            guest_id (int): Unique identifier for the guest.
            name (str): Guest's name.
            contact (str): Contact information.
            guest_type (str): Type of guest ("regular", "vip", or "member").
            points (int, optional): Loyalty points for member guests.

        Returns:
            Guest: An instance of VIPGuest, MemberGuest, or RegularGuest.
        """
        guest_type = guest_type.lower()

        if guest_type == "vip":
            return VIPGuest(guest_id, name, contact)
        elif guest_type == "member":
            return MemberGuest(guest_id, name, contact, points=points if points is not None else 0)
        else:
            return RegularGuest(guest_id, name, contact)

    @staticmethod
    def create_booking(booking_id, guest, room, check_in, check_out, status="confirmed", installments=1):
        """
        Create a new Booking object with normalized date handling.

        Args:
            booking_id (int): Unique ID for the booking.
            guest (Guest): Guest instance.
            room (Room): Room instance.
            check_in (str or date): Check-in date.
            check_out (str or date): Check-out date.
            status (str, optional): Booking status. Default is "confirmed".
            installments (int, optional): Number of installments. Default is 1.

        Returns:
            Booking: Instantiated Booking object.
        """
        if isinstance(check_in, str):
            check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
        if isinstance(check_out, str):
            check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()

        return Booking(booking_id, guest, room, check_in, check_out, status, installments=installments)

    @staticmethod
    def create_room(room_number, room_type, price, status='available'):
        """
        Create and return a new Room instance.

        Args:
            room_number (int): The unique room number.
            room_type (str): The type of the room (e.g., single, double, suite).
            price (float): The price per night for the room.
            status (str): The initial status of the room (default is 'available').

        Returns:
            Room: A new Room instance with the given attributes.
        """
        return Room(room_number, room_type, price, status)

    @staticmethod
    def create_guest_service_strategy(guest):
        """
        Create appropriate service strategy based on guest type.
        Replaces DiscountStrategyFactory and PaymentStrategyFactory.

        Args:
            guest (Guest): Guest object with status field.

        Returns:
            GuestServiceStrategy: An instance of the appropriate service strategy.
        """
        status = guest.status.lower()

        if status == "vip":
            return VIPGuestServiceStrategy()
        elif status == "member":
            return MemberGuestServiceStrategy()
        else:
            return RegularGuestServiceStrategy()