from __future__ import annotations
from datetime import date, datetime, timedelta, time
from typing import Dict
from enum import Enum
from fastapi import FastAPI, HTTPException, Body
import uvicorn
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import re

from fastmcp import FastMCP

mcp = FastMCP("Spa_system")
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

    def create_booking_id(self,d :date):
        return f'BK-{d.year}{d.month if len(str(d.month)) > 1 else f"0{d.month}"}{d.day if len(str(d.day)) > 1 else f"0{d.day}"}-{spa.booking_count}'

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

    def add_treatment_trasaction_at_date_time(self,treatment:TreatmentTransaction,date:date,time:int):
        slot = self.get_slot_by_date_time(date,time)
        slot.add_treatment_transaction(treatment)

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

    def enroll_new_customer(self, name, member_type):
        
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
        
        self.add_customer(customer)

        return customer
    
class Coupon:
    def __init__(self, id: str, discount: float):
        self.__id = id
        self.__discount = discount

    @property
    def id(self):
        return self.__id

    @property
    def discount(self):
        return self.__discount

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
    @property
    def date(self): return self.__date
    @property
    def status(self): return self.__status
    @property
    def id(self): return self.__id

    @status.setter
    def status(self, value):
        self.__status = value

class Customer:
    def __init__(self, id: str, name: str):
        if not isinstance(id, str) or not isinstance(name, str):
            raise TypeError("Customer ID and Name must be strings")
        if not id.strip() or not name.strip(): raise ValueError("Customer ID and Name cannot be empty")
        self.__id = id
        self.__name = name
        self.__booking_list = []
        self.__notice_list = []
        self.__coupon_list = []
        self.__wellness_record = []
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
    def wellness_record(self): return self.__wellness_record
    @property
    def discount(self): return 0.0
    @property
    def booking_quota(self): return 0

    def add_notice_list(self, message: Message):
        if not isinstance(message, Message): raise TypeError("Must be a Message object")
        self.__notice_list.append(message)

    def add_coupon_list(self, coupon: Coupon):
        if not isinstance(coupon, Coupon): raise TypeError("Must be a Coupon object")
        self.__coupon_list.append(coupon)

    def add_wellness_record(self, record: WellnessRecord):
        if not isinstance(record, WellnessRecord): raise TypeError("Must be a WellnessRecord object")
        self.__wellness_record.append(record)

    def search_coupon_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("Coupon ID Must be a string")
        for coupon in self.__coupon_list:
            if coupon.id == id:
                return coupon
        return None

    def remove_coupon_by_id(self, coupon_id: str):
        if not isinstance(id, str): raise TypeError("Coupon ID Must be a string")
        coupon = self.search_coupon_by_id(coupon_id)
        self.__coupon_list.remove(coupon)

    def search_booking_by_id(self, id: str):
        if not isinstance(id, str): raise TypeError("Booking ID must be a string")
        for booking in self.__booking_list:
            if booking.id == id: return booking
        return None

    def book(self,booking:Booking):
        self.__booking_list.append(booking)
  
    def add_treatment_transaction(self, booking_id: str, treatment_transaction):
        if not isinstance(booking_id, str): raise TypeError("Booking ID must be a string")
        if not isinstance(treatment_transaction, TreatmentTransaction): 
            raise TypeError("Must be a TreatmentTransaction object")
        booking = self.search_booking_by_id(booking_id)
        if not booking: raise ValueError(f"Booking ID {booking_id} not found")
        booking.treatment_list.append(treatment_transaction)

    def get_active_booking(self):
        active_booking_list = []
        for booking in self.__booking_list:
            if booking.status == "Waiting deposit" or booking.status == "Confirmed":
                active_booking_list.append(booking)
        return active_booking_list

    def get_completed_booking(self):
        completed_booking_list = []
        for booking in self.__booking_list:
            if booking.status == "Completed" or booking.status == "Cancelled":
                completed_booking_list.append(booking)
        return completed_booking_list

    def check_notice(self):
        unread_notice = []
        for notice in self.__notice_list:
            if notice.status == "UNREAD":
                unread_notice.append(notice)
        return unread_notice

    def read_notice(self, notice_id: str):
        for notice in self.__notice_list:
            if notice.id == notice_id:
                notice.status = "READ"
                return notice
        return None
    
    def change_personal_info(self, new_name:str):
        if not isinstance (new_name, str) or not new_name.strip():
            raise ValueError("New name must be a non-empty string")
        old_name = self.__name
        self.__name = new_name
        return f"Name updated from {old_name} to {new_name}"
    
    def rating_employee(self, employee: Employee, score: int):
        if not isinstance(employee, Employee):
            raise TypeError("employee must be Employee object")
        
        employee.add_rating(score)

        avg_score = employee.get_average_rating()
        
        return f"Successfully rated {employee.name}! ({score} stars) | Current Average Rating: {avg_score:.2f} stars"
    
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
    @property
    def name(self): return self.__name

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
    
    def is_ava(self):
        return self.__amount > 0

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
        
    def add_treatment_trasaction_at_date_time(self,treatment:TreatmentTransaction,date:date,time:int):
        slot = self.get_slot_by_date_time(date,time)
        slot.add_treatment_transaction(treatment)

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

    def is_ava(self):
        return self.__vacancy > 0
  
