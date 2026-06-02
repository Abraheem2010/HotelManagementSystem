from guests.guests import MemberGuest
from system.universal_factory import UniversalEntityFactory


class GuestService:
    """
    Service class responsible for managing guest-related operations
    such as registration, updates, and retrieval.
    """

    def __init__(self, guest_manager, guest_data):
        """
        Initialize the GuestService with required managers and data handlers.

        Args:
            guest_manager: Object handling in-memory guest storage.
            guest_data: Object responsible for saving/loading guest data.
        """
        self.guest_manager = guest_manager
        self.guest_data = guest_data

    def register_guest(self, guest_id, name, contact, guest_type="regular"):
        """
        Register a new guest in the system.

        Args:
            guest_id (int): Unique guest identifier.
            name (str): Guest's name.
            contact (str): Guest's contact information.
            guest_type (str): Type of guest ("regular", "vip", "member").

        Returns:
            str: Success or error message.
        """
        if self.guest_manager.get_guest_by_id(guest_id):
            return f"Guest with ID {guest_id} already exists."

        guest = UniversalEntityFactory.create_guest(guest_id, name, contact, guest_type)
        self.guest_manager.add_guest(guest)
        self.guest_data.save(self.guest_manager.to_dict())
        return f"{guest.get_guest_type()} guest registered successfully with ID: {guest_id}"

    def update_guest_type(self, guest_id, new_type):
        """
        Change the guest type (e.g., regular → vip).

        Args:
            guest_id (int): Guest's ID.
            new_type (str): New type to assign.

        Returns:
            str: Status message.
        """
        guest = self.guest_manager.get_guest_by_id(guest_id)
        if not guest:
            return "Guest not found."

        new_guest = UniversalEntityFactory.create_guest(guest_id, guest.name, guest.contact, new_type)

        if isinstance(new_guest, MemberGuest) and isinstance(guest, MemberGuest):
            new_guest.points = guest.points

        self.guest_manager.replace_guest(guest_id, new_guest)
        self.guest_data.save(self.guest_manager.to_dict())
        return f"Guest type updated to {new_guest.get_guest_type()}."

    def view_guest_details(self, search_input):
        """
        Retrieve details of a guest by ID or name.

        Args:
            search_input (str): Guest ID or name.

        Returns:
            str or list: Guest details or message if not found.
        """
        try:
            guest_id = int(search_input)
            guest = self.guest_manager.get_guest_by_id(guest_id)
            return str(guest) if guest else f"No guest found with ID: {guest_id}"
        except ValueError:
            results = [
                str(guest)
                for guest in self.guest_manager.get_all_guests()
                if search_input.lower() in guest.name.lower()
            ]
            return results if results else f"No guest found with name containing: {search_input}"

    def view_guests(self):
        """
        View all registered guests.

        Returns:
            list or str: List of guest descriptions or message if none exist.
        """
        guests = self.guest_manager.get_all_guests()
        return [str(g) for g in guests] if guests else "No registered guests."

    def update_guest(self, guest_id, name=None, contact=None):
        """
        Update guest name and/or contact details.

        Args:
            guest_id (int): ID of the guest to update.
            name (str, optional): New name.
            contact (str, optional): New contact.

        Returns:
            str: Status message.
        """
        guest = self.guest_manager.get_guest_by_id(guest_id)
        if not guest:
            return "Guest not found."

        guest.update_guest(name, contact)
        self.guest_data.save(self.guest_manager.to_dict())
        return "Guest updated successfully."

    def remove_guest(self, guest_id):
        """
        Remove a guest from the system.

        Args:
            guest_id (int): ID of the guest to remove.

        Returns:
            str: Success or failure message.
        """
        removed = self.guest_manager.remove_guest(guest_id)
        if not removed:
            return "Guest not found."
        self.guest_data.save(self.guest_manager.to_dict())
        return "Guest removed successfully."
