from datetime import date, datetime, timedelta
from fastapi import FastAPI
import uvicorn
from typing import Union
from pydantic import BaseModel

from fastmcp import FastMCP
from abc import ABC, abstractmethod

mcp = FastMCP("Demo")
app = FastAPI()

# <==BOAT==>
class Spa:
  def __init__(self, name):
    self.__name = name
    self.__customer_list = []
    self.__employee_list = []
    self.__room_list = []
    self.__transaction_list = []
    self.__treatment_list = []
    self.__resource_list = []
    self.__add_on_list = []
    self.__revenue_per_day_list = []

  @property
  def employee_list(self):
    return self.__employee_list

  @property
  def treatment_list(self):
    return self.__treatment_list

  @property
  def add_on_list(self):
    return self.__add_on_list

  @property
  def customer_list(self):
    return self.__customer_list

  @property
  def revenue_per_day_list(self):
    return self.__revenue_per_day_list

  def search_customer_by_id(self, id):
    for customer in self.__customer_list:
      if customer.id == id:
        return customer

  def search_employee_by_id(self, id):
    for employee in self.__employee_list:
      if employee.id == id:
        return employee

  def search_treatment_by_id(self, id):
    for treatment in self.__treatment_list:
      if treatment.id == id:
        return treatment

  def search_add_on_by_id(self, id):
    for add_on in self.__add_on_list:
      if add_on.id == id:
        return add_on

  def search_room_by_id(self, id):
    for room in self.__room_list:
      if room.id == id:
        return room

  def get_room_by_room_type(self, type):
    result_list = []
    for room in self.__room_list:
      if room.id.startswith(type):
        result_list.append(room)
    return result_list


  def verify_admin(self, employee_id, input_password):
    employee = self.search_employee_by_id(employee_id)
    password = employee.password
    if password == input_password:
      employee.login = True

  def add_employee(self, employee):
    self.__employee_list.append(employee)

  def add_treatment(self, treatment):
    self.__treatment_list.append(treatment)

  def add_customer(self, customer):
    self.__customer_list.append(customer)

  def add_room(self, room):
    self.__room_list.append(room)

  def add_add_on_list(self, add_on):
    self.__add_on_list.append(add_on)



  def find_intersect_free_slot(self, room_slot, therapist_slot):
    list_of_intersect_free_slot = []
    for i in range(0, 16):
        if room_slot[i].vacancy > 0 and therapist_slot[i].vacancy > 0:
            list_of_intersect_free_slot.append(room_slot[i])
    return list_of_intersect_free_slot
        
class Employee:
  def __init__(self, id, name):
      self.__id = id
      self.__slot = []
      self.__name = name

  @property
  def id(self):
    return self.__id

  @property
  def slot(self):
    return self.__slot

  @property
  def name(self):
    return self.__name 

  def get_slot_by_date(self,date):
    slot_in_date = []
    for slot in self.__slot:
        if slot.date == date:
            slot_in_date.append(slot)
    return slot_in_date

  def get_slot_by_date_time(self,date,time):
    slot_in_date = self.get_slot_by_date(date)
    for slot in slot_in_date:
        if slot.slot_order == time:
           return slot

  def add_slot_by_time(self,slot_list,time):
      for slot_ in slot_list:
            if slot_.slot_order == time:
                slot_.vacancy += 1

class Admin(Employee):
  def __init__(self, id, name, spa, password):
    super().__init__(id, name)
    self.__spa = spa
    self.__password = password
    self.__login = False

  @property
  def password(self):
    return self.__password

  @property
  def login(self):
    return self.__login

  @property
  def spa(self):
    return self.__spa

  @login.setter
  def login(self, value):
    self.__login = value

  def logout(self):
    self.__login = False

