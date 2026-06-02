# Hotel Management System 🏨
A modular object-oriented system to manage hotel operations such as rooms, guests, bookings, payments, and reports.
Built using Python, with a clean CLI interface, enterprise-level architecture, and comprehensive design patterns implementation.

# 🚀 Features

Guest Management - Add and manage Regular, VIP, and Member guests with personalized services
Room Operations - Complete room management with real-time availability tracking
Smart Booking System - Advanced booking creation with automated cost calculation
Flexible Payment Options - Installment payment support for all guest types
Intelligent Invoice System - Context-aware invoice generation and delivery
Comprehensive Reports - Management dashboards for occupancy, guest history, and discount analytics
Data Persistence - Reliable JSON-based data storage with automatic backup
Professional CLI Interface - Intuitive command-line interface for all operations
Enterprise Architecture - Built with industry-standard design patterns


# 🏗️ Architecture Overview
📁 HotelManagementSystem/
├── 📁 bookings/          # Booking logic and services
├── 📁 guests/            # Guest management + service strategies  
├── 📁 reports/           # Analytics and report generation
├── 📁 rooms/             # Room management and availability
├── 📁 system/            # Core system and universal factory
├── 📁 utils/             # Data management and utilities
├── 📄 hms/hms.py         # CLI interface and user interaction
├── 📄 constants.py       # System-wide constants
├── 📄 main.py            # Application entry point
├── 📄 .gitignore         # Git ignore rules
├── 📄 requirements.txt   # Dependencies (Python stdlib only)
└── 📄 README.md          # Project documentation
# Enterprise Design Patterns:

✅ Strategy Pattern – Unified guest service strategies (payment, discount, delivery)
✅ Factory Pattern – Centralized object creation via UniversalEntityFactory
✅ Singleton Pattern – Single instance managers for data consistency
✅ Service Layer Pattern – Clear separation between business logic and data access


# 🎯 Guest Types & Services
Guest TypeDiscountPayment BenefitsSpecial ServicesInvoice DeliveryVIP20%+5% payment discountPersonal AssistantExclusive VIP serviceMember10-25%*+2% payment discountLoyalty PointsPriority member serviceRegular0%Standard paymentStandard ServiceBasic email service
*Member discount: 10% base + points/10 (maximum 25%)

# 🔧 Key Components
UniversalEntityFactory
Centralized factory for creating all system entities:

Guest creation with automatic service strategy assignment
Room and booking instantiation with proper validation
Service strategy selection based on guest type

# GuestServiceStrategy (Strategy Pattern)
Unified service approach combining:

Dynamic discount calculation logic
Installment payment processing
Context-aware invoice delivery methods

# Singleton Architecture

HotelManagementSystem - Central system coordinator
Data consistency across all operations
Single source of truth for system state


# 🚀 Getting Started
Prerequisites

Python 3.7 or higher
No external dependencies required (uses Python standard library only)

# Installation

Clone or download the project
Navigate to the project directory
Run the main application:

bashpython main.py
## Data Files (Auto-Generated)
The system automatically creates and manages:
rooms.json          # Room inventory and status
guests.json         # Guest profiles and loyalty points
bookings.json       # Reservations and transaction history
First Steps

Add Rooms - Set up your hotel inventory with different types and prices
Register Guests - Add guest profiles with appropriate service levels
Create Bookings - Make reservations with automatic pricing and discounts
Generate Reports - Monitor hotel performance and guest analytics


# 💼 System Workflow

Guest Registration → Automatic service strategy assignment based on type
Room Selection → Real-time availability verification with date validation
Booking Creation → Automated pricing with guest-specific discounts applied
Payment Processing → Flexible installment options with additional discounts
Invoice Generation → Context-aware delivery using guest service strategy
Report Analytics → Comprehensive performance tracking and insights


# 📊 Management Reports
Access detailed analytics through the Reports Menu:

Room Status Report - Current room availability and occupancy details
Occupancy Rate - Real-time hotel utilization percentage metrics
Guest Booking History - Complete reservation records per individual guest
Discount Analytics - Applied discounts and total savings analysis
Upcoming Bookings - Future reservation overview with check-in dates
Date-Based Search - Find all bookings for specific dates
Guest Name Search - Locate bookings by partial guest name matching


# 🏢 Business Logic
Room Management

Multiple room types (single, double, suite, deluxe)
Dynamic status tracking (available, occupied, maintenance, reserved)
Real-time availability checking with date range validation

# Guest Services

VIP Guests: 20% discount + 5% payment bonus + premium personal service
Member Guests: Dynamic discounts (10-25%) + 2% payment bonus + loyalty points
Regular Guests: Standard pricing and basic service level

# Booking Intelligence

Automatic cost calculation with guest-specific discounts
Flexible installment payment options for all guest types
Invoice generation with personalized delivery methods


# 📁 Project Structure Details

system/
├── system.py                    # Central HotelManagementSystem (Singleton)
└── universal_factory.py        # Entity and strategy factory

guests/
├── guests.py                    # Guest entity with inheritance hierarchy
├── guest_manager.py             # Guest data management and CRUD operations
├── guest_service.py             # Guest business logic and operations
└── guest_service_strategy.py    # Strategy pattern for guest services

rooms/
├── room.py                      # Room entity class
├── room_manager.py              # Room data management
└── room_service.py              # Room business logic and availability

bookings/
├── booking.py                   # Booking entity with cost calculation
├── booking_manager.py           # Booking data management
└── booking_service.py           # Booking business logic and processing

reports/
└── report_service.py            # Analytics and comprehensive reporting

utils/
└── data_manager.py              # JSON persistence utility with error handling
# 🛠️ Technical Specifications

Language: Python 3.7+
Architecture: Layered architecture with service pattern
Data Storage: JSON files with automatic serialization
Design Patterns: Strategy, Factory, Singleton, Service Layer
Error Handling: Comprehensive validation and exception management
Type Safety: Full type hints throughout codebase


# 🎓 Educational Value
This project demonstrates:

Clean Architecture principles in Python
Design Pattern implementation in real-world scenarios
Object-Oriented Programming best practices
Service Layer architecture for business logic separation
Data Persistence strategies for small to medium applications


# 🔄 Future Enhancements

Web Interface: Flask/Django web application
Database Integration: PostgreSQL/MySQL support
API Development: RESTful API endpoints
Advanced Reporting: Charts and visual analytics
Email Integration: Automated invoice delivery
Multi-language Support: Internationalization


# 📚 Learning Resources

Study the strategy pattern implementation in guest_service_strategy.py
Examine the factory pattern in universal_factory.py
Review the service layer architecture across all service classes
Analyze the singleton implementation in system.py


Built with Python 🐍 | Designed for Learning 📚 | Ready for Production 🚀
A comprehensive hotel management solution showcasing enterprise-level Python development practices.