class Administrative(Admin):
    def calculate_revenue_per_day(self, date_target: date):
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        booking_count = 0
        total_sum = 0
        treatment_count = {
            "Traditional Thai Massage": 0,
            "Aroma Therapy": 0,
            "Deep Tissue Massage": 0,
            "Hydrotherapy Pool": 0
        }
        addon_count = {
            "Premium Essential Oil": 0,
            "Herbal Compress": 0,
            "Detox Scrub": 0,
            "After-Service Snack Set": 0
        }
        
        for customer in self.spa.customer_list:
            for booking in customer.booking_list:
                if len(booking.treatment_list) > 0 and booking.treatment_list[0].date == date_target and booking.status == "Completed":
                    booking_count += 1
                    if booking.coupon_used_record is not None:
                        coupon_used = booking.coupon_used_record.id
                    else:
                        coupon_used = "None"
                    total_sum += booking.calculate_total(coupon_used)
                    for transaction in booking.treatment_list:
                        treatment_count[transaction.treatment.name] += 1
                        for addon in transaction.add_on_list:
                            addon_count[addon.name] += 1

        report_revenue = {
                            "date": date_target,
                            "total": total_sum,
                            "booking_count": booking_count,
                            "treatment_count": treatment_count,
                            "addon_count": addon_count
                        }
        return report_revenue
    
    def send_promotion(self, promo_text: str):
        if not isinstance(promo_text, str) or not promo_text.strip():
            raise ValueError("Promotion must be non-empty string")
        
        customer_list = self.spa.customer_list 
        count = 0
        now = datetime.now()

        for customer in customer_list:
            notice_id = f"PROMOTION-{now.strftime('%Y%m%d%H%M%S')}-{customer.id}"
            promo_msg = Message(notice_id, customer, promo_text, now)
            customer.add_notice_list(promo_msg)
            count += 1
            
        return f"Promotion sent {count} person"
    
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
        if money < deposit: return "False", f"You have to pay {deposit} ฿ for deposit⚠️"
        return "True", f"Your booking confirmed✅, Paid for deposit {deposit} ฿ Your change = {money - deposit} ฿"

    def pay_expenses(self, total: float, money: float):
        if not isinstance(total, (int, float)) or not isinstance(money, (int, float)):
            raise TypeError("Total and money must be numbers")
        if money < 0: raise ValueError("Money cannot be negative")
        if money < total: return "False", f"Not enough money! You have to pay {total} ฿⚠️"
        return "True", f"Payment Success✅, Paid total {total} ฿ Your change = {money - total} ฿"

class Card(Payment):
    def pay_deposit(self, deposit: float, number: str):
        if not isinstance(deposit, (int, float)): raise TypeError("Deposit must be a number")
        if not isinstance(number, str): raise TypeError("Card number must be a string")
        if deposit < 0: raise ValueError("Deposit cannot be negative")
        return "True", f"Your booking confirmed✅, {deposit} ฿ deducted from your card (Card id : {number})"

    def pay_expenses(self, total: float, number: str):
        if not isinstance(total, (int, float)): raise TypeError("Total must be a number")
        if not isinstance(number, str): raise TypeError("Card number must be a string")
        if total < 0: raise ValueError("Total cannot be negative")
        return "True", f"Payment Success✅, {total} ฿ deducted from your card (Card id : {number})"