class RegistrationOfficer(Admin):
  def __init__(self, id, name, spa, password):
    super().__init__(id, name, spa, password)

  def add_slot(self, end_date_month, entity, vacancy):
    year = end_date_month.year
    month = end_date_month.month
    end_date = end_date_month.day
    if self.login:
      for i in range(1, end_date + 1):
        for n in range(1, 17):
            slot = Slot(date(year, month, i), n, vacancy)
            entity.slot.append(slot)
  
  def add_customer(self, customer):
    if self.login:
        self.spa.add_customer(customer)
        notice_id = f"ENROLL_RESULT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        customer.add_notice_list(Message(notice_id, customer, "Enroll success✅", datetime.now()))
  
  def add_employee(self, employee):
    if isinstance(employee, RegistrationOfficer) or isinstance(employee, Administrative) or self.login:
      self.spa.add_employee(employee)

  def add_room(self, room):
    if self.login:
      self.spa.add_room(room)

  def add_resource(self, room_id, resource):
    if self.login:
      room = self.spa.search_room_by_id(room_id)
      room.resource_list.append(resource)

  def add_add_on(self, add_on):
    if self.login:
      self.spa.add_add_on_list(add_on)

  def add_treatment(self, treatment):
    if self.login:
      self.spa.add_treatment(treatment)

class Message:
  def __init__(self, id, receiver, text, date):
    self.__id = id
    self.__receiver = receiver
    self.__text = text
    self.__date = date
    self.__status = "UNREAD"

  @property
  def text(self):
    return self.__text

class Customer:
  def __init__(self, id, name):
    self.__id = id
    self.__name = name
    self.__booking_list = []
    self.__notice_list = []
    self.__wellness_record = []
    self.__coupons = []
    self.__missed_count = 0

  @property
  def id(self):
    return self.__id
    
  @property
  def name(self):
    return self.__name

  @property
  def booking_list(self):
    return self.__booking_list

  @property
  def missed_count(self):
    return self.__missed_count

  @property
  def notice_list(self):
    return self.__notice_list

  def add_notice_list(self, message):
    self.__notice_list.append(message)

  def search_booking_by_id(self, id):
    for booking in self.__booking_list:
      if booking.id == id:
        return booking

  def book(self, id, customer_id, date):
    booking = Booking(id, self, date)
    self.__booking_list.append(booking)
  
  def add_treatment_transaction(self,booking_id,treatment_transaction):
    booking = self.search_booking_by_id(booking_id)
    booking.treatment_list.append(treatment_transaction)


  

  


class Bronze(Customer):
  def __init__(self, id, name):
    super().__init__(id, name)
    self.__discount = 0
    self.__booking_quota = 1
    self.__fee = 0
  @property
  def discount(self):
    return self.__discount

  @property
  def booking_quota(self):
    return self.__booking_quota

class Silver(Customer):
  def __init__(self, id, name):
      super().__init__(id, name)
      self.__discount = 0.05
      self.__booking_quota = 2
      self.__fee = 1000
  @property
  def discount(self):
    return self.__discount
  
  @property
  def booking_quota(self):
    return self.__booking_quota
  
class Gold(Customer):
  def __init__(self, id, name):
      super().__init__(id, name)
      self.__discount = 0.1 
      self.__booking_quota = 3
      self.__fee = 1500
  @property
  def discount(self):
    return self.__discount
  
  @property
  def booking_quota(self):
    return self.__booking_quota

class Platinum(Customer):
  def __init__(self, id, name):
      super().__init__(id, name)
      self.__discount = 0.2
      self.__booking_quota = 5
      self.__fee = 2500

  @property
  def discount(self):
    return self.__discount
  
  @property
  def booking_quota(self):
    return self.__booking_quota

