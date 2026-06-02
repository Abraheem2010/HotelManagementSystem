from guests.guests import Guest, VIPGuest, MemberGuest


class GuestManager:
    """
    Manages the collection of guests in the system.
    Responsible for adding, removing, searching, and updating guests.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize an empty list to store guests."""
        self.guests = []

    def load_guests(self, guest_data):
        """
        Load guests from a list of dictionaries (usually from a JSON file).

        Args:
            guest_data (list): List of dictionaries representing guests.
        """
        self.guests = []
        for data in guest_data:
            # Skip malformed records that are missing required fields.
            if not all(key in data for key in ("guest_id", "name", "contact")):
                print(f"Skipping malformed guest record: {data}")
                continue

            guest_type = data.get("guest_type", "regular").lower()
            if guest_type == "vip":
                guest = VIPGuest(data["guest_id"], data["name"], data["contact"])
            elif guest_type == "member":
                guest = MemberGuest(
                    data["guest_id"], data["name"], data["contact"], data.get("points", 0)
                )
            else:
                guest = Guest(data["guest_id"], data["name"], data["contact"])
            self.guests.append(guest)

    def get_guest_by_id(self, guest_id):
        """
        Retrieve a guest object by their unique ID.

        Args:
            guest_id (int): The ID of the guest to search for.

        Returns:
            Guest or None: The guest if found, otherwise None.
        """
        for guest in self.guests:
            if guest.guest_id == guest_id:
                return guest
        return None

    def replace_guest(self, guest_id, new_guest):
        """
        Replace an existing guest object with a new one (e.g. after type update).

        Args:
            guest_id (int): The ID of the guest to replace.
            new_guest (Guest): The new guest object to insert.

        Returns:
            bool: True if replacement succeeded, False otherwise.
        """
        for i, guest in enumerate(self.guests):
            if guest.guest_id == guest_id:
                self.guests[i] = new_guest
                return True
        return False

    def add_guest(self, guest: Guest):
        """
        Add a new guest to the collection.

        Args:
            guest (Guest): The guest object to add.

        Raises:
            ValueError: If a guest with the same ID already exists.
        """
        if self.get_guest_by_id(guest.guest_id):
            raise ValueError("Guest with this ID already exists.")
        self.guests.append(guest)

    def remove_guest(self, guest_id):
        """
        Remove a guest by their ID.

        Args:
            guest_id (int): The ID of the guest to remove.

        Returns:
            bool: True if a guest was removed, False if not found.
        """
        original_count = len(self.guests)
        self.guests = [g for g in self.guests if g.guest_id != guest_id]
        return len(self.guests) < original_count

    def get_all_guests(self):
        """
        Retrieve all guests currently in the system.

        Returns:
            list: List of Guest objects.
        """
        return self.guests

    def to_dict(self):
        """
        Convert all guest objects to a list of dictionaries for saving.

        Returns:
            list: List of dictionaries representing each guest.
        """
        return [guest.to_dict() for guest in self.guests]
