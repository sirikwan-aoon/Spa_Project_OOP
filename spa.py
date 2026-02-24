from __future__ import annotations
from datetime import date, datetime, timedelta
from enum import Enum
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod


app = FastAPI()

# ==========================================
# 1. DOMAIN CLASSES (FULL TYPE & VALUE VALIDATION)
# ==========================================

class SkillSets(Enum):
  TM = "Traditional Thai Massage"
  AT = "Aroma Therapy"
  DT = "Deep Tissue Massage"
  HP = "Hydrotherapy Pool"

class Spa:
    def __init__(self, name: str):
        if not isinstance(name, str): raise TypeError("Spa name must be a string")
        if not name.strip(): raise ValueError("Spa name cannot be empty")
        self.__name = name
        self.__customer_list = []
        self.__employee_list = []
        self.__room_list = []
        self.__transaction_list = []
        self.__treatment_list = []
        self.__resource_list = []
        self.__add_on_list = []
        self.__revenue_per_day_list = []
        self.__booking_count = 0

    @property
    def employee_list(self): return self.__employee_list
    @property
    def treatment_list(self): return self.__treatment_list
    @property
    def add_on_list(self): return self.__add_on_list
    @property
    def customer_list(self): return self.__customer_list
    @property
    def revenue_per_day_list(self): return self.__revenue_per_day_list
    @property
    def booking_count(self): return self.__booking_count

    @booking_count.setter
    def booking_count(self, value): self.__booking_count = value

    def search_customer_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("ID must be a string")
        for customer in self.__customer_list:
            if customer.id == id: return customer
        return None

    def search_employee_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("ID must be a string")
        for employee in self.__employee_list:
            if employee.id == id: return employee
        return None

    def search_treatment_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("ID must be a string")
        for treatment in self.__treatment_list:
            if treatment.id == id: return treatment
        return None

    def search_add_on_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("ID must be a string")
        for add_on in self.__add_on_list:
            if add_on.id == id: return add_on
        return None

    def search_room_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("ID must be a string")
        for room in self.__room_list:
            if room.id == id: return room
        return None

    def get_room_by_room_type(self, type_str: str):
        if not isinstance(type_str, str): raise TypeError("Room type must be a string")
        return [room for room in self.__room_list if room.id.startswith(type_str)]

    def verify_admin(self, employee_id: str, input_password: str):
        if not isinstance(employee_id, str) or not isinstance(input_password, str):
            raise TypeError("Employee ID and Password must be strings")
        
        employee = self.search_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee ID {employee_id} not found")
        if not hasattr(employee, 'password'):
            raise TypeError("This employee does not have admin privileges")
        
        if employee.password == input_password:
            employee.login = True
        else:
            raise ValueError("Invalid password")

    def add_employee(self, employee):
        if not isinstance(employee, Employee): raise TypeError("Must be an Employee object")
        if self.search_employee_by_id(employee.id): raise ValueError(f"Employee ID {employee.id} already exists!")
        self.__employee_list.append(employee)

    def add_treatment(self, treatment):
        if not isinstance(treatment, Treatment): raise TypeError("Must be a Treatment object")
        if self.search_treatment_by_id(treatment.id): raise ValueError(f"Treatment ID {treatment.id} already exists!")
        self.__treatment_list.append(treatment)

    def add_customer(self, customer):
        if not isinstance(customer, Customer): raise TypeError("Must be a Customer object")
        if self.search_customer_by_id(customer.id): raise ValueError(f"Customer ID {customer.id} already exists!")
        self.__customer_list.append(customer)

    def add_room(self, room):
        if not isinstance(room, Room): raise TypeError("Must be a Room object")
        if self.search_room_by_id(room.id): raise ValueError(f"Room ID {room.id} already exists!")
        self.__room_list.append(room)

    def add_add_on_list(self, add_on):
        if not isinstance(add_on, AddOn): raise TypeError("Must be an AddOn object")
        if self.search_add_on_by_id(add_on.id): raise ValueError(f"Add-on ID {add_on.id} already exists!")
        self.__add_on_list.append(add_on)

    def find_intersect_free_slot(self, room_slot: list, therapist_slot: list):
        if not isinstance(room_slot, list) or not isinstance(therapist_slot, list):
            raise TypeError("Slots must be provided as lists")
        list_of_intersect_free_slot = []
        for i in range(16):
            if i < len(room_slot) and i < len(therapist_slot):
                if room_slot[i].vacancy > 0 and therapist_slot[i].vacancy > 0:
                    list_of_intersect_free_slot.append(room_slot[i])
        return list_of_intersect_free_slot
    
    def generate_customer_id(self) :
        
        current_count = len(self.customer_list)
        
        while True:
            current_count += 1
            new_id = f"C{current_count:04d}"
            
            if self.search_customer_by_id(new_id) is None:
                return new_id
class Employee:
    def __init__(self, id: str, name: str):
        if not isinstance(id, str) or not isinstance(name, str):
            raise TypeError("Employee ID and Name must be strings")
        if not id.strip() or not name.strip(): 
            raise ValueError("Employee ID and Name cannot be empty")
        self.__id = id
        self.__name = name
        self.__slot = []

    @property
    def id(self): return self.__id
    @property
    def slot(self): return self.__slot
    @property
    def name(self): return self.__name 

    def get_slot_by_date(self, date_target: date):
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        return [slot for slot in self.__slot if slot.date == date_target]

    def get_slot_by_date_time(self, date_target: date, time: int):
        if not isinstance(time, int): raise TypeError("Time order must be an integer")
        for slot in self.get_slot_by_date(date_target):
            if slot.slot_order == time:
                return slot
        return None

    def add_slot_by_time(self, slot_list: list, time: int):
        if not isinstance(slot_list, list): raise TypeError("Slot list must be a list")
        if not isinstance(time, int): raise TypeError("Time must be an integer")
        for slot_ in slot_list:
            if slot_.slot_order == time:
                slot_.vacancy += 1