class Booking:
    def __init__(self, id: str, customer: Customer, date_target: date,treat_list:list[TreatmentTransaction]):
        if not isinstance(id, str): raise TypeError("Booking ID must be a string")
        if not isinstance(customer, Customer): raise TypeError("Must be a Customer object")
        if not isinstance(date_target, date): raise TypeError("Must be a date object")
        if not id: raise ValueError("Booking ID cannot be empty")
        
        self.__id = id
        self.__customer = customer
        self.__date = date_target
        self.__treatment_list = treat_list
        self.__coupon_used_record = None
        self.__status = "Waiting deposit"

    @property
    def id(self): return self.__id
    @property
    def treatment_list(self): return self.__treatment_list
    @property
    def date(self): return self.__date
    @property
    def status(self): return self.__status
    @property
    def coupon_used_record(self): return self.__coupon_used_record

    @status.setter
    def status(self, value: str):
        if not isinstance(value, str): raise TypeError("Status must be a string")
        self.__status = value

    def calculate_total(self, coupon_id: str):
        if coupon_id != "None":
            coupon = self.__customer.search_coupon_by_id(coupon_id)
            if coupon is None:
                return False
            self.__coupon_used_record = coupon
            coupon_discount = coupon.discount
        else:
            coupon_discount = 0
            coupon = None

        total = 0.0
        for transaction in self.treatment_list:
            total += transaction.treatment.price

        discount = total * self.__customer.discount
        total -= discount
        total -= coupon_discount

        if coupon is not None:
            self.__customer.remove_coupon_by_id(coupon_id)
        
        return max(0, total) 

    def pay_expenses(self, payment: Payment, total: float, **kwargs):
        if not isinstance(payment, Payment): raise TypeError("Must be a Payment object")
        if not isinstance(total, (int, float)): raise TypeError("Total must be a number")
        if total < 0: raise ValueError("Total cannot be negative")
        if self.__status == "Checked-In":
            status, text = payment.pay_expenses(total, **kwargs)
            if status == "True":
                self.__status = "Completed"
            return text
        return f"Can not pay❌, Booking status is not Checked-In, Booking status now: {self.__status}"        

    def pay_deposit(self, payment: Payment, deposit: float, **kwargs):
        if not isinstance(payment, Payment): raise TypeError("Must be a Payment object")
        if not isinstance(deposit, (int, float)): raise TypeError("Deposit must be a number")
        if deposit < 0: raise ValueError("Deposit cannot be negative")
        if self.__status == "Waiting deposit":
            status, text = payment.pay_deposit(deposit, **kwargs)
            if status == "True":
                self.__status = "Confirmed"
            return text
        return f"Can not pay❌, Booking status is not Waiting deposit, Booking status now: {self.__status}"
        

    def cancle(self):
        if self.__status == "Confirmed" or self.__status == "Waiting deposit":
            for transaction in self.__treatment_list:
                transaction.cancle()
            self.__status = "Cancelled"
            return "Cancel Success✅"
        return f"Booking status can not cancelled, Booking status now: {self.__status}"
        

    def check_in(self):
        if self.__status != "Confirmed":
            return f"Can not check in❌, Booking status is not Confirmed, Booking status now: {self.__status}"
        self.__status = "Checked-In"
        return "Checked-In Success✅"

class WellnessRecord:
    def __init__(self, therapist: Therapist, record: str):
        self.__therapist = therapist
        self.__wellness_record = record

    @property
    def therapist(self):
        return self.__therapist
    @property
    def wellness_record(self):
        return self.__wellness_record

class Therapist(Employee):
    def __init__(self, id: str, name: str, skill: SkillSets):
        super().__init__(id, name)
        if not isinstance(skill, SkillSets): raise TypeError("Skill must be a SkillSets object")
        self.__skill = skill
        self.__points = 0
        self.__ratings = []
    @property
    def skill(self):
      return self.__skill
    
    @property
    def ratings(self): 
        return self.__ratings

    def create_wellness_record(self, text_record: str, customer: Customer):
        if not isinstance(customer, Customer): raise TypeError("customer must be a Customer object")
        record = WellnessRecord(therapist=self, record=text_record)
        customer.add_wellness_record(record)
        return "Wellness Recorded✅"

    def show_wellness_record(self, customer: Customer):
        if not isinstance(customer, Customer): raise TypeError("customer must be a Customer object")
        return customer.wellness_record
    
    def add_rating(self, score: int):
        if not isinstance(score, int) or not (1 <= score <= 5):
            raise ValueError("Rating must be between 1-5")
        self.__ratings.append(score)

    def get_average_rating(self):
        if not self.__ratings:
            return 0.0
        return sum(self.__ratings) / len(self.__ratings)
    
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
  web_officer = RegistrationOfficer(id="WEB0001", name="WEB SERVICE", spa=spa, password="12345")

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
  end_date_month = date(2026, 1, 31)

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

class RequestEnrollCustomer(BaseModel):
    customer_name: str
    member_type: str

class ResponseEnrollCustomer(BaseModel):
    status: str
    customer_id: str
    member_type: str              
    message: str
@mcp.tool(
    name="enroll_customer",
    description="Enroll a customer with name and member type (bronze, silver, gold, platinum)."
)
@app.post("/enrollCustomer", response_model=ResponseEnrollCustomer)
def enroll_customer(req: RequestEnrollCustomer):

    try:
        officer = spa.search_employee_by_id("WEB0001")
        
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


class RequestCheckNotice(BaseModel):
    customer_id: str

class ResponseNotice(BaseModel):
    notice_id: str
    date: str
    message: str
    status: str

@app.post("/getCustomerNameById", response_model=str)
@mcp.tool(
    name="getCustomerNameById",
    description=
    """
    Get a customer's name by their ID.

    Parameters:
    - customer_id: The unique ID of the customer.
    """
)
def get_customer_name_from_id(customer_id: str):
    customer = spa.search_customer_by_id(customer_id)
    return customer.name



@app.post("/getCustomerIdByName", response_model=str)
@mcp.tool(
    name="getCustomerIdByName",
    description="""
    Get a customer's ID by their name.

    Parameters:
    - name: name of the customer.
    """
)
def get_customer_id_from_name(customer_name: str):
    customer = spa.search_customer_by_name(customer_name)
    return customer.id