class TreatmentTransaction:
    def __init__(self,customer,treatment, date, room, time_slot, therapist, add_on_list):
      self.__customer = customer
      self.__treatment = treatment
      self.__date = date
      self.__room = room
      self.__time_slot = time_slot
      self.__add_on_list = add_on_list
      self.__therapist = therapist
      self.__status = ""


    @property
    def customer(self):
      return self.__customer

    @property  
    def treatment(self):
      return self.__treatment

    @property  
    def date(self):
      return self.__date

    @property  
    def room(self):
      return self.__room

    @property  
    def time_slot(self):
      return self.__time_slot

    @property  
    def add_on_list(self):
      return self.__add_on_list

    @property
    def therapist(self):
      return self.__therapist

    def cancle(self):
      for time in self.__time_slot:
        room_slot = self.room.get_slot_by_date_time(self.__date,time)
        therapist_slot = self.therapist.get_slot_by_date_time(self.__date,time)
        room_slot.remove_treatment_transaction(self)
        therapist_slot.remove_treatment_transaction(self)
      self.__status = "CANCLE"
      return self.__status == "CANCLE"

class Treatment:
    def __init__(self, id, name, price, duration, room_type):
      self.__name = name
      self.__id = id
      self.__price = price
      self.__duration = duration
      self.__room_type = room_type

    @property
    def id(self):
      return self.__id

    @property
    def price(self):
      return self.__price

    @property
    def room_type(self):
      return self.__room_type

    @property
    def name(self):
      return self.__name

class AddOn:
  def __init__(self, id, name, price):
    self.__id = id
    self.__name = name
    self.__price = price

  @property
  def id(self):
    return self.__id

  @property
  def price(self):
    return self.__price

# <==IAOON==>
class Room:
  def __init__(self, id):
    self.__id = id
    self.__slot = []
    self.__resource_list = []

  @property
  def id(self):
    return self.__id
  
  @property
  def slot(self):
    return self.__slot

  @property
  def resource_list(self):
    return self.__resource_list

  @resource_list.setter
  def resource_list(self, value):
    self.__resource_list.append(value)


  def get_slot_by_date(self,date):
    slot_in_date = []
    for slot in self.__slot:
        if slot.date == date:
            slot_in_date.append(slot)
    return slot_in_date

  def get_slot_by_date_time(self,date,time):
    slot_in_date = self.get_slot_by_date(date)
    for slot in slot_in_date:
        if slot.slot_order == time:
           return slot



  def add_slot_by_time(self,slot_list,time):
      for slot_ in slot_list:
            if slot_.slot_order == time:
                slot_.vacancy = 1