class Admin(Employee):
    def __init__(self, id: str, name: str, spa: Spa, password: str):
        super().__init__(id, name)
        if not isinstance(spa, Spa): raise TypeError("Must be a Spa object")
        if not isinstance(password, str): raise TypeError("Password must be a string")
        if not password: raise ValueError("Password cannot be empty")
        self.__spa = spa
        self.__password = password
        self.__login = False

    @property
    def password(self): return self.__password
    @property
    def login(self): return self.__login
    @property
    def spa(self): return self.__spa

    @login.setter
    def login(self, value: bool):
        if not isinstance(value, bool): raise TypeError("Login status must be a boolean")
        self.__login = value

    def logout(self):
        self.__login = False

class RegistrationOfficer(Admin):
    def add_slot(self, end_date_month: date, entity, vacancy: int):
        if not isinstance(end_date_month, date): raise TypeError("Must be a date object")
        if not isinstance(vacancy, int): raise TypeError("Vacancy must be an integer")
        if not self.login: raise PermissionError("Officer must login first")
        if vacancy < 0: raise ValueError("Vacancy cannot be negative")
        
        year, month, end_date = end_date_month.year, end_date_month.month, end_date_month.day
        for i in range(1, end_date + 1):
            for n in range(1, 17):
                slot = Slot(date(year, month, i), n, vacancy)
                entity.slot.append(slot)
  
    def add_customer(self, customer: Customer):
        if not isinstance(customer, Customer): raise TypeError("Must be a Customer object")
        if not self.login: raise PermissionError("Officer must login first")
        self.spa.add_customer(customer)
        notice_id = f"ENROLL_RESULT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        customer.add_notice_list(Message(notice_id, customer, "Enroll success", datetime.now()))
  
    def add_employee(self, employee: Employee):
        if not isinstance(employee, Employee): raise TypeError("Must be an Employee object")
        if not self.login and not isinstance(employee, (RegistrationOfficer, Administrative)):
             raise PermissionError("Officer must login to add standard employees")
        self.spa.add_employee(employee)

    def add_room(self, room: Room):
        if not isinstance(room, Room): raise TypeError("Must be a Room object")
        if not self.login: raise PermissionError("Officer must login first")
        self.spa.add_room(room)

    def add_resource(self, room_id: str, resource: Resource):
        if not isinstance(room_id, str): raise TypeError("Room ID must be a string")
        if not isinstance(resource, Resource): raise TypeError("Must be a Resource object")
        if not self.login: raise PermissionError("Officer must login first")
        room = self.spa.search_room_by_id(room_id)
        if not room: raise ValueError(f"Room {room_id} not found")
        room.add_resource_list(resource)

    def add_add_on(self, add_on: AddOn):
        if not isinstance(add_on, AddOn): raise TypeError("Must be an AddOn object")
        if not self.login: raise PermissionError("Officer must login first")
        self.spa.add_add_on_list(add_on)

    def add_treatment(self, treatment: Treatment):
        if not isinstance(treatment, Treatment): raise TypeError("Must be a Treatment object")
        if not self.login: raise PermissionError("Officer must login first")
        self.spa.add_treatment(treatment)
    
    def enroll_new_customer(self, name , member_type):
        
        new_customer_id = self.spa.generate_customer_id()

        m_type = member_type.strip().lower()

        if m_type == "bronze":
           customer = Bronze(new_customer_id, name)
        elif m_type == "silver":
           customer = Silver(new_customer_id, name)
        elif m_type == "gold":
           customer = Gold(new_customer_id, name)
        elif m_type == "platinum":
           customer = Platinum(new_customer_id, name)
        else:
            raise Exception("Invalid member type")
        
        # 3. พนักงานบันทึกลูกค้าเข้าสู่ระบบ (เรียกใช้ Method เดิมที่มีอยู่)
        self.add_customer(customer)

        return customer

class Message:
    def __init__(self, id: str, receiver, text: str, date_received: datetime):
        if not isinstance(id, str) or not isinstance(text, str): raise TypeError("ID and text must be strings")
        if not isinstance(date_received, datetime): raise TypeError("Must be a datetime object")
        self.__id = id
        self.__receiver = receiver
        self.__text = text
        self.__date = date_received
        self.__status = "UNREAD"

    @property
    def text(self): return self.__text

class Customer:
    def __init__(self, id: str, name: str):
        if not isinstance(id, str) or not isinstance(name, str):
            raise TypeError("Customer ID and Name must be strings")
        if not id.strip() or not name.strip(): raise ValueError("Customer ID and Name cannot be empty")
        self.__id = id
        self.__name = name
        self.__booking_list = []
        self.__notice_list = []
        self.__missed_count = 0

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def booking_list(self): return self.__booking_list
    @property
    def missed_count(self): return self.__missed_count
    @property
    def notice_list(self): return self.__notice_list
    
    @property
    def discount(self): return 0.0
    @property
    def booking_quota(self): return 0

    def add_notice_list(self, message: Message):
        if not isinstance(message, Message): raise TypeError("Must be a Message object")
        self.__notice_list.append(message)

    def search_booking_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("Booking ID must be a string")
        for booking in self.__booking_list:
            if booking.id == id: return booking
        return None

    def book(self, id: str, customer_id: str, date_booking: date):
        if not isinstance(id, str) or not isinstance(customer_id, str): raise TypeError("IDs must be strings")
        if not isinstance(date_booking, date): raise TypeError("Must be a date object")
        if len(self.__booking_list) >= self.booking_quota:
            raise ValueError("Booking quota exceeded for this customer")
        booking = Booking(id, self, date_booking)
        self.__booking_list.append(booking)
  
    def add_treatment_transaction(self, booking_id: str, treatment_transaction):
        if not isinstance(booking_id, str): raise TypeError("Booking ID must be a string")
        if not isinstance(treatment_transaction, TreatmentTransaction): 
            raise TypeError("Must be a TreatmentTransaction object")
        booking = self.search_booking_by_id(booking_id)
        if not booking: raise ValueError(f"Booking ID {booking_id} not found")
        booking.treatment_list.append(treatment_transaction)

class Bronze(Customer):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self.__discount = 0.0
        self.__booking_quota = 1
        self.__fee = 0
    @property
    def discount(self): return self.__discount
    @property
    def booking_quota(self): return self.__booking_quota

