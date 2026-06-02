from system.system import HotelManagementSystem
from constants import (
    VALID_ROOM_TYPES,
    VALID_ROOM_STATUSES,
    VALID_GUEST_TYPES,
    VALID_BOOKING_STATUSES)


class Hotelcli:
    """
    Command Line Interface (CLI) for interacting with the Hotel Management System.
    Provides navigation through menus for managing rooms, guests, bookings, and reports.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def run_cli(self):
        """
        Start the CLI main loop and route user choices to the appropriate menu.
        """
        system = HotelManagementSystem()
        while True:
            print("\n--- Main Menu ---")
            print("1. Room Management")
            print("2. Guest Management")
            print("3. Booking Management")
            print("4. Management Reports")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == '1':
                room_menu(system)
            elif choice == '2':
                guest_menu(system)
            elif choice == '3':
                booking_menu(system)
            elif choice == '4':
                reports_menu(system)
            elif choice == '5':
                print("Saving data and exiting the program.")
                system.save_all()
                break
            else:
                print("Invalid choice. Try again.")


def room_menu(system):
    """
     Display and handle options for room management.
        """
    valid_room_types = VALID_ROOM_TYPES
    valid_room_statuses = VALID_ROOM_STATUSES

    while True:
        print("\n--- Room Management Menu ---")
        print("1. Add Room")
        print("2. View All Rooms")
        print("3. Update Room")
        print("4. Remove Room")
        print("5. Check Room Availability")
        print("6. Return to Main Menu")
        choice = input("Choose an option: ")

        if choice == '1':
            try:
                room_number = int(input("Enter room number: "))
            except ValueError:
                print("Invalid room number.")
                continue

            print(f"Valid room types: {', '.join(valid_room_types)}")
            room_type = input("Enter room type: ").lower()
            if room_type not in valid_room_types:
                print("Invalid room type.")
                continue

            try:
                price = float(input("Enter price: "))
            except ValueError:
                print("Invalid price.")
                continue

            print(f"Valid room statuses: {', '.join(valid_room_statuses)}")
            status = input("Enter room status (leave blank for 'available'): ").lower()
            status = status if status else 'available'
            if status not in valid_room_statuses:
                print("Invalid status.")
                continue

            msg = system.room_service.add_room(room_number, room_type, price, status)
            if msg:
                print(msg)

        elif choice == '2':
            result = system.room_service.view_rooms()
            if isinstance(result, str):
                print(result)
            else:
                for room in result:
                    print(room)

        elif choice == '3':
            try:
                room_number = int(input("Enter room number to update: "))
            except ValueError:
                print("Invalid room number.")
                continue

            print(f"Valid room types: {', '.join(valid_room_types)}")
            room_type = input("Enter new type (leave blank for no change): ").lower()
            price_input = input("Enter new price (leave blank for no change): ")
            price = float(price_input) if price_input.strip() else None

            print(f"Valid room statuses: {', '.join(valid_room_statuses)}")
            status = input("Enter new status (leave blank for no change): ").lower()
            status = status if status in valid_room_statuses else None

            msg = system.room_service.update_room(room_number, room_type or None, price, status)
            if msg:
                print(msg)

        elif choice == '4':
            try:
                room_number = int(input("Enter room number to remove: "))
            except ValueError:
                print("Invalid room number.")
                continue

            msg = system.room_service.remove_room(room_number)
            if msg:
                print(msg)

        elif choice == '5':
            try:
                room_number = int(input("Enter room number to check: "))
                check_in = input("Enter check-in date (YYYY-MM-DD): ")
                check_out = input("Enter check-out date (YYYY-MM-DD): ")
                available, msg = system.room_service.check_availability(room_number, check_in, check_out)

                print(msg)
            except ValueError:
                print("Invalid input.")

        elif choice == '6':
            break
        else:
            print("Invalid choice. Try again.")


def guest_menu(system):
    """
       Display and handle options for guest management.
       """
    while True:
        print("\n--- Guest Management Menu ---")
        print("1. Register Guest")
        print("2. View All Guests")
        print("3. View Guest Details")
        print("4. Update Guest")
        print("5. Update Guest Type")
        print("6. Remove Guest")
        print("7. Return to Main Menu")
        choice = input("Choose an option: ")

        if choice == '1':
            name = input("Enter guest name: ")
            contact = input("Enter contact info: ")
            print(f"Valid guest types: {', '.join(VALID_GUEST_TYPES)}")
            guest_type = input("Enter guest type: ").lower()
            if guest_type not in VALID_GUEST_TYPES:
                print("Invalid guest type.")
                continue
            msg = system.guest_service.register_guest(system.next_guest_id, name, contact, guest_type)
            system.next_guest_id += 1
            if msg:
                print(msg)

        elif choice == '2':
            result = system.guest_service.view_guests()
            if isinstance(result, str):
                print(result)
            else:
                for guest in result:
                    print(guest)

        elif choice == '3':
            search_input = input("Enter guest ID or name: ")
            result = system.guest_service.view_guest_details(search_input)
            if isinstance(result, str):
                print(result)
            else:
                for guest in result:
                    print(guest)

        elif choice == '4':
            try:
                guest_id = int(input("Enter guest ID to update: "))
                name = input("New name (leave blank to skip): ") or None
                contact = input("New contact (leave blank to skip): ") or None
                msg = system.guest_service.update_guest(guest_id, name, contact)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid guest ID.")

        elif choice == '5':
            try:
                guest_id = int(input("Enter guest ID to change type: "))
                print(f"Valid guest types: {', '.join(VALID_GUEST_TYPES)}")
                guest_type = input("New guest type: ").lower()
                if guest_type not in VALID_GUEST_TYPES:
                    print("Invalid guest type.")
                    continue
                msg = system.guest_service.update_guest_type(guest_id, guest_type)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid guest ID.")

        elif choice == '6':
            try:
                guest_id = int(input("Enter guest ID to remove: "))
                msg = system.guest_service.remove_guest(guest_id)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid guest ID.")

        elif choice == '7':
            break
        else:
            print("Invalid choice. Try again.")


def booking_menu(system):
    """
        Display and handle options for booking management.
        """
    while True:
        print("\n--- Booking Management Menu ---")
        print("1. Create Booking")
        print("2. View All Bookings")
        print("3. Update Booking")
        print("4. Cancel Booking")
        print("5. Update Booking Status")
        print("6. Mark as Paid")
        print("7. Generate Invoice")
        print("8. Return to Main Menu")
        choice = input("Choose an option: ")

        if choice == '1':
            try:
                guest_id = int(input("Enter guest ID: "))
                room_number = int(input("Enter room number: "))
                check_in = input("Enter check-in (YYYY-MM-DD): ")
                check_out = input("Enter check-out (YYYY-MM-DD): ")
                installments_input = input("Enter number of installments (default is 1): ")
                installments = int(installments_input) if installments_input.strip() else 1
                booking, msg = system.booking_service.create_booking(
                    system.next_booking_id,
                    guest_id,
                    room_number,
                    check_in,
                    check_out,
                    installments
                )
                if msg:
                    print(msg)
                if booking:
                    system.next_booking_id += 1
            except ValueError:
                print("Invalid input.")

        elif choice == '2':
            result = system.booking_service.get_all_bookings_text()
            if isinstance(result, list) and result == ["No bookings in the system."]:
                print("No bookings in the system.")
            else:
                active_bookings = [booking_str for booking_str in result
                                   if "Status: cancelled" not in booking_str]
                if not active_bookings:
                    print("No active bookings in the system.")
                else:
                    for booking in active_bookings:
                        print(booking)

        elif choice == '3':

            try:

                booking_id = int(input("Enter booking ID: "))
                check_in = input("New check-in (blank to skip): ") or None
                check_out = input("New check-out (blank to skip): ") or None
                room_input = input("New room number (blank to skip): ")
                room_number = int(room_input) if room_input.strip() else None
                installments_input = input("New number of installments (blank to skip): ")
                installments = int(installments_input) if installments_input.strip() else None
                msg = system.booking_service.update_booking(booking_id, check_in, check_out, room_number, installments)
                if msg:
                    print(msg)

            except ValueError:
                print("Invalid input.")

        elif choice == '4':
            try:
                booking_id = int(input("Enter booking ID to cancel: "))
                msg = system.booking_service.cancel_booking(booking_id)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid ID.")

        elif choice == '5':
            try:
                booking_id = int(input("Enter booking ID: "))
                print(f"Valid statuses: {', '.join(VALID_BOOKING_STATUSES)}")
                status = input("New status: ").lower()
                if status not in VALID_BOOKING_STATUSES:
                    print("Invalid status.")
                    continue
                msg = system.booking_service.update_booking_status(booking_id, status)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid input.")

        elif choice == '6':
            try:
                booking_id = int(input("Enter booking ID: "))
                paid = input("Mark as paid? (yes/no): ").lower() in ['yes', 'y']
                msg = system.booking_service.mark_booking_paid(booking_id, paid)
                if msg:
                    print(msg)
            except ValueError:
                print("Invalid input.")

        elif choice == '7':

            try:
                booking_id = int(input("Enter booking ID for invoice: "))
                bookings = system.booking_service.view_bookings()
                booking = None
                if isinstance(bookings, list):
                    booking = next((b for b in bookings if b.booking_id == booking_id), None)
                if not booking:
                    print("Booking not found.")
                    continue
                invoice = system.booking_service.generate_invoice_text(booking_id)
                guest = booking.guest
                send = input("Would you like to send the invoice to the guest's contact? [y/n]: ").lower()
                if send in ['y', 'yes']:
                    # Use guest service strategy for invoice delivery
                    guest.send_invoice(invoice)
                else:
                    print("\nInvoice generated (not sent):")
                    print(invoice)
            except ValueError:
                print("Invalid input.")

        elif choice == '8':
            break
        else:
            print("Invalid choice. Try again.")


def reports_menu(system):
    """
        Display and handle options for generating management reports.
        """
    while True:
        print("\n--- Management Reports Menu ---")
        print("1. Room Status Report")
        print("2. Occupancy Rate")
        print("3. Upcoming Bookings")
        print("4. Search Bookings by Date")
        print("5. Search Bookings by Guest Name")
        print("6. Guest Booking History")
        print("7. Discounts Applied")
        print("8. Return to Main Menu")
        choice = input("Choose an option: ")
        if choice == '1':
            rooms = system.report_service.view_room_status_report()
            if not rooms:
                print("No rooms in the system.")
            else:
                for room in rooms:
                    print(room)
        elif choice == '2':
            rate = system.report_service.view_occupancy_rate()
            print(f"Occupancy rate: {rate:.2f}%")
        elif choice == '3':
            bookings = system.report_service.view_upcoming_bookings()
            if not bookings:
                print("No upcoming bookings found.")
            else:
                for booking in bookings:
                    print(booking)
        elif choice == '4':
            date = input("Enter date (YYYY-MM-DD): ")
            search_date, bookings = system.report_service.search_bookings_by_date(date)
            if bookings == "Invalid date format. Use YYYY-MM-DD.":
                print(bookings)
            elif not bookings:
                print(f"No bookings found for {search_date}.")
            else:
                print(f"\nBookings for {search_date}:")
                for booking in bookings:
                    print(booking)
        elif choice == '5':
            name = input("Enter guest name: ")
            guest_name, bookings = system.report_service.search_bookings_by_guest(name)
            if not bookings:
                print("No bookings found for guest with that name.")
            else:
                print(f"\nBookings for guest containing '{guest_name}':")
                for booking in bookings:
                    print(booking)
        elif choice == '6':
            try:
                guest_id = int(input("Enter guest ID: "))
                guest_name, bookings = system.report_service.view_guest_booking_history(guest_id)
                if bookings == "Guest not found." or guest_name is None:
                    print("Guest not found.")
                elif not bookings:
                    print("No bookings found for this guest.")
                else:
                    print(f"\nBooking History for Guest {guest_id} - {guest_name}:")
                    for booking in bookings:
                        print(booking)
            except ValueError:
                print("Invalid guest ID.")
        elif choice == '7':
            discounts = system.report_service.view_discounts_applied()
            if not discounts:
                print("No bookings with discounts found.")
            else:
                print("\nBookings with Discounts Applied:")
                for d in discounts:
                    print(f"Booking {d['booking_id']}: Guest {d['guest_name']} ({d['guest_type']})")
                    print(f"  Discount: {d['discount_percent']}% (-{d['discount_amount']:.2f} ₪)")
                    print(f"  Total After Discount: {d['total_after_discount']:.2f} ₪")
        elif choice == '8':
            break
        else:
            print("Invalid choice. Try again.")
