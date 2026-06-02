# Design Patterns in Hotel Management System

## Overview

The Hotel Management System implements three core Design Patterns that create a robust, flexible, and maintainable architecture:

1. **Abstract Factory Pattern** - For creating entities
2. **Strategy Pattern** - For managing different guest behaviors  
3. **Singleton Pattern** - For global state management

---

## 1. Abstract Factory Pattern 🏭

### Purpose
Create families of related objects without specifying their concrete classes.

### Implementation - UniversalEntityFactory

```python
class UniversalEntityFactory:
    """
    Abstract Factory that centralizes all object creation in the system
    """
    
    @staticmethod
    def create_booking(booking_id, guest, room, check_in, check_out, status="confirmed"):
        """Creates a new booking with all required details"""
        return Booking(booking_id, guest, room, check_in, check_out, status)
    
    @staticmethod  
    def create_guest(guest_id, name, phone, email, guest_type="regular"):
        """Creates a new guest based on specified type"""
        if guest_type.lower() == "vip":
            return VipGuest(guest_id, name, phone, email)
        elif guest_type.lower() == "member":
            return MemberGuest(guest_id, name, phone, email)
        else:
            return RegularGuest(guest_id, name, phone, email)
    
    @staticmethod
    def create_room(room_id, room_type, price_per_night, status="available"):
        """Creates a new hotel room"""
        return Room(room_id, room_type, price_per_night, status)
    
    @staticmethod
    def create_guest_service_strategy(guest):
        """Creates appropriate service strategy for guest type"""
        if isinstance(guest, VipGuest):
            return VipGuestServiceStrategy()
        elif isinstance(guest, MemberGuest):
            return MemberGuestServiceStrategy()
        else:
            return RegularGuestServiceStrategy()
```

### Benefits
- **Centralized Creation** - All objects created in one place
- **Consistency** - Same creation methods for all objects
- **Flexibility** - Easy to add new types
- **Testability** - Easy to mock the factory

---

## 2. Strategy Pattern + Service Object 🎯

### Purpose
Define a family of algorithms, encapsulate each one, and make them interchangeable.

### Implementation - GuestServiceStrategy

```python
class GuestServiceStrategy(ABC):
    """Abstract base class for all guest service strategies"""
    
    @abstractmethod
    def calculate_payment_per_installment(self, total_price, num_installments):
        """Calculate installment payment"""
        pass
    
    @abstractmethod
    def get_discount_percentage(self):
        """Get discount percentage for guest type"""
        pass
    
    @abstractmethod
    def send_invoice(self, guest, invoice_text):
        """Send invoice in appropriate manner for guest type"""
        pass

class VipGuestServiceStrategy(GuestServiceStrategy):
    """VIP service strategy - 20% discount + personal service"""
    
    def calculate_payment_per_installment(self, total_price, num_installments):
        return total_price / num_installments
    
    def get_discount_percentage(self):
        return 20.0
    
    def send_invoice(self, guest, invoice_text):
        return f"📧 Personal Assistant: Dear {guest.name}, your exclusive invoice:\n{invoice_text}"

class MemberGuestServiceStrategy(GuestServiceStrategy):
    """Member service strategy - 15% discount + loyalty points"""
    
    def calculate_payment_per_installment(self, total_price, num_installments):
        return total_price / num_installments
    
    def get_discount_percentage(self):
        return 15.0
    
    def send_invoice(self, guest, invoice_text):
        return f"📱 Member App: Hi {guest.name}! +50 loyalty points earned!\n{invoice_text}"

class RegularGuestServiceStrategy(GuestServiceStrategy):
    """Regular service strategy - basic service"""
    
    def calculate_payment_per_installment(self, total_price, num_installments):
        return total_price / num_installments
    
    def get_discount_percentage(self):
        return 0.0
    
    def send_invoice(self, guest, invoice_text):
        return f"📧 Hotel System: Dear {guest.name}, your invoice:\n{invoice_text}"
```

### Benefits
- **Unified Behavior** - All services for guest type in one place
- **Polymorphism** - Each guest type behaves differently automatically
- **No Complex Conditionals** - No need for if-else chains
- **Easy Extension** - Adding new services is simple

---