class Silver(Customer):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self.__discount = 0.05
        self.__booking_quota = 2
        self.__fee = 1000
    @property
    def discount(self): return self.__discount
    @property
    def booking_quota(self): return self.__booking_quota
  
class Gold(Customer):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self.__discount = 0.1 
        self.__booking_quota = 3
        self.__fee = 1500
    @property
    def discount(self): return self.__discount
    @property
    def booking_quota(self): return self.__booking_quota

class Platinum(Customer):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self.__discount = 0.2
        self.__booking_quota = 5
        self.__fee = 2500
    @property
    def discount(self): return self.__discount
    @property
    def booking_quota(self): return self.__booking_quota

class TreatmentTransaction:
    def __init__(self, customer, treatment, date_target: date, room, time_slot: list, therapist, add_on_list: list):
        if not isinstance(customer, Customer): raise TypeError("Must be a Customer object")
        if not isinstance(treatment, Treatment): raise TypeError("Must be a Treatment object")
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        if not isinstance(room, Room): raise TypeError("Must be a Room object")
        if not isinstance(therapist, Employee): raise TypeError("Therapist must be an Employee object")
        if not isinstance(time_slot, list) or not time_slot: raise ValueError("Time slot must be a non-empty list")
        if not isinstance(add_on_list, list): raise TypeError("Add-ons must be in a list")

        self.__customer = customer
        self.__treatment = treatment
        self.__date = date_target
        self.__room = room
        self.__time_slot = time_slot
        self.__add_on_list = add_on_list
        self.__therapist = therapist
        self.__status = ""

    @property
    def customer(self): return self.__customer
    @property  
    def treatment(self): return self.__treatment
    @property  
    def date(self): return self.__date
    @property  
    def room(self): return self.__room
    @property  
    def time_slot(self): return self.__time_slot
    @property  
    def add_on_list(self): return self.__add_on_list
    @property
    def therapist(self): return self.__therapist

    def cancle(self):
      for time_order in self.__time_slot:
          room_slot = self.room.get_slot_by_date_time(self.__date, time_order)
          therapist_slot = self.therapist.get_slot_by_date_time(self.__date, time_order)
          if room_slot: room_slot.remove_treatment_transaction(self)
          if therapist_slot: therapist_slot.remove_treatment_transaction(self)
      for addon in self.__add_on_list:
        addon.add_amount(1)
      self.__status = "CANCLE"
      return self.__status == "CANCLE"

class Treatment:
    def __init__(self, id: str, name: str, price: float, duration: int, room_type: str):
        if not isinstance(id, str) or not isinstance(name, str) or not isinstance(room_type, str):
            raise TypeError("ID, name, and room type must be strings")
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if not isinstance(duration, int): raise TypeError("Duration must be an integer")

        if price < 0: raise ValueError("Treatment price cannot be negative")
        if duration <= 0: raise ValueError("Treatment duration must be > 0")
        
        self.__id = id
        self.__name = name
        self.__price = float(price)
        self.__duration = duration
        self.__room_type = room_type

    @property
    def id(self): return self.__id
    @property
    def price(self): return self.__price
    @property
    def room_type(self): return self.__room_type
    @property
    def name(self): return self.__name
    @property
    def duration(self): return self.__duration

class AddOn:
    def __init__(self, id: str, name: str, price: float, amount: int):
        if not isinstance(id, str) or not isinstance(name, str): raise TypeError("ID and name must be strings")
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if not isinstance(amount, int): raise TypeError("Amount must be an integer")
        
        if price < 0: raise ValueError("AddOn price cannot be negative")
        if amount < 0: raise ValueError("AddOn initial amount cannot be negative")
        self.__id = id
        self.__name = name
        self.__price = float(price)
        self.__amount = amount

    @property
    def id(self): return self.__id
    @property
    def price(self): return self.__price
    @property
    def amount(self): return self.__amount

    def reduce_amount(self, value: int):
        if not isinstance(value, int): raise TypeError("Reduction value must be an integer")
        if value < 0: raise ValueError("Reduction value cannot be negative")
        if self.__amount < value:
            raise ValueError(f"Not enough stock for {self.__name} (Available: {self.__amount})")
        self.__amount -= value

    def add_amount(self, value: int):
        if not isinstance(value, int): raise TypeError("Reduction value must be an integer")
        if value < 0: raise ValueError("Reduction value cannot be negative")
        self.__amount += value

class Room:
    def __init__(self, id: str):
        if not isinstance(id, str): raise TypeError("Room ID must be a string")
        if not id: raise ValueError("Room ID cannot be empty")
        self.__id = id
        self.__slot = []
        self.__resource_list = []

    @property
    def id(self): return self.__id
    @property
    def slot(self): return self.__slot
    @property
    def resource_list(self): return self.__resource_list

    def add_resource_list(self, resource: Resource):
        if not isinstance(resource, Resource): raise TypeError("Must be a Resource object")
        self.__resource_list.append(resource)

    def get_slot_by_date(self, date_target: date):
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        return [slot for slot in self.__slot if slot.date == date_target]

    def get_slot_by_date_time(self, date_target: date, time_order: int):
        if not isinstance(time_order, int): raise TypeError("Time order must be an integer")
        for slot in self.get_slot_by_date(date_target):
            if slot.slot_order == time_order:
                return slot
        return None

    def add_slot_by_time(self, slot_list: list, time_order: int):
        if not isinstance(slot_list, list): raise TypeError("Must be a list of slots")
        if not isinstance(time_order, int): raise TypeError("Time order must be an integer")
        for slot_ in slot_list:
            if slot_.slot_order == time_order:
                slot_.vacancy = 1

class DryPrivateRoom(Room):
    def __init__(self, id: str, price: float):
        super().__init__(id)
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if price < 0: raise ValueError("Room price cannot be negative")
        self.__price = float(price)
    @property
    def price(self): return self.__price

class DrySharedRoom(Room):
    def __init__(self, id: str, price: float):
        super().__init__(id)
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if price < 0: raise ValueError("Room price cannot be negative")
        self.__price = float(price)
    @property
    def price(self): return self.__price

class WetPrivateRoom(Room):
    def __init__(self, id: str, price: float):
        super().__init__(id)
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if price < 0: raise ValueError("Room price cannot be negative")
        self.__price = float(price)
    @property
    def price(self): return self.__price