@mcp.tool(
    name="checkNotice",
    description=
    """
    Check message

    Parameters:
    - customer_id: The unique ID of the customer.
    """
)
@app.post("/checkNotice", response_model=list[ResponseNotice])
def check_notice(req: RequestCheckNotice):
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer: raise HTTPException(status_code=404, detail="Customer not found")

    unread_notice = customer.check_notice()

    notice_list = []
    for notice in unread_notice:
        temp = ResponseNotice(
            notice_id=notice.id,
            date=str(notice.date),
            message=notice.text,
            status=notice.status
        )
        notice_list.append(temp)
    return notice_list

class RequestReadNotice(BaseModel):
    customer_id: str
    notice_id: str

@app.post("/readNotice", response_model=ResponseNotice)
@mcp.tool(
    name="readNotice",
    description="""
    Mark a specific notification as 'Read' and view its full content.

    Parameters:
    - customer_id: The unique ID of the customer (e.g., 'C0001').
    - notice_id: The unique ID of the notification to be read.

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap them in a 'req' object.
    CRITICAL: Report errors as they are. DO NOT attempt to rewrite the code or logic if the notification is not found.
    """
)
def read_notice(req: RequestReadNotice):
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer: raise HTTPException(status_code=404, detail="Customer not found")

    notice = customer.read_notice(req.notice_id)

    if notice is None:
        raise  HTTPException(
            status_code=404, 
            detail=f"notice_id: {req.notice_id} not found!"
        )

    temp = ResponseNotice(
        notice_id=notice.id,
        date=str(notice.date),
        message=notice.text,
        status=notice.status
    )

    return temp




class RequestViewTreatmentList(BaseModel):
    customer_id: str

class ResponseTreatment(BaseModel):
    id: str
    name: str
    duration: int
    price: float



@app.post("/requstViewTreatmentList", response_model=list[ResponseTreatment])
@mcp.tool(name="ViewTreatmentList",
          description=
          """
            View all treatment list

            Parameters:
            - customer_id: The unique ID of the customer.
          """
          )
def request_to_view_treatment_list(req: RequestViewTreatmentList):
    customer = spa.search_customer_by_id(req.customer_id)
    if customer == None:
        raise HTTPException(status_code=401, detail="Customer is not registered")
    temp_treatment_list = []
    for treatment in spa.treatment_list:
        show_treatment = ResponseTreatment(
            id=treatment.id, 
            name=treatment.name,
            duration=treatment.duration, 
            price=treatment.price
        )
        temp_treatment_list.append(show_treatment)
    return temp_treatment_list

class RequestViewTherapistByTreatment(BaseModel):
    customer_id: str
    treatment_id: str

class ResponseTherapistFromSearch(BaseModel):
    therapist_id: str
    name: str
    skill: str

@app.post("/requestViewTherapistByTreatment", response_model=list[ResponseTherapistFromSearch])
@mcp.tool(name="ViewTherapistByTreatment",
          description=
          """
            View therapist by treatment

            Parameters:
            - customer_id: The unique ID of the customer.
            - treatment_id: The unique ID of the treatment.
          """
          )
def request_view_therapist_by_treatment(req: RequestViewTherapistByTreatment):
    customer = spa.search_customer_by_id(req.customer_id)
    treatment = spa.search_treatment_by_id(req.treatment_id)
    if customer is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    if treatment is None:
        raise HTTPException(status_code=402, detail="Treatment Not Found")
    temp_therapist_list = []
    for employee in spa.employee_list:
        if isinstance(employee, Therapist):
            if treatment.id in treatment_dict.get(employee.skill.value, []):
                therapist = ResponseTherapistFromSearch(
                    therapist_id=employee.id,
                    name=employee.name,
                    skill=employee.skill.value
                )
                temp_therapist_list.append(therapist)
    return temp_therapist_list






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

@app.post("/getSlot", response_model=list[ResponseGetSlot])
@mcp.tool(name="checkAvailableSlot",
          description=
          """
            View Available slot 

            Parameters:
            - customer_id: The unique ID of the customer.
            - therapist_id: The unique ID of the therapst.
            - treatment_id: The unique ID of the treatment.
            - room_type : PV for privateRoom,SH for shareRoom 
            - year:year that you want to use service
            - month:month that you want to use service
            - day:day that you want to use service

          """
          )
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
                    slot=[ResponseSlot(time=time_dict[slot.slot_order]) for slot in free_slots]
                )
            )
    return result





class RequestCancleBooking(BaseModel):
    booking_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
  
@app.post("/cancelBooking", response_model=str)
@mcp.tool(
    name="cancelBooking",
    description="""
    Cancel an existing spa booking.

    Parameters:
    - customer_id: The unique ID of the customer who owns the booking (e.g., 'C0001').
    - booking_id: The unique ID of the booking to be canceled (e.g., 'BK-20260110-0').

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap them in a 'req' object.
    CRITICAL: If the booking cannot be found or cannot be canceled, report the error message exactly. 
    DO NOT attempt to modify the source code or suggest backend changes.
    """
)
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