class DryPrivateRoom(Room):
  def __init__(self, id, price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class DrySharedRoom(Room):
  def __init__(self, id, price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class WetPrivateRoom(Room):
  def __init__(self, id, price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class WetSharedRoom(Room):
  def __init__(self, id, price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class Slot:
  def __init__(self, date, slot_order, vacancy):
      self.__date = date
      self.__slot_order = slot_order
      self.__vacancy = vacancy
      self.__treatment_transaction = []

  @property
  def date(self):
      return self.__date

  @property
  def slot_order(self):
      return self.__slot_order

  @property
  def vacancy(self):
      return self.__vacancy

  @vacancy.setter
  def vacancy(self, value):
      self.__vacancy = value

  @property
  def treatment_transaction(self):
    return self.__treatment_transaction

  def add_treatment_transaction(self,transaction):
    self.__treatment_transaction.append(transaction)
    self.__vacancy -= 1

  def remove_treatment_transaction(self,transaction):
    self.__treatment_transaction.remove(transaction)
    self.__vacancy += 1
  
  



class Administrative(Admin):
  def __init__(self, id, name, spa, password):
      super().__init__(id, name, spa, password)

  def create_resource_count_class(self):
    treatment_list = []
    addon_list = []
    for treatment in self.spa.treatment_list:
      treatment_list.append(ResourceCount(treatment))
    for addon in self.spa.add_on_list:
      addon_list.append(ResourceCount(addon))
    return addon_list, treatment_list

  def calculate_revenue_per_day(self, date):
    booking_count = 0
    total_sum = 0
    addon_count, treatment_count = self.create_resource_count_class()
    customer_list = self.spa.customer_list
    for customer in customer_list:
      booking_list = customer.booking_list
      for booking in booking_list:
        if booking.treatment_list[0].date == date and booking.status == "Completed":
          booking_count += 1
          total = booking.calculate_total()
          total_sum += total
          for treatment_transaction in booking.treatment_list:
            for resource in treatment_count:
              if resource.resource.id == treatment_transaction.treatment.id:
                resource.count += 1
            for resource in addon_count:
              for addon in treatment_transaction.add_on_list:
                if addon.id == resource.resource.id:
                  resource.count += 1

    report_revenue = RevenuePerDay(date, total_sum, booking_count, addon_count, treatment_count)
    self.spa.revenue_per_day_list.append(report_revenue)
    return report_revenue

class RevenuePerDay:
  def __init__(self, date, total, booking_count, addon_count, treatment_count):
    self.__date = date
    self.__total = total
    self.__booking_count = booking_count
    self.__addon_count = addon_count
    self.__treatment_count = treatment_count

  @property
  def booking_count(self):
    return self.__booking_count

  @booking_count.setter
  def booking_count(self,value):
    self.__booking_count = value

  @property
  def total(self):
    return self.__total

  @total.setter
  def total(self,value):
    self.__total = value
  
  @property
  def date(self):
    return self.__date
  @property
  def addon_count(self):
    return self.__addon_count
  @property
  def treatment_count(self):
    return self.__treatment_count 



class ResourceCount:
  def __init__(self, resource):
    self.__resource = resource
    self.__count = 0

  @property
  def resource(self):
    return self.__resource

  @property
  def count(self):
    return self.__count

  @count.setter
  def count(self,value):
    self.__count = value

class Payment(ABC):
  @abstractmethod
  def pay_deposit(self, deposit, **kwargs):
    pass

  @abstractmethod
  def pay_expenses(self, total, **kwargs):
    pass

class Cash(Payment):
  def pay_deposit(self, deposit, money):
    if money < deposit:
      return f"You have to pay {deposit} ฿ for deposit⚠️"
    else:
      return "Your booking confirmed✅"

  def pay_expenses(self, total, money):
    if money < total:
      return f"Not enough money! You have to pay {total} ฿⚠️"
    else:
      return f"Payment Success✅, Your change = {money - total} ฿"

class Card(Payment):
  def pay_deposit(self, deposit, number):
    return f"Your booking confirmed✅, {deposit} ฿ deducted from your card (Card id : {number})"

  def pay_expenses(self, total, number):
    return f"Payment Success✅, {total} ฿ deducted from your card (Card id : {number})"

# <==TA==>
class Booking:
  def __init__(self, id, customer, date):
    self.__id = id
    self.__customer = customer
    self.__date = date
    self.__treatment_list = []
    self.__status = "Waiting deposit"

  @property
  def id(self):
    return self.__id

  def get_treatment_list(self):
    return self.__treatment_list

  @property
  def treatment_list(self):
    return self.__treatment_list

  @property
  def date(self):
    return self.__date
  
  @property
  def status(self):
    return self.__status

  @status.setter
  def status(self, value):
    self.__status = value

  def calculate_total(self):
    total = 0
    for treatment in self.treatment_list:
      total += treatment.treatment.price
      total += treatment.room.price
      for add_on in treatment.add_on_list:
          total += add_on.price

      discount = total * self.__customer.discount
      total -= discount

    return total

  def pay_expenses(self, payment, total, **kwargs):
    self.__status = "Completed"
    return payment.pay_expenses(total, **kwargs)

  def pay_deposit(self, payment, deposit, **kwargs):
    self.__status = "Confirmed"
    return payment.pay_deposit(deposit, **kwargs)

  def cancle(self):
    for treatment in self.__treatment_list:
      treatment.cancle()
    
    # if self.__treatment_list[0].date - date.today() > timedelta(days=1):
    #   self.__notice_list.append(Message(self.__id, "Refund deposit 50%", datetime.now()))
    # else:
    #   self.__notice_list.append(Message(self.__id, "No refund deposit", datetime.now()))

    self.__status = "CANCEL"

    return "Cancel Success✅"


    

class Therapist(Employee):
  def __init__(self, id, name, skill):
    super().__init__(id, name)
    self.__skill = skill
    self.__points = 0

class Resource:
  def __init__(self, id, name, amount):
    self.__id = id
    self.__name = name
    self.__amount = amount
    self.__status = "Available"
# <==TA==>

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
  t1 = Therapist(id="T0001", name="John", skill="Massage")
  t2 = Therapist(id="T0002", name="Anna", skill="Massage")
  t3 = Therapist(id="T0003", name="Emma", skill="Massage")
  t4 = Therapist(id="T0004", name="Olivia", skill="Massage")
    
  t5 = Therapist(id="T0005", name="Justin", skill="Aroma")
  t6 = Therapist(id="T0006", name="Sophia", skill="Aroma")
  t7 = Therapist(id="T0007", name="Mary", skill="Aroma")
  t8 = Therapist(id="T0008", name="Matha", skill="Aroma")
    
  t9 = Therapist(id="T0009", name="Ben", skill="Pool")
  t10 = Therapist(id="T0010", name="Jane", skill="Pool")
  t11 = Therapist(id="T0011", name="May", skill="Pool")

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
  add_on1 = AddOn(id="OIL-P", name="Premium Essential Oil", price=350)
  add_on2 = AddOn(id="CMP-H", name="Herbal Compress", price=250)
  add_on3 = AddOn(id="SCRB-D", name="Detox Scrub", price=450) 
  add_on4 = AddOn(id="SNK-S", name="After-Service Snack Set", price=150) 

  # Create Operation Officer //
  reg1 = RegistrationOfficer(id="0001", name="Kevin", spa=spa, password="12345")
  ad1 = Administrative(id="0002", name="Paul", spa=spa, password="12345")

  # Add themselves //
  reg1.add_employee(reg1)
  reg1.add_employee(ad1)  

  # Login //
  spa.verify_admin(reg1.id, "12345")
  
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
  reg1.add_employee(t9)
  reg1.add_slot(end_date_month, t9, 1)
  reg1.add_employee(t10)
  reg1.add_slot(end_date_month, t10, 1)

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

class RequestGetSlot(BaseModel):
    customer_id: str
    therapist_id: str
    treatment_id: str
    room_type: str
    year: int
    month: int
    day: int
class ResponseSlot(BaseModel):
    time:str
class ResponseGetSlot(BaseModel):
    room_id: str
    year: int
    month: int
    day: int
    slot: list[ResponseSlot]
time = {
    1: "8:00-8:30",
    2: "8:30-9:00",
    3: "9:00-9:30",
    4: "9:30-10:00",
    5: "10:00-10:30",
    6: "10:30-11:00",
    7: "11:00-11:30",
    8: "11:30-12:00",
    9: "12:00-12:30",
    10: "12:30-13:00",
    11: "13:00-13:30",
    12: "13:30-14:00",
    13: "14:00-14:30",
    14: "14:30-15:00",
    15: "15:00-15:30",
    16: "15:30-16:00",
}
@app.post("/getSlot",response_model=list[ResponseGetSlot])
def find_free_slot(req :RequestGetSlot):
    # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
    date_class = date(req.year, req.month, req.day)
    customer = spa.search_customer_by_id(req.customer_id)
    therapist = spa.search_employee_by_id(req.therapist_id)
    therapist_slot = therapist.get_slot_by_date(date_class)
    treatment = spa.search_treatment_by_id(req.treatment_id)
    room_type_str = f'ROOM-{treatment.room_type}-{req.room_type}'
    room_list = spa.get_room_by_room_type(room_type_str)
    result = []

    for room in room_list:
        room_slot = room.get_slot_by_date(date_class)
        free_slots = spa.find_intersect_free_slot(room_slot, therapist_slot)
        
        # PART 2 -> PARSE INTO JSON
        result.append(
            ResponseGetSlot(
                room_id=room.id,
                year=free_slots[0].date.year,
                month=free_slots[0].date.month,
                day=free_slots[0].date.day,
                slot=[ResponseSlot(
                                      time=time[slot.slot_order],
                                   ) for slot in free_slots]
                            )
                      )
    return result
       


class Request_cancle_booking(BaseModel):
  booking_id:str
  customer_id:str
@app.post("/cancelBooking",response_model=str)
def cancel_booking(req :Request_cancle_booking):
    customer = spa.search_customer_by_id(req.customer_id)
    booking = customer.search_booking_by_id(req.booking_id)
    result = booking.cancle()
    return result




class Request_treatment(BaseModel):
  therapist_id:str
  treatment_id:str
  room_id:str
  time:str
  addon:list[str]
class Request_booking(BaseModel):
  customer_id:str
  year:int
  month:int
  day:int
  treatments:list[Request_treatment]
class Response_request_booking(BaseModel):
  status:str
  booking_id:str
def change_str_to_index_list(str):
    result = []
    found_start_time = False
    start_time,end_time = str.split("-")
    for key,value in time.items():
        start,end = value.split("-")
        if start_time == start:
            result.append(key)
            found_start_time = True
            if end_time == end:
                return result
            continue
        if found_start_time:
            result.append(key)
        if end_time == end:
            return result
@app.post("/requestBooking",response_model=Response_request_booking)
def request_booking(req:Request_booking):
    # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
    date_booking = date(req.year, req.month, req.day)
    customer = spa.search_customer_by_id(req.customer_id)

    if customer.booking_quota <= 0 or customer.missed_count > 2:
      return "CANNOT MAKE BOOKING"

    d = date(2026, 1, 8) 
    booking_id = f'BK-{d.year}{d.month if len(str(d.month)) > 1 else f"0{d.month}"}{d.day if len(str(d.day)) > 1 else f"0{d.day}"}-0001'

    customer.book(booking_id, customer.id, d)

    for treat in req.treatments:
      treatment = spa.search_treatment_by_id(treat.treatment_id)
      room = spa.search_room_by_id(treat.room_id)
      therapist = spa.search_employee_by_id(treat.therapist_id)
      addon_list = [spa.search_add_on_by_id(id) for id in treat.addon]
      slot = change_str_to_index_list(treat.time)
      treatment_transaction = TreatmentTransaction(customer, treatment, date_booking, room,slot, therapist, addon_list)
      customer.add_treatment_transaction(booking_id,treatment_transaction)
      room_slot = room.get_slot_by_date(date_booking)
      therapist_slot = therapist.get_slot_by_date(date_booking)
      for order in slot:
        for slot_ in room_slot:
            if slot_.slot_order == order:
                slot_.add_treatment_transaction(treatment_transaction)
        for slot_ in therapist_slot:
            if slot_.slot_order == order:
                slot_.add_treatment_transaction(treatment_transaction)

    # PART 2 -> PARSE INTO JSON
    return Response_request_booking(status="SUCCESS",booking_id=booking_id)


class Request_to_pay(BaseModel):
  customer_id:str
  booking_id:str
  payment_type:str
  payment_value:int
@app.post("/requestToPay",response_model=str)
def request_to_pay(req :Request_to_pay):
    customer = spa.search_customer_by_id(req.customer_id)
    booking = customer.search_booking_by_id(req.booking_id)
    total = booking.calculate_total()
    
    if req.payment_type == "Cash":
      cash = Cash()
      return booking.pay_expenses(cash, total, money=req.payment_value) 
    elif req.payment_type == "Card":
      card = Card()
      return booking.pay_expenses(card, total, number=req.payment_value)





class Request_to_calculate_revenue_per_day(BaseModel):
   admin_id:str
   year:int
   month:int
   day:int
class Response_addon_usage(BaseModel):
  addon_id:str
  count:int
class Response_treatment_usage(BaseModel):
  treatment_id:str
  count:int
class Response_report_per_day(BaseModel):
  day:int
  year:int
  month:int
  total:float
  addon_list_count:list[Response_addon_usage]
  treatment_list_count:list[Response_treatment_usage]
@app.post("/requestToCalculateRevenuePerDay",response_model=Response_report_per_day)
def request_to_calculate_revenue_per_day(req :Request_to_calculate_revenue_per_day):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  date_to_cal = date(req.year, req.month, req.day)
  admin = spa.search_employee_by_id(req.admin_id)
  report = admin.calculate_revenue_per_day(date_to_cal)

  # PART 2 -> PARSE INTO JSON
  result = Response_report_per_day(day=report.date.day,
                                   month=report.date.month,
                                   year=report.date.year,
                                   total=report.total,
                                   addon_list_count=[Response_addon_usage(addon_id=addon.resource.id,count=addon.count) for addon in report.addon_count],
                                   treatment_list_count=[Response_treatment_usage(treatment_id=addon.resource.id,count=addon.count) for addon in report.treatment_count]
                                   )
  return result



class Response_employee_slot(BaseModel):
  time:str
  room_id:str
  treatment_id:str
  customer_id:str
class Response_employee_schedule(BaseModel):
  year:int
  month:int
  day:int
  slot:list[Response_employee_slot]
class Request_employee_schedule(BaseModel):
  employee_id:str
  year:int
  month:int
  day:int
@app.post("/requestEmployeeSchedule",response_model=Response_employee_schedule)
def request_employee_schedule(req :Request_employee_schedule):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  employee = spa.search_employee_by_id(req.employee_id)
  d = date(req.year,req.month,req.day)
  slot_day = employee.get_slot_by_date(d)

  # PART 2 -> PARSE INTO JSON
  sub_result = []
  for slot in slot_day:
   if slot.vacancy == 1:
    sub_result.append(Response_employee_slot(time=time[slot.slot_order],room_id="",treatment_id="",customer_id=""))
   else:
    sub_result.append(Response_employee_slot(time=time[slot.slot_order],room_id=slot.treatment_transaction[0].room.id,treatment_id=slot.treatment_transaction[0].treatment.id,customer_id=slot.treatment_transaction[0].customer.id))
  result = Response_employee_schedule(year=req.year,month=req.month,day=req.day,slot=sub_result)
  return result 


class Response_room_detail(BaseModel):
  customer_id:str
  treatment_id:str
  employee_id:str
class Response_room_slot(BaseModel):
  time:str
  detail: list[Response_room_detail]
class Response_room_schedule(BaseModel):
  year:int
  month:int
  day:int
  slot:list[Response_room_slot]
class Request_room_schedule(BaseModel):
  room_id:str
  year:int
  month:int
  day:int
@app.post("/requestRoomSchedule",response_model=Response_room_schedule)
def request_room_schedule(req :Request_room_schedule):
  # PART 1 -> GET DATE(WORK ACCORDING TO SEQUENCE)
  room = spa.search_room_by_id(req.room_id)
  d = date(req.year,req.month,req.day)
  slot_day = room.get_slot_by_date(d)
  sub_result = []

  # PART 2 -> PARSE INTO JSON
  for slot in slot_day:
   sub_sub_result = []
   for treatment in slot.treatment_transaction:
       sub_sub_result.append(Response_room_detail(customer_id=treatment.customer.id,treatment_id=treatment.treatment.id,employee_id=treatment.therapist.id))
   sub_result.append(Response_room_slot(time=time[slot.slot_order],detail=sub_sub_result))
  result = Response_room_schedule(year=req.year,month=req.month,day=req.day,slot=sub_result)
  return result 







if __name__ == "__main__":
  uvicorn.run("spa:app", host="127.0.0.1", port=8000, log_level="info")