class WetSharedRoom(Room):
    def __init__(self, id: str, price: float):
        super().__init__(id)
        if not isinstance(price, (int, float)): raise TypeError("Price must be a number")
        if price < 0: raise ValueError("Room price cannot be negative")
        self.__price = float(price)
    @property
    def price(self): return self.__price

class Slot:
    def __init__(self, date_target: date, slot_order: int, vacancy: int):
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        if not isinstance(slot_order, int) or not isinstance(vacancy, int): 
            raise TypeError("Slot order and vacancy must be integers")
        
        if not (1 <= slot_order <= 16): raise ValueError("Slot order must be between 1 and 16")
        if vacancy < 0: raise ValueError("Vacancy cannot be negative")
        self.__date = date_target
        self.__slot_order = slot_order
        self.__vacancy = vacancy
        self.__treatment_transaction = []

    @property
    def date(self): return self.__date
    @property
    def slot_order(self): return self.__slot_order
    @property
    def vacancy(self): return self.__vacancy

    @vacancy.setter
    def vacancy(self, value: int):
        if not isinstance(value, int): raise TypeError("Vacancy must be an integer")
        if value < 0: raise ValueError("Vacancy cannot be negative")
        self.__vacancy = value

    @property
    def treatment_transaction(self): return self.__treatment_transaction

    def add_treatment_transaction(self, transaction: TreatmentTransaction):
        if not isinstance(transaction, TreatmentTransaction): raise TypeError("Must be a TreatmentTransaction object")
        if self.__vacancy <= 0:
            raise ValueError(f"Cannot add transaction: Slot {self.__slot_order} is full!")
        self.__treatment_transaction.append(transaction)
        self.__vacancy -= 1

    def remove_treatment_transaction(self, transaction: TreatmentTransaction):
        if not isinstance(transaction, TreatmentTransaction): raise TypeError("Must be a TreatmentTransaction object")
        if transaction in self.__treatment_transaction:
            self.__treatment_transaction.remove(transaction)
            self.__vacancy += 1
  
class Administrative(Admin):
    def create_resource_count_class(self):
        treatment_list = [ResourceCount(t) for t in self.spa.treatment_list]
        addon_list = [ResourceCount(a) for a in self.spa.add_on_list]
        return addon_list, treatment_list

    def calculate_revenue_per_day(self, date_target: date):
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        booking_count = 0
        total_sum = 0
        addon_count, treatment_count = self.create_resource_count_class()
        
        for customer in self.spa.customer_list:
            for booking in customer.booking_list:
                if len(booking.treatment_list) > 0 and booking.treatment_list[0].date == date_target and booking.status == "Completed":
                    booking_count += 1
                    total_sum += booking.calculate_total()
                    for transaction in booking.treatment_list:
                        for resource in treatment_count:
                            if resource.resource.id == transaction.treatment.id:
                                resource.count += 1
                        for resource in addon_count:
                            for addon in transaction.add_on_list:
                                if addon.id == resource.resource.id:
                                    resource.count += 1

        report_revenue = RevenuePerDay(date_target, total_sum, booking_count, addon_count, treatment_count)
        self.spa.revenue_per_day_list.append(report_revenue)
        return report_revenue

class RevenuePerDay:
    def __init__(self, date_target: date, total: float, booking_count: int, addon_count: list, treatment_count: list):
        self.__date = date_target
        self.__total = total
        self.__booking_count = booking_count
        self.__addon_count = addon_count
        self.__treatment_count = treatment_count

    @property
    def booking_count(self): return self.__booking_count
    @property
    def total(self): return self.__total
    @property
    def date(self): return self.__date
    @property
    def addon_count(self): return self.__addon_count
    @property
    def treatment_count(self): return self.__treatment_count 

class ResourceCount:
    def __init__(self, resource):
        self.__resource = resource
        self.__count = 0

    @property
    def resource(self): return self.__resource
    @property
    def count(self): return self.__count

    @count.setter
    def count(self, value: int):
        if not isinstance(value, int): raise TypeError("Count must be an integer")
        if value < 0: raise ValueError("Count cannot be negative")
        self.__count = value

class Payment(ABC):
    @abstractmethod
    def pay_deposit(self, deposit: float, **kwargs): pass
    @abstractmethod
    def pay_expenses(self, total: float, **kwargs): pass

class Cash(Payment):
    def pay_deposit(self, deposit: float, money: float):
        if not isinstance(deposit, (int, float)) or not isinstance(money, (int, float)):
            raise TypeError("Deposit and money must be numbers")
        if money < 0: raise ValueError("Money cannot be negative")
        if money < deposit: return f"You have to pay {deposit} ฿ for deposit⚠️"
        return "Your booking confirmed✅"

    def pay_expenses(self, total: float, money: float):
        if not isinstance(total, (int, float)) or not isinstance(money, (int, float)):
            raise TypeError("Total and money must be numbers")
        if money < 0: raise ValueError("Money cannot be negative")
        if money < total: return f"Not enough money! You have to pay {total} ฿⚠️"
        return f"Payment Success✅, Your change = {money - total} ฿"

class Card(Payment):
    def pay_deposit(self, deposit: float, number: str):
        if not isinstance(deposit, (int, float)): raise TypeError("Deposit must be a number")
        if not isinstance(number, str): raise TypeError("Card number must be a string")
        if deposit < 0: raise ValueError("Deposit cannot be negative")
        return f"Your booking confirmed✅, {deposit} ฿ deducted from your card (Card id : {number})"

    def pay_expenses(self, total: float, number: str):
        if not isinstance(total, (int, float)): raise TypeError("Total must be a number")
        if not isinstance(number, str): raise TypeError("Card number must be a string")
        if total < 0: raise ValueError("Total cannot be negative")
        return f"Payment Success✅, {total} ฿ deducted from your card (Card id : {number})"

class Booking:
    def __init__(self, id: str, customer: Customer, date_target: date):
        if not isinstance(id, str): raise TypeError("Booking ID must be a string")
        if not isinstance(customer, Customer): raise TypeError("Must be a Customer object")
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        if not id: raise ValueError("Booking ID cannot be empty")
        
        self.__id = id
        self.__customer = customer
        self.__date = date_target
        self.__treatment_list = []
        self.__status = "Waiting deposit"

    @property
    def id(self): return self.__id
    @property
    def treatment_list(self): return self.__treatment_list
    @property
    def date(self): return self.__date
    @property
    def status(self): return self.__status

    @status.setter
    def status(self, value: str):
        if not isinstance(value, str): raise TypeError("Status must be a string")
        self.__status = value

    def calculate_total(self):
        total = 0.0
        for transaction in self.treatment_list:
            total += transaction.treatment.price
            total += transaction.room.price
            for add_on in transaction.add_on_list:
                total += add_on.price

        discount = total * self.__customer.discount
        total -= discount
        return max(0, total) 

    def pay_expenses(self, payment: Payment, total: float, **kwargs):
        if not isinstance(payment, Payment): raise TypeError("Must be a Payment object")
        if not isinstance(total, (int, float)): raise TypeError("Total must be a number")
        if total < 0: raise ValueError("Total cannot be negative")
        self.__status = "Completed"
        return payment.pay_expenses(total, **kwargs)

    def pay_deposit(self, payment: Payment, deposit: float, **kwargs):
        if not isinstance(payment, Payment): raise TypeError("Must be a Payment object")
        if not isinstance(deposit, (int, float)): raise TypeError("Deposit must be a number")
        if deposit < 0: raise ValueError("Deposit cannot be negative")
        self.__status = "Confirmed"
        return payment.pay_deposit(deposit, **kwargs)

    def cancle(self):
        for transaction in self.__treatment_list:
            transaction.cancle()
        self.__status = "CANCEL"
        return "Cancel Success✅"

class Therapist(Employee):
    def __init__(self, id: str, name: str, skill: SkillSets):
        super().__init__(id, name)
        if not isinstance(skill, SkillSets): raise TypeError("Skill must be a SkillSets object")
        self.__skill = skill
        self.__points = 0

    @property
    def skill(self):
      return self.__skill

class Resource:
    def __init__(self, id: str, name: str, amount: int):
        if not isinstance(id, str) or not isinstance(name, str): raise TypeError("ID and name must be strings")
        if not isinstance(amount, int): raise TypeError("Amount must be an integer")
        if amount < 0: raise ValueError("Resource amount cannot be negative")
        self.__id = id
        self.__name = name
        self.__amount = amount
        self.__status = "Available"

# ==========================================
# 2. SYSTEM INITIALIZATION
# ==========================================

def init_system():

  spa = Spa(name="LADKRABANG SPA")

  # Service //
  massage1 = Treatment(id="TM-01", name='Traditional Thai Massage', price=600, duration=60, room_type='DRY')
  massage2 = Treatment(id="TM-02", name='Traditional Thai Massage', price=850, duration=90, room_type='DRY')
  massage3 = Treatment(id="TM-03", name='Traditional Thai Massage', price=1100, duration=120, room_type='DRY')
  massage4 = Treatment(id="DT-03", name='Deep Tissue Massage', price=1200, duration=60, room_type='DRY')
  aroma = Treatment(id="AT-02", name='Aroma Therapy', price=1500, duration=90, room_type='DRY')
  pool = Treatment(id="HP-04", name='Hydrotherapy Pool', price=800, duration=60, room_type='WET')

  # Customer //
  c1 = Silver(id="C0001", name="Batman")
  c2 = Silver(id="C0002", name="Aquaman")
  c3 = Bronze(id="C0003", name="Superman")
  c4 = Gold(id="C0004", name="Iron Man")
  c5 = Platinum(id="C0005", name="Spider-Man")
  c6 = Gold(id="C0006", name="Wonder Woman")
  c7 = Silver(id="C0007", name="Black Widow")
  c8 = Bronze(id="C0008", name="Thor")
  c9 = Platinum(id="C0009", name="Hulk")
  c10 = Bronze(id="C0010", name="Flash")
  
  # Employee // 
  t1 = Therapist(id="T0001", name="John", skill=SkillSets.TM)
  t2 = Therapist(id="T0002", name="Anna", skill=SkillSets.TM)

  t3 = Therapist(id="T0003", name="Emma", skill=SkillSets.AT)
  t4 = Therapist(id="T0004", name="Olivia", skill=SkillSets.AT)
    
  t5 = Therapist(id="T0005", name="Justin", skill=SkillSets.DT)
  t6 = Therapist(id="T0006", name="Sophia", skill=SkillSets.DT)

  t7 = Therapist(id="T0007", name="Mary", skill=SkillSets.HP)
  t8 = Therapist(id="T0008", name="Matha", skill=SkillSets.HP)

  # Room //
  dr_p1 = DryPrivateRoom(id="ROOM-DRY-PV-001", price=300)
  dr_p2 = DryPrivateRoom(id="ROOM-DRY-PV-002", price=300)
  dr_p3 = DryPrivateRoom(id="ROOM-DRY-PV-003", price=300)
  dr_s1 = DrySharedRoom(id="ROOM-DRY-SH-001", price=0)
  dr_s2 = DrySharedRoom(id="ROOM-DRY-SH-002", price=0)

    
  wr_p1 = WetPrivateRoom(id="ROOM-WET-PV-001", price=300)
  wr_p2 = WetPrivateRoom(id="ROOM-WET-PV-002", price=300)
  wr_p3 = WetPrivateRoom(id="ROOM-WET-PV-003", price=300)
  wr_s1 = WetSharedRoom(id="ROOM-WET-SH-001", price=0)

  # Resource //
  res1 = Resource(id="RES-0001-BED", name="Massage Bed", amount=1)
  res2 = Resource(id="RES-0002-BED", name="Massage Bed", amount=1)
  res3 = Resource(id="RES-0003-BED", name="Massage Bed", amount=1)
  res4 = Resource(id="RES-0004-BED", name="Massage Bed", amount=1)
  res5 = Resource(id="RES-0005-BED", name="Massage Bed", amount=1)
  res6 = Resource(id="RES-0006-BED", name="Massage Bed", amount=1)
  res7 = Resource(id="RES-0007-POOL", name="Hydrotherapy Pool", amount=1)
  res8 = Resource(id="RES-0008-POOL", name="Hydrotherapy Pool", amount=1)
  res9 = Resource(id="RES-0009-POOL", name="Hydrotherapy Pool", amount=1)

  # Add on //
  add_on1 = AddOn(id="OIL-P", name="Premium Essential Oil", price=350, amount=100)
  add_on2 = AddOn(id="CMP-H", name="Herbal Compress", price=250, amount=100)
  add_on3 = AddOn(id="SCRB-D", name="Detox Scrub", price=450, amount=100) 
  add_on4 = AddOn(id="SNK-S", name="After-Service Snack Set", price=150, amount=100) 

  # Create Operation Officer //
  reg1 = RegistrationOfficer(id="0001", name="Kevin", spa=spa, password="12345")
  ad1 = Administrative(id="0002", name="Paul", spa=spa, password="12345")
  web_officer = RegistrationOfficer(id="WEB0001", name="Max", spa=spa, password="12345")

  # Add themselves //
  reg1.add_employee(reg1)
  reg1.add_employee(ad1)  
  reg1.add_employee(web_officer)  
  

  # Login //
  spa.verify_admin(reg1.id, "12345")
  spa.verify_admin(web_officer.id, "12345")
  
  # Add service //
  reg1.add_treatment(massage1)
  reg1.add_treatment(massage2)
  reg1.add_treatment(massage3)
  reg1.add_treatment(massage4)
  reg1.add_treatment(aroma)
  reg1.add_treatment(pool)

  # Add customer //
  reg1.add_customer(c1)
  reg1.add_customer(c2)
  reg1.add_customer(c3)
  reg1.add_customer(c4)
  reg1.add_customer(c5)
  reg1.add_customer(c6)
  reg1.add_customer(c7)
  reg1.add_customer(c8)
  reg1.add_customer(c9)
  reg1.add_customer(c10)

  # Add employee //
  end_date_month = date(2026, 2, 28)

  reg1.add_employee(t1)
  reg1.add_slot(end_date_month, t1, 1)
  reg1.add_employee(t2)
  reg1.add_slot(end_date_month, t2, 1)
  reg1.add_employee(t3)
  reg1.add_slot(end_date_month, t3, 1)
  reg1.add_employee(t4)
  reg1.add_slot(end_date_month, t4, 1)
  reg1.add_employee(t5)
  reg1.add_slot(end_date_month, t5, 1)
  reg1.add_employee(t6)
  reg1.add_slot(end_date_month, t6, 1)
  reg1.add_employee(t7)
  reg1.add_slot(end_date_month, t7, 1)
  reg1.add_employee(t8)
  reg1.add_slot(end_date_month, t8, 1)

  reg1.add_room(dr_p1)
  reg1.add_slot(end_date_month, dr_p1, 1)
  reg1.add_room(dr_p2)
  reg1.add_slot(end_date_month, dr_p2, 1)
  reg1.add_room(dr_p3)
  reg1.add_slot(end_date_month, dr_p3, 1)
  reg1.add_room(wr_p1)
  reg1.add_slot(end_date_month, wr_p1, 1)
  reg1.add_room(wr_p2)
  reg1.add_slot(end_date_month, wr_p2, 1)
  reg1.add_room(wr_p3)
  reg1.add_slot(end_date_month, wr_p3, 1)
  reg1.add_room(dr_s1)
  reg1.add_slot(end_date_month, dr_s1, 10)
  reg1.add_room(dr_s2)
  reg1.add_slot(end_date_month, dr_s2, 10)
  reg1.add_room(wr_s1)
  reg1.add_slot(end_date_month, wr_s1, 10)

  reg1.add_resource(dr_p1.id, res1)
  reg1.add_resource(dr_p2.id, res2)
  reg1.add_resource(dr_p3.id, res3)
  reg1.add_resource(dr_s1.id, res4)
  reg1.add_resource(wr_p1.id, res5)
  reg1.add_resource(wr_p2.id, res6)
  reg1.add_resource(wr_p3.id, res7)
  reg1.add_resource(wr_s1.id, res8)
  reg1.add_resource(wr_s1.id, res9)
  
  reg1.add_add_on(add_on1)
  reg1.add_add_on(add_on2)
  reg1.add_add_on(add_on3)
  reg1.add_add_on(add_on4)
   
  return spa

spa = init_system()

# ==========================================
# 3. API ROUTES & PYDANTIC VALIDATION (OUTER LAYER)
# ==========================================

class RequestGetSlot(BaseModel):
    customer_id: str = Field(..., min_length=1)
    therapist_id: str = Field(..., min_length=1)
    treatment_id: str = Field(..., min_length=1)
    room_type: str = Field(..., min_length=1)
    year: int = Field(..., ge=2024)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)

class ResponseSlot(BaseModel): time: str

class ResponseGetSlot(BaseModel):
    room_id: str
    year: int
    month: int
    day: int
    slot: list[ResponseSlot]

time = {
  1: "8:00-8:30", 2: "8:30-9:00", 3: "9:00-9:30", 4: "9:30-10:00",
  5: "10:00-10:30", 6: "10:30-11:00", 7: "11:00-11:30", 8: "11:30-12:00",
  9: "12:00-12:30", 10: "12:30-13:00", 11: "13:00-13:30", 12: "13:30-14:00",
  13: "14:00-14:30", 14: "14:30-15:00", 15: "15:00-15:30", 16: "15:30-16:00",
}

treatment_dict = {
  "Traditional Thai Massage" : ["TM-01", "TM-02", "TM-03"],
  "Aroma Therapy" : ["AT-02"],
  "Deep Tissue Massage" : ["DT-03"],
  "Hydrotherapy Pool" : ["HP-04"],
}

@app.post("/getSlot", response_model=list[ResponseGetSlot])
def find_free_slot(req: RequestGetSlot):
    try:
        date_class = date(req.year, req.month, req.day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    customer = spa.search_customer_by_id(req.customer_id)
    if not customer: raise HTTPException(status_code=404, detail="Customer not found")

    therapist = spa.search_employee_by_id(req.therapist_id)
    if not therapist: raise HTTPException(status_code=404, detail="Therapist not found")

    treatment = spa.search_treatment_by_id(req.treatment_id)
    if not treatment: raise HTTPException(status_code=404, detail="Treatment not found")

    if treatment.id not in treatment_dict.get(therapist.skill.value,[]):
      raise HTTPException(
            status_code=400, 
            detail="The requested treatment does not match the selected therapist's skill ⚠️"
        )

    therapist_slot = therapist.get_slot_by_date(date_class)
    room_type_str = f'ROOM-{treatment.room_type}-{req.room_type}'
    room_list = spa.get_room_by_room_type(room_type_str)
    
    if not room_list: raise HTTPException(status_code=404, detail="Room type not found")

    result = []
    for room in room_list:
        room_slot = room.get_slot_by_date(date_class)
        free_slots = spa.find_intersect_free_slot(room_slot, therapist_slot)
        
        if free_slots: 
            result.append(
                ResponseGetSlot(
                    room_id=room.id, year=free_slots[0].date.year,
                    month=free_slots[0].date.month, day=free_slots[0].date.day,
                    slot=[ResponseSlot(time=time[slot.slot_order]) for slot in free_slots]
                )
            )
    return result

class RequestCancleBooking(BaseModel):
    booking_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
  
@app.post("/cancelBooking", response_model=str)
def cancel_booking(req: RequestCancleBooking):
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer: raise HTTPException(status_code=404, detail="Customer not found")

    booking = customer.search_booking_by_id(req.booking_id)
    if not booking: raise HTTPException(status_code=404, detail="Booking not found")

    result = booking.cancle()
    return result

class RequestTreatment(BaseModel):
    therapist_id: str = Field(..., min_length=1)
    treatment_id: str = Field(..., min_length=1)
    room_id: str = Field(..., min_length=1)
    time: str = Field(..., min_length=1)
    addon: list[str]

class RequestBooking(BaseModel):
    customer_id: str = Field(..., min_length=1)
    year: int = Field(..., ge=2024)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    treatments: list[RequestTreatment]

class ResponseRequestBooking(BaseModel):
    status: str
    booking_id: str

def change_str_to_index_list(str_time):
    result = []
    found_start_time = False
    try:
        start_time, end_time = str_time.split("-")
    except ValueError:
        return [] 
    for key, value in time.items():
        start, end = value.split("-")
        if start_time == start:
            result.append(key)
            found_start_time = True
            if end_time == end: return result
            continue
        if found_start_time:
            result.append(key)
        if end_time == end: return result
    return result

def is_continuous(numbers):
    if not numbers:
        return False

    numbers = sorted(numbers)

    for i in range(len(numbers) - 1):
        if numbers[i + 1] - numbers[i] != 1:
            return False

    return True


@app.post("/requestBooking", response_model=ResponseRequestBooking)
def request_booking(req: RequestBooking):
    try:
        date_booking = date(req.year, req.month, req.day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    customer = spa.search_customer_by_id(req.customer_id)
    if not customer: raise HTTPException(status_code=404, detail="Customer not found")

    if customer.booking_quota <= len(customer.booking_list) or customer.missed_count > 2:
        raise HTTPException(status_code=400, detail="CANNOT MAKE BOOKING: Quota exceeded or missed too many")

    d = date.today()
    booking_id = f'BK-{d.year}{d.month if len(str(d.month)) > 1 else f"0{d.month}"}{d.day if len(str(d.day)) > 1 else f"0{d.day}"}-{spa.booking_count}'

    customer.book(booking_id, customer.id, d)

    for treat in req.treatments:
        treatment = spa.search_treatment_by_id(treat.treatment_id)
        if not treatment: raise HTTPException(status_code=404, detail=f"Treatment {treat.treatment_id} not found")

        room = spa.search_room_by_id(treat.room_id)
        if not room: raise HTTPException(status_code=404, detail=f"Room {treat.room_id} not found")

        therapist = spa.search_employee_by_id(treat.therapist_id)
        if not therapist: raise HTTPException(status_code=404, detail=f"Therapist {treat.therapist_id} not found")

        addon_list = []
       
        addon_list_enough = []
        addon_list_not_enough = []
        for id in treat.addon:
            addon = spa.search_add_on_by_id(id)
            if addon.amount < 1:
                addon_list_not_enough.append(addon)
            else:
                addon_list_enough.append(addon)

        if len(addon_list_not_enough) >= 1: raise HTTPException(status_code=404, detail=f"{', '.join(str(addon.id) for addon in addon_list_not_enough)} was not enough")

        for id in treat.addon:
            addon = spa.search_add_on_by_id(id)
            if not addon: raise HTTPException(status_code=404, detail=f"Add-on {id} not found")
            addon.reduce_amount(1)
            addon_list.append(addon)

        slot = change_str_to_index_list(treat.time)
        if not slot: raise HTTPException(status_code=400, detail="Invalid time format")
        if not is_continuous(slot): raise HTTPException(status_code=404, detail=f"Invalid, Time must be continuous")
        if len(slot)*30 != treatment.duration : raise HTTPException(status_code=400, detail=f"Time must be exactly {treatment.duration} minutes.")

        treatment_transaction = TreatmentTransaction(customer, treatment, date_booking, room, slot, therapist, addon_list)
        customer.add_treatment_transaction(booking_id, treatment_transaction)
        
        room_slot = room.get_slot_by_date(date_booking)
        therapist_slot = therapist.get_slot_by_date(date_booking)

        try:
            for order in slot:
                for slot_ in room_slot:
                    if slot_.slot_order == order:
                        slot_.add_treatment_transaction(treatment_transaction)
                for slot_ in therapist_slot:
                    if slot_.slot_order == order:
                        slot_.add_treatment_transaction(treatment_transaction)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=str(e)) 

    spa.booking_count += 1

    return ResponseRequestBooking(status="SUCCESS", booking_id=booking_id)

# print(find_free_slot(RequestGetSlot(customer_id = "C0001", therapist_id = "T0001", treatment_id = "TM-01", room_type = "SH", year = 2026, month = 1, day = 10)))

# request_data = Request_booking(
#     customer_id="C0001",
#     year=2026,
#     month=1,
#     day=10,
#     treatments=[
#         RequestTreatment(
#             therapist_id="T0001",  
#             treatment_id="TM-01",
#             room_id="ROOM-DRY-SH-001",
#             time="8:00-8:30",
#             addon=["OIL-P", "CMP-H"]
#         )
#     ]
# )

# print(request_booking(request_data))

# print(find_free_slot(RequestGetSlot(customer_id = "C0001", therapist_id = "T0001", treatment_id = "TM-01", room_type = "SH", year = 2026, month = 1, day = 10)))


class RequestToPay(BaseModel):
  customer_id:str
  booking_id:str
  payment_type:str
  payment_value:int
@app.post("/requestToPay",response_model=str)
def request_to_pay(req :RequestToPay):
    customer = spa.search_customer_by_id(req.customer_id)
    booking = customer.search_booking_by_id(req.booking_id)
    total = booking.calculate_total()
    
    if req.payment_type == "Cash":
      cash = Cash()
      return booking.pay_expenses(cash, total, money=req.payment_value) 
    elif req.payment_type == "Card":
      card = Card()
      return booking.pay_expenses(card, total, number=req.payment_value)



class RequestToCalculateRevenuePerDay(BaseModel):
   admin_id:str
   year:int
   month:int
   day:int
class ResponseAddOnUsage(BaseModel):
  addon_id:str
  count:int
class ResponseTreatmentUsage(BaseModel):
  treatment_id:str
  count:int
class ResponseReportPerDay(BaseModel):
  day:int
  year:int
  month:int
  total:float
  addon_list_count:list[ResponseAddOnUsage]
  treatment_list_count:list[ResponseTreatmentUsage]
@app.post("/requestToCalculateRevenuePerDay",response_model=ResponseReportPerDay)
def request_to_calculate_revenue_per_day(req :RequestToCalculateRevenuePerDay):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  date_to_cal = date(req.year, req.month, req.day)
  admin = spa.search_employee_by_id(req.admin_id)
  report = admin.calculate_revenue_per_day(date_to_cal)

  # PART 2 -> PARSE INTO JSON
  result = ResponseReportPerDay(day=report.date.day,
                                   month=report.date.month,
                                   year=report.date.year,
                                   total=report.total,
                                   addon_list_count=[ResponseAddOnUsage(addon_id=addon.resource.id,count=addon.count) for addon in report.addon_count],
                                   treatment_list_count=[ResponseTreatmentUsage(treatment_id=addon.resource.id,count=addon.count) for addon in report.treatment_count]
                                   )
  return result




class ResponseEmployeeSlot(BaseModel):
    time:str
    room_id:str
    treatment_id:str
    customer_id:str
class ResponseEmployeeSchedule(BaseModel):
  year:int
  month:int
  day:int
  slot:list[ResponseEmployeeSlot]
class Request_employee_schedule(BaseModel):
  employee_id:str
  year:int
  month:int
  day:int
@app.post("/requestEmployeeSchedule",response_model=ResponseEmployeeSchedule)
def request_employee_schedule(req :Request_employee_schedule):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  employee = spa.search_employee_by_id(req.employee_id)
  d = date(req.year,req.month,req.day)
  slot_day = employee.get_slot_by_date(d)

  # PART 2 -> PARSE INTO JSON
  sub_result = []
  for slot in slot_day:
   if slot.vacancy == 1:
    sub_result.append(ResponseEmployeeSlot(time=time[slot.slot_order],room_id="",treatment_id="",customer_id=""))
   else:
    sub_result.append(ResponseEmployeeSlot(time=time[slot.slot_order],room_id=slot.treatment_transaction[0].room.id,treatment_id=slot.treatment_transaction[0].treatment.id,customer_id=slot.treatment_transaction[0].customer.id))
  result = ResponseEmployeeSchedule(year=req.year,month=req.month,day=req.day,slot=sub_result)
  return result 




class ResponseRoomDetail(BaseModel):
  customer_id:str
  treatment_id:str
  employee_id:str
class ResponseRoomSlot(BaseModel):
  time:str
  detail: list[ResponseRoomDetail]
class ResponseRoomSchedule(BaseModel):
  year:int
  month:int
  day:int
  slot:list[ResponseRoomSlot]
class RequestRoomSchedule(BaseModel):
  room_id:str
  year:int
  month:int
  day:int
@app.post("/requestRoomSchedule",response_model=ResponseRoomSchedule)
def request_room_schedule(req :RequestRoomSchedule):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  room = spa.search_room_by_id(req.room_id)
  d = date(req.year,req.month,req.day)
  slot_day = room.get_slot_by_date(d)
  sub_result = []

  # PART 2 -> PARSE INTO JSON
  for slot in slot_day:
   sub_sub_result = []
   for treatment in slot.treatment_transaction:
       sub_sub_result.append(ResponseRoomDetail(customer_id=treatment.customer.id,treatment_id=treatment.treatment.id,employee_id=treatment.therapist.id))
   sub_result.append(ResponseRoomSlot(time=time[slot.slot_order],detail=sub_sub_result))
  result = ResponseRoomSchedule(year=req.year,month=req.month,day=req.day,slot=sub_result)
  return result 

if __name__ == "__main__":
    uvicorn.run("spa:app", host="127.0.0.1", port=8000, log_level="info")




class RequestEnrollCustomer(BaseModel):
    customer_name: str
    member_type: str

class ResponseEnrollCustomer(BaseModel):
    status: str
    customer_id: str
    member_type: str              
    message: str


# API ENDPOINT
@app.post("/enrollCustomer", response_model=ResponseEnrollCustomer)
def enroll_customer(req: RequestEnrollCustomer):
    try:
        # 1. ไปตามหา Max (WEB0001)
        officer = spa.search_employee_by_id("WEB0001")
        
        # 2. มอบหมายงานให้ Max จัดการทั้งหมด
        customer = officer.enroll_new_customer(req.customer_name, req.member_type)

        return ResponseEnrollCustomer(
            status="SUCCESS",
            customer_id=customer.id,
            member_type=req.member_type,
            message=f"Registered by {officer.name}"
        )

    except: 
        return ResponseEnrollCustomer(
            status="FAILED",
            customer_id="",
            member_type=req.member_type,
            message="Registration failed. Please check your data or contact admin."
        )