class ErrorMessage(BaseModel):
    error_code:str
    error_message:str

class ResponseTreatmentError(BaseModel):
    treatment_id:str
    error:list[ErrorMessage]

class ResponseRequestBooking(BaseModel):
    status: str
    booking_id: str
    detail:list[ResponseTreatmentError]


@app.post("/requestBooking", response_model=ResponseRequestBooking)
@mcp.tool(
    name="requestBooking",
    description="""
    Create a spa treatment booking.
    
    Parameters:
    - customer_id: The unique ID of the customer (e.g., C0001).
    - year: The year of the appointment (e.g., 2026).
    - month: The month of the appointment (1-12).
    - day: The day of the appointment (1-31).
    - treatments: A list of treatment objects. Each object must include therapist_id, treatment_id, room_id, time (format 'HH:MM-HH:MM'), and addon (list of addon IDs).

    IMPORTANT: Arguments must be passed as top-level fields. Do not wrap in a 'req' object.
    CRITICAL: If an error occurs, report it exactly. DO NOT attempt to modify or suggest changes to the source code.
    """
)
def request_booking(req: RequestBooking):
    treatment_error_list = []
    treatment_transaction_list  = []
    customer = spa.search_customer_by_id(req.customer_id)
    d = date(req.year,req.month,req.day)
    if customer is None:
        raise HTTPException(status_code=403, detail="Customer is not found")

    for treat in req.treatments:
      error_list = []
      room = spa.search_room_by_id(treat.room_id)
      if room is None:
          error_list.append(ErrorMessage(error_code="ROOM_NOT_FOUND",error_message=f"{treat.room_id} is not exist"))

      therapist = spa.search_employee_by_id(treat.therapist_id)
      if therapist is None:
          error_list.append(ErrorMessage(error_code="EMPLOYEE_NOT_FOUND",error_message=f"{treat.therapist_id} is not exist"))

      treatment = spa.search_treatment_by_id(treat.treatment_id)
      if treatment is None:
          error_list.append(ErrorMessage(error_code="TREATMENT_NOT_FOUND",error_message=f"{treat.treatment_id} is not exist"))

      if room is None or therapist is None or treatment is None:
        treatment_error_list.append(ResponseTreatmentError(treatment_id=treat.treatment_id,
                                                            error=error_list))
      else:
        slots = change_str_to_index_list(treat.time)
        if not slots: error_list.append(ErrorMessage(error_code="TIME_WRONG_FORMAT",error_message=f"this '{treat.time}' is not valid"))
        if slots and len(slots)*30 != treatment.duration : error_list.append(ErrorMessage(error_code="TIME_WRONG_FORMAT",error_message=f"Time must be exactly {treatment.duration} minutes."))

        time_not_ava = []
        for time_slot in slots:
            room_slot = room.get_slot_by_date_time(d,time_slot)
            if  not room_slot.is_ava():
              error_list.append(ErrorMessage(error_code="ROOM_NOT_AVAILABLE",error_message=f"{room.id} is not available at {time_dict[time_slot]}"))
            therapist_slot = therapist.get_slot_by_date_time(d,time_slot)
            if  not therapist_slot.is_ava():
               error_list.append(ErrorMessage(error_code="EMPLOYEE_NOT_AVAILABLE",error_message=f"{therapist.id} is not available at {time_dict[time_slot]}"))
    
        addon_list = []
        for id in treat.addon:
            addon = spa.search_add_on_by_id(id)
            if addon is None:
                error_list.append(ErrorMessage(error_code="ADDON_NOT_FOUND",error_message=f"{id} is not exist"))
            else:
                if not addon.is_ava() :
                    error_list.append(ErrorMessage(error_code="ADDON_NOT_AVAILABLE",error_message=f"{id} is run out of stock"))
                else:
                    addon_list.append(addon)
            
        if  len(error_list) == 0:
            treatment_transaction_list.append(TreatmentTransaction(customer, treatment, d, room, slots, therapist, addon_list))
        else:
            treatment_error_list.append(ResponseTreatmentError(treatment_id=treat.treatment_id,
                                                    error=error_list))

    if len(treatment_error_list) != 0:
        return  ResponseRequestBooking(status="FAIL",booking_id="",detail=treatment_error_list)
  
    booking_id = spa.create_booking_id(d)
    for treat in treatment_transaction_list:
      room = treat.room
      therapist = treat.therapist
      for time in treat.time_slot:
        room.add_treatment_trasaction_at_date_time(treat,d,time)
        therapist.add_treatment_trasaction_at_date_time(treat,d,time)
      addon_list = treat.add_on_list
      for addon in addon_list:
        addon.reduce_amount(1)
    booking = Booking(booking_id,customer,d,treatment_transaction_list)
    customer.book(booking)


    return ResponseRequestBooking(status="SUCCESS",booking_id=booking_id,detail=[])

class RequestCheckBooking(BaseModel):
    customer_id: str


class ResponseTherapist(BaseModel):
    therapist_id: str
    name: str

