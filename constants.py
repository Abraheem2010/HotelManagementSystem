"""
constants.py

This module defines the constant sets used across the Hotel Management System project.
These include valid types and statuses for rooms, guests, and bookings.
"""

# Valid room types in the hotel
VALID_ROOM_TYPES = {'single', 'double', 'suite', 'deluxe'}

# Possible statuses for a hotel room
VALID_ROOM_STATUSES = {'available', 'occupied', 'maintenance', 'reserved'}

# Supported guest types
VALID_GUEST_TYPES = {'regular', 'vip', 'member'}

# Possible statuses for a booking
VALID_BOOKING_STATUSES = {'confirmed', 'checked-in', 'checked-out', 'cancelled'}