## 3. Singleton Pattern 👑

### Purpose
Ensure a class has only one instance and provide global access to it.

### Implementation in System

```python
class HotelCli:
    """User interface - single instance only"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.system = HotelManagementSystem()
            self.initialized = True

class BookingManager:
    """Booking manager - single instance"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

class GuestManager:
    """Guest manager - single instance"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

class RoomManager:
    """Room manager - single instance"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Benefits in Our System
- **Single Source of Truth** - Only one instance of each manager
- **Memory Efficiency** - No unnecessary manager creation
- **State Consistency** - All code sees the same data
- **Global Access** - Easy access to managers from anywhere

### Why It Fits Our System
- **Single-threaded CLI** - No concurrency issues
- **Hotel Management** - Really need single instance of each manager
- **Clear Boundaries** - Manager boundaries are well-defined

---

## Practical Usage Examples

### Creating a New Booking

```python
# Create VIP guest
guest = UniversalEntityFactory.create_guest(
    guest_id=1, 
    name="David Cohen", 
    phone="050-1234567",
    email="david@email.com",
    guest_type="vip"
)

# Create deluxe room
room = UniversalEntityFactory.create_room(
    room_id=101, 
    room_type="deluxe",
    price_per_night=300,
    status="available"
)

# Create booking
booking = UniversalEntityFactory.create_booking(
    booking_id=1, 
    guest=guest, 
    room=room,
    check_in="2025-06-15", 
    check_out="2025-06-20"
)

# Get appropriate service for guest
service = UniversalEntityFactory.create_guest_service_strategy(guest)
```

### Using Service Strategy

```python
# Calculate installment payment
total_price = 1500
payment_per_installment = service.calculate_payment_per_installment(
    total_price=total_price, 
    num_installments=3
)
# VIP: $500 per installment

# Get discount
discount_percentage = service.get_discount_percentage()
# VIP: 20%

# Calculate final price after discount
final_price = total_price * (1 - discount_percentage / 100)
# VIP: $1200

# Send invoice
invoice_text = f"Amount to pay: ${final_price}"
notification = service.send_invoice(guest, invoice_text)
# VIP: "📧 Personal Assistant: Dear David Cohen, your exclusive invoice:..."
```

### Accessing Managers (Singleton)

```python
# All calls return the same instance
booking_manager1 = BookingManager()
booking_manager2 = BookingManager()
# booking_manager1 is booking_manager2 → True

# Add booking - saved everywhere
booking_manager1.add_booking(booking)
all_bookings = booking_manager2.get_all_bookings()
# Contains the booking we added through booking_manager1
```

---

## Architecture Benefits

### Flexibility and Extension 🚀
- **Adding new guest type:** Only update factory and create new strategy
- **Adding new service:** Only add method to strategies
- **Changing behavior:** Only in relevant strategy

### Maintenance and Testing 🔧
- **Finding bugs:** Logic centralized in clear locations
- **Unit testing:** Each strategy testable separately
- **Mock testing:** Easy to mock factory and strategies

### Performance and Efficiency 📊
- **Memory:** Singleton ensures single instance of managers
- **Consistency:** All code works with same objects
- **Reusability:** Strategies reusable in multiple places

---

## System Structure

```
📁 HotelManagementSystem/
├── 📁 bookings/          # Booking-related functionality
├── 📁 guests/            # Guest management + GuestServiceStrategy
├── 📁 hms/              # User interface (CLI)
├── 📁 reports/          # Reports and analytics
├── 📁 rooms/            # Room-related functionality
├── 📁 system/           # UniversalEntityFactory + System core
├── 📁 utils/            # Utilities and data management
├── 📄 constants.py      # System constants
├── 📄 main.py          # Entry point
└── 📄 README.md        # Documentation
```

---

## Summary

The combination of three patterns creates a professional and efficient architecture:

### 🏭 Abstract Factory
Centralizes and organizes all object creation in the system, ensuring consistency and maintainability.

### 🎯 Strategy 
Provides complete flexibility in adapting behavior to different guest types without complex code.

### 👑 Singleton
Ensures data consistency and memory efficiency through single instances of system managers.

**Result: A robust, flexible, and maintainable system suitable for advanced business needs! 🏆**