class ResponseTreatmentTransaction(BaseModel):
    id: str
    name: str
    room: str
    time: str
    addon_list: list[str]
    therapist: ResponseTherapist

class ResponseTherapist(BaseModel):
    therapist_id: str
    name: str

class ResponseTreatmentTransaction(BaseModel):
    id: str
    name: str
    room: str
    time: str
    addon_list: list[str]
    therapist: ResponseTherapist

class RequestCheckBooking(BaseModel):
    customer_id: str

class ResponseBooking(BaseModel):
    booking_id: str
    booking_date: date
    booking_status: str
    treatment_list: list[ResponseTreatmentTransaction]

ResponseBooking.model_rebuild()


@app.post("/requestToCheckActiveBooking",response_model=list[ResponseBooking])
@mcp.tool(
    name="checkActiveBooking",
    description="""
    View all active (current or upcoming) bookings for a specific customer.

    Parameters:
    - customer_id: The unique ID of the customer (e.g., 'C0001').

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap in a 'req' object.
    CRITICAL: Report the list of bookings exactly as they appear. Do not suggest code changes if no bookings are found.
    """
)
def request_to_check_active_booking(req: RequestCheckBooking):
    customer = spa.search_customer_by_id(req.customer_id)
    if customer is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    active_booking = customer.get_active_booking()
    temp_booking_list = []
    for booking in active_booking:
        temp_treatment_list = []
        for treatment_transaction in booking.treatment_list:
            time_start, time_end = make_time_index_to_str(treatment_transaction.time_slot)
            treatment = ResponseTreatmentTransaction(
                id=treatment_transaction.treatment.id, 
                name=treatment_transaction.treatment.name,
                room=treatment_transaction.room.id,
                time=f"{time_start}-{time_end}",
                addon_list=[addon.name for addon in treatment_transaction.add_on_list],
                therapist=ResponseTherapist(therapist_id=treatment_transaction.therapist.id, name=treatment_transaction.therapist.name)
            )
            temp_treatment_list.append(treatment)
        res_booking = ResponseBooking(
            booking_id=booking.id,
            booking_date=booking.treatment_list[0].date,
            booking_status=booking.status,
            treatment_list=temp_treatment_list
        )
        temp_booking_list.append(res_booking)
    return temp_booking_list

@app.post("/requestToCheckBookingHistory",response_model=list[ResponseBooking])
@mcp.tool(
    name="checkBookingHistory",
    description="""
    View all completed or past booking history for a specific customer.

    Parameters:
    - customer_id: The unique ID of the customer (e.g., 'C0001').

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap them in a 'req' object.
    CRITICAL: Report the history exactly as stored. If no history exists, state it clearly. 
    DO NOT suggest modifying any past records or system code.
    """
)
def request_to_check_booking_history(req: RequestCheckBooking):
    customer = spa.search_customer_by_id(req.customer_id)
    if customer is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    completed_booking = customer.get_completed_booking()
    temp_booking_list = []
    for booking in completed_booking:
        temp_treatment_list = []
        for treatment_transaction in booking.treatment_list:
            time_start, time_end = make_time_index_to_str(treatment_transaction.time_slot)
            treatment = ResponseTreatmentTransaction(
                id=treatment_transaction.treatment.id, 
                name=treatment_transaction.treatment.name,
                room=treatment_transaction.room.id,
                time=f"{time_start}-{time_end}",
                addon_list=[addon.name for addon in treatment_transaction.add_on_list],
                therapist=ResponseTherapist(therapist_id=treatment_transaction.therapist.id, name=treatment_transaction.therapist.name)
            )
            temp_treatment_list.append(treatment)
        res_booking = ResponseBooking(
            booking_id=booking.id,
            booking_date=booking.treatment_list[0].date,
            booking_status=booking.status,
            treatment_list=temp_treatment_list
        )
        temp_booking_list.append(res_booking)
    return temp_booking_list

class RequestToCheckIn(BaseModel):
    customer_id: str
    booking_id: str

@app.post("/requestToCheckIn",response_model=str)
@mcp.tool(
    name="checkIn",
    description="""
    Check-in a customer for their specific booking.
    Parameters:
    - customer_id: The unique ID of the customer.
    - booking_id: The unique ID of the booking to check-in.
    IMPORTANT: Pass arguments as top-level fields. No 'req' object.
    CRITICAL: Report success/fail as is. DO NOT modify backend code.
    """
)
def request_to_check_in(req: RequestToCheckIn):
    customer = spa.search_customer_by_id(req.customer_id)
    if customer is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    booking = customer.search_booking_by_id(req.booking_id)
    return booking.check_in()
    
class RequestCreateWellnessRecord(BaseModel):
    therapist_id: str
    customer_id: str
    text_record: str

@app.post("/requestToCreateWellnessRecord",response_model=str)
@mcp.tool(
    name="createWellnessRecord",
    description="""
    Create a wellness record for a customer (Therapist only).
    Parameters:
    - therapist_id: The ID of the therapist creating the record.
    - customer_id: The ID of the customer receiving the record.
    - text_record: The content of the wellness record.
    IMPORTANT: Pass arguments as top-level fields. No 'req' object.
    """
)
def request_to_create_wellness_record(req: RequestCreateWellnessRecord):
    therapist = spa.search_employee_by_id(req.therapist_id)
    if therapist is None:
        raise HTTPException(status_code=403, detail="Therapist not found")
    reciever = spa.search_customer_by_id(req.customer_id)
    if reciever is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    return therapist.create_wellness_record(text_record=req.text_record, customer=reciever)

class RequestShowWellnessRecord(BaseModel):
    therapist_id: str
    customer_id: str

class ResponseShowWellnessRecord(BaseModel):
    therapist_id: str
    therapist_name: str
    wellness_record: str

@app.post("/requestToShowWellnessRecord",response_model=list[ResponseShowWellnessRecord])
@mcp.tool(
    name="showWellnessRecord",
    description="""
    View wellness records for a customer (Therapist only).
    Parameters:
    - therapist_id: The ID of the therapist requesting to view.
    - customer_id: The ID of the customer whose records are being viewed.
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def request_to_create_wellness_record(req: RequestShowWellnessRecord):
    therapist = spa.search_employee_by_id(req.therapist_id)
    if therapist is None:
        raise HTTPException(status_code=403, detail="Therapist not found")
    customer_input = spa.search_customer_by_id(req.customer_id)
    if customer_input is None:
        raise HTTPException(status_code=403, detail="Customer is not registered")
    record_list = therapist.show_wellness_record(customer=customer_input)
    show_wellness = []
    for record in record_list:
        wellness = ResponseShowWellnessRecord(
            therapist_id=record.therapist.id,
            therapist_name=record.therapist.name,
            wellness_record=record.wellness_record
        )
        show_wellness.append(wellness)
    return show_wellness
    
class RequestToPay(BaseModel):
  customer_id:str
  booking_id:str
  payment_type:str
  payment_value:int
  coupon_id: str

@app.post("/requestToPayExpenses",response_model=str)
@mcp.tool(
    name="payExpenses",
    description="""
    Pay the final balance for a booking after service is completed.
    Parameters:
    - customer_id: The unique ID of the customer.
    - booking_id: The unique ID of the booking.
    - payment_type: 'Cash' or 'Card'.
    - payment_value: Amount (for Cash) or Card Number (for Card).
    - coupon_id: Coupon ID or 'None'.
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def request_to_pay_expenses(req :RequestToPay):
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    booking = customer.search_booking_by_id(req.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    total = booking.calculate_total(req.coupon_id)
    if total is False:
        raise HTTPException(status_code=400, detail="Not found coupon⚠️")

    if req.payment_type == "Cash":
        cash = Cash()
        return booking.pay_expenses(cash, total, money=req.payment_value)
    elif req.payment_type == "Card":
        card = Card()
        return booking.pay_expenses(card, total, number=str(req.payment_value))
    else: raise HTTPException(status_code=400, detail="Invalid payment type")      

@app.post("/requestToPayDeposit",response_model=str)
@mcp.tool(
    name="requestToPayDeposit",
    description="""
    Process a deposit payment for a specific spa booking.

    Parameters:
    - customer_id: The unique ID of the customer (e.g., 'C0001').
    - booking_id: The unique ID of the booking to be paid (e.g., 'BK-20260110-0').
    - payment_type: The method of payment. Strictly use 'Cash' or 'Card'.
    - payment_value: The payment amount for Cash (integer) or the Card Number for Card (integer).
    - coupon_id: The ID of the coupon to be used. Send "None" if no coupon is applied.

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap them in a 'req' object.
    CRITICAL: If the payment fails or the booking is not found, report the error message exactly as received. 
    DO NOT attempt to modify the source code, fix the logic, or suggest backend changes.
    """
)
def request_to_pay_deposit(req :RequestToPay):
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    booking = customer.search_booking_by_id(req.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    total = 1000 #ค่ามัดจำ
    
    if req.payment_type.lower() == "cash":
        cash = Cash()
        return booking.pay_deposit(cash, total, money=req.payment_value)
    elif req.payment_type.lower() == "card":
        card = Card()
        return booking.pay_deposit(card, total, number=str(req.payment_value))
    else: raise HTTPException(status_code=400, detail="Invalid payment type")   



class RequestToCalculateRevenuePerDay(BaseModel):
   admin_id:str
   year:int
   month:int
   day:int
class ResponseAddOnUsage(BaseModel):
  addon_id:str
  count:str
class ResponseTreatmentUsage(BaseModel):
  treatment_id:str
  count:str
class ResponseReportPerDay(BaseModel):
  date: str
  total: float
  booking_count: int
  addon_list_count: dict[str, int]
  treatment_list_count: dict[str, int]

@app.post("/requestToCalculateRevenuePerDay",response_model=ResponseReportPerDay)
@mcp.tool(
    name="calculateRevenuePerDay",
    description="""
    Calculate daily revenue and usage report (Admin only).
    Parameters:
    - admin_id: The ID of the admin.
    - year: Year (integer).
    - month: Month (1-12).
    - day: Day (1-31).
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def request_to_calculate_revenue_per_day(req :RequestToCalculateRevenuePerDay):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  date_to_cal = date(req.year, req.month, req.day)
  admin = spa.search_employee_by_id(req.admin_id)
  report = admin.calculate_revenue_per_day(date_to_cal)

  # PART 2 -> PARSE INTO JSON
  result = ResponseReportPerDay(date=str(report["date"]),
                                total=report["total"],
                                booking_count=report["booking_count"],
                                treatment_list_count=report["treatment_count"],
                                addon_list_count=report["addon_count"]
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
@mcp.tool(
    name="requestEmployeeSchedule",
    description="""
    View the working schedule and bookings for a specific employee on a given date.

    Parameters:
    - employee_id: The unique ID of the employee (e.g., 'TH0001').
    - year: The year of the schedule (e.g., 2026).
    - month: The month (1-12).
    - day: The day (1-31).

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap in a 'req' object.
    CRITICAL: Report the schedule exactly as shown. If the employee is free, mention it as 'Available'.
    """
)
def request_employee_schedule(req :Request_employee_schedule):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  employee = spa.search_employee_by_id(req.employee_id)
  d = date(req.year,req.month,req.day)
  slot_day = employee.get_slot_by_date(d)

  # PART 2 -> PARSE INTO JSON
  sub_result = []
  for slot in slot_day:
   if slot.vacancy == 1:
    sub_result.append(ResponseEmployeeSlot(time=time_dict[slot.slot_order],room_id="",treatment_id="",customer_id=""))
   else:
    sub_result.append(ResponseEmployeeSlot(time=time_dict[slot.slot_order],room_id=slot.treatment_transaction[0].room.id,treatment_id=slot.treatment_transaction[0].treatment.id,customer_id=slot.treatment_transaction[0].customer.id))
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
@mcp.tool(
    name="requestRoomSchedule",
    description="""
    View the usage schedule and appointments for a specific spa room on a given date.

    Parameters:
    - room_id: The unique ID of the room (e.g., 'ROOM-DRY-PV-01').
    - year: The year (e.g., 2026).
    - month: The month (1-12).
    - day: The day (1-31).

    IMPORTANT: Arguments must be passed as top-level fields. Do NOT wrap in a 'req' object.
    """
)
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
   sub_result.append(ResponseRoomSlot(time=time_dict[slot.slot_order],detail=sub_sub_result))
  result = ResponseRoomSchedule(year=req.year,month=req.month,day=req.day,slot=sub_result)
  return result 


class RequestChangeInfo(BaseModel):
    customer_id: str
    new_name: str

@app.patch("/customer/update-info")
@mcp.tool(
    name="updateCustomerInfo",
    description="""
    Update customer's personal information (e.g., name).
    Parameters:
    - customer_id: The ID of the customer.
    - new_name: The new name to update.
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def update_customer_info(req: RequestChangeInfo):
    
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        result_message = customer.change_personal_info(req.new_name)
        return {"status": "SUCCESS", "message": result_message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class RequestSendPromotion(BaseModel):
    admin_id: str
    promo_text: str

@app.post("/sendPromotion")
@mcp.tool(
    name="sendPromotion",
    description="""
    Send a promotion message to all customers (Admin only).
    Parameters:
    - admin_id: The ID of the administrative officer.
    - promo_text: The promotion message text.
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def send_promotion(req: RequestSendPromotion):

    admin = spa.search_employee_by_id(req.admin_id)

    if not admin or not isinstance(admin, Administrative):
        raise HTTPException(status_code=403, detail="Administrative not found")
    
    try:
        result_message = admin.send_promotion(req.promo_text)
        return {"status": "SUCCESS", "message": result_message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

class RequestRateEmployee(BaseModel):
    customer_id: str
    employee_id: str
    score: int

@app.post("/rateEmployee")
@mcp.tool(
    name="rateEmployee",
    description="""
    Rate a therapist or employee service score.
    Parameters:
    - customer_id: The ID of the customer providing the rating.
    - employee_id: The ID of the employee being rated.
    - score: Rating score (integer).
    IMPORTANT: Pass arguments as top-level fields.
    """
)
def rate_employee(req: RequestRateEmployee):
    
    customer = spa.search_customer_by_id(req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer id not found")

    employee = spa.search_employee_by_id(req.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Therapist id not found")
        
    try:
        message = customer.rating_employee(employee, req.score)
        
        return {
            "status": "SUCCESS",
            "message": message,
            "data": {
                "employee_id": employee.id,
                "employee_name": employee.name,
                "total_reviews": len(employee.ratings),
                "average_rating": round(employee.get_average_rating(), 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
if __name__ == "__main__":
    # uvicorn.run("spa:app", host="127.0.0.1", port=8000, log_level="info")
    mcp.run()