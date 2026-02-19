from datetime import date, datetime, timedelta
from fastapi import FastAPI
import uvicorn
from typing import Union

from fastmcp import FastMCP

from abc import ABC, abstractmethod

mcp = FastMCP("Demo")
app = FastAPI()

# <==BOAT==>
class Spa():
  def __init__(self,name):
    self.__name = name
    self.__customer_list = []
    self.__employee_list = []
    self.__room_list = []
    self.__transaction_list = []
    self.__treatment_list = []
    self.__resource_list = []
    self.__add_on_list = []

  @property
  def employee_list(self):
    return self.__employee_list

  def search_customer_by_id(self,id):
    for customer in self.__customer_list:
      if customer.id == id:
        return customer

  def search_employee_by_id(self,id):
    for employee in self.__employee_list:
      if employee.id == id:
        return employee

  def search_treatment_by_id(self,id):
    for treatment in self.__treatment_list:
      if treatment.id == id:
        return treatment

  def search_add_on_by_id(self,id):
    for add_on in self.__add_on_list:
      if add_on.id == id:
        return add_on

  def search_room_by_id(self,id):
    for room in self.__room_list:
      if room.id == id:
        return room

  def get_room_by_room_type(self,type):
    result_list = []
    for room in self.__room_list:
      # print(room.id,type)
      if room.id.startswith(type):
        result_list.append(room)
    return result_list

  # def requestToPay(self,admin,customer,booking_id):
  #   return admin.calculate_total(customer,booking_id)

  def get_employee_slot(self,Employee,date):
    slot_all = Employee.slot
    slot_in_date = []
    for slot in slot_all:
        if slot.date == date:
            slot_in_date.append(slot)
    return slot_in_date

  def get_room_slot(self,Room,date):
    slot_all = Room.slot
    slot_in_date = []
    for slot in slot_all:
        if slot.date == date:
            slot_in_date.append(slot)
    return slot_in_date

  def verify_admin(self,employee_id,input_password):
    employee = self.search_employee_by_id(employee_id)
    password = employee.password
    if password == input_password:
      employee.login = True

  def add_employee(self,Employee):
    self.__employee_list.append(Employee)

  def add_treatment(self,Treatment):
    self.__treatment_list.append(Treatment)

  def add_customer(self,Customer):
    self.__customer_list.append(Customer)

  def add_room(self,Room):
    self.__room_list.append(Room)

  def add_add_on_list(self,Add_on):
    self.__add_on_list.append(Add_on)

  def reques_to_cancle_booking(self,booking_id,customer_id):
    customer = self.search_customer_by_id(customer_id)
    booking = customer.search_booking_by_id(booking_id)
    customer.cancle_booking(booking_id)
    for treatment in booking.treatment_list:
      room = self.search_room_by_id(treatment.room.id)
      therapist = self.search_employee_by_id(treatment.therapist_id)
      time_slot_list = treatment.time_slot
      for time in time_slot_list:
        therapist.slot[treatment.date.day].slot_list[time][1] = 1 
        room.slot[treatment.date.day].slot_list[time][1] += 1

  def find_intersect_free_slot(self,room_slot,therapist_slot):
    list_of_intersect_free_slot = []
    for i in range(0,16):
        if room_slot[i].vacancy > 0 and therapist_slot[i].vacancy > 0:
            list_of_intersect_free_slot.append(room_slot[i])
    return list_of_intersect_free_slot
        
class Employee():
  def __init__(self,id,name):
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

class Admin(Employee):
  def __init__(self,id,name,password):
    super().__init__(id,name)
    self.__password = password
    self.__login = False

  @property
  def password(self):
    return self.__password

  @property
  def login(self):
    return self.__login


  @login.setter
  def login(self,value):
    self.__login = value

  def logout(self):
    self.__login = False

class Registration_officer(Admin):
  def __init__(self,id,name,Spa,password):
    super().__init__(id,name,password)
    self.__spa = Spa

#   def add_slot(self,Entity,vacancy):
#     if self.login:
#       for i in range(1,32):
#         slot = Slot(date(2026,1,i),vacancy)
#         Entity.slot.append(slot)

  def add_slot(self,end_date_month,Entity,vacancy):
    year = end_date_month.year
    month = end_date_month.month
    end_date = end_date_month.day
    if self.login:
      for i in range(1,end_date + 1):
        for n in range(1,17):
            slot = Slot(date(year,month,i),n,vacancy)
            Entity.slot.append(slot)
  
  def add_customer(self,Customer):
    if self.login:
        self.__spa.add_customer(Customer)
        Customer.add_notice_list(Message(Customer.id,"OTP-005",datetime.now()))
  
  def add_employee(self,Employee):
    if isinstance(Employee,Registration_officer) or isinstance(Employee,Administrative) or self.login:
      self.__spa.add_employee(Employee)

  def add_room(self,Room):
    if self.login:
      self.__spa.add_room(Room)

  def add_resource(self,room_id,Resource):
    if self.login:
      room = self.__spa.search_room_by_id(room_id)
      room.resource_list.append(Resource)

  def add_add_on(self,Add_on):
    if self.login:
      self.__spa.add_add_on_list(Add_on)

  def add_treatment(self,Treatment):
    if self.login:
      self.__spa.add_treatment(Treatment)

class Message():
  def __init__(self,reciever,text,date):
    self.__reciever = reciever
    self.__text= text
    self.__date = date
    self.__status = "UNREAD"

class Customer():
  def __init__(self,id,name):
    self.__id = id
    self.__name = name
    self.__booking_list = []
    self.__free_slot_from_find_intersect_free_slot = []
    self.__notice_list = []
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

  def add_notice_list(self,Message):
    self.__notice_list.append(Message)

  def search_booking_by_id(self,id):
    for  booking in self.__booking_list:
      if booking.id == id:
        return booking

  def book(self,id,customer_id,date):
    booking = Booking(id,self,date)
    self.__booking_list.append(booking)
  
  def add_treatment_transaction(self,booking_id,treatment_id,date,room_id,time_slot,therapist,add_on_list):
    booking = self.search_booking_by__id(booking_id)
    booking.treatment_list.append(Treatment_transaction(treatment_id,date,room_id,time_slot,therapist,add_on_list))
  
  # d1 = date(2026, 2, day)
  def cancle_booking(self,booking_id):
    booking = self.search_booking_by_id(booking_id)
    booking.status = "CANCLE"
    if booking.treatment_list[0].date - date.today() > timedelta(days=1):
    #Compare Time
      self.__notice_list.append(Message(self.__id,"Refund deposit 50%", datetime.now()))
    else:
      self.__notice_list.append(Message(self.__id,"No refund deposit", datetime.now()))

class Bronze(Customer):
  def __init__(self,id,name):
    super().__init__(id,name)
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
  def __init__(self,id,name):
      super().__init__(id,name)
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
  def __init__(self,id,name):
      super().__init__(id,name)
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
  def __init__(self,id,name):
      super().__init__(id,name)
      self.__discount = 0.2
      self.__booking_quota = 5
      self.__fee = 2500

  @property
  def discount(self):
    return self.__discount
  
  @property
  def booking_quota(self):
    return self.__booking_quota

class Treatment_transaction():
    def __init__(self,treatment,date,room,time_slot,therapist,add_on_list):
      self.__treatment = treatment
      self.__date = date
      self.__room = room
      self.__time_slot = time_slot
      self.__add_on_list = add_on_list
      self.__therapist = therapist

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
 

class Treatment():
    def __init__(self,id,name,price,duration,room_type):
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

class Add_on():
  def __init__(self,id,name,price):
    self.__id = id
    self.__name = name
    self.__price = price

  @property
  def id(self):
    return self.__id

  @property
  def price(self):
    return self.__price
# <==BOAT==>

# <==IAOON==>
class Room:
  def __init__(self,id):
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

class Dry_private_room(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class Dry_shared_room(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class Wet_private_room(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class Wet_shared_room(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class Slot:
  def __init__(self,date,slot_order,vacancy):
      self.__date = date
      self.__slot_order = slot_order
      self.__vacancy = vacancy

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
  def vacancy(self,value):
      self.__vacancy = value

class Administrative(Admin):
  def __init__(self,id,name,password):
      super().__init__(id,name,password)
  
  def get_booking_by_id(self,customer,booking_id):
      for booking in customer.booking_list:
          if booking.id == booking_id:
              return booking

  def calculate_total(self,customer,booking_id):
    booking = self.get_booking_by_id(customer,booking_id)            
    return booking.calculate_total()

class Payment(ABC):
  @abstractmethod
  def pay_deposit(self,deposit, **kwargs):
    pass

  @abstractmethod
  def pay_expenses(self,total, **kwargs):
    pass

class Cash(Payment):
  def pay_deposit(self,deposit,money):
    if money < deposit:
      return f"You have to pay {deposit} ฿ for deposite⚠️"
    else:
      return "Your booking confirmed✅"

  def pay_expenses(self,total,money):
    if money < total:
      return f"Not enough money! You have to pay {total} ฿⚠️"
    else:
      return f"Payment Success✅, Your change = {money - total} ฿"

class Promptpay(Payment):
  def pay_deposit(self,deposit,number):
    return f"Your booking confirmed✅, {deposit} ฿ deducted from your promptpay account ({number})"

  def pay_expenses(self,total,number):
    return f"Payment Sucsess✅, {total} ฿ deducted from your promptpay account ({number})"
# <==IAOON==>


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
  def status(self,value):
    self.__status = value

  def calculate_total(self):
    total = 0

    for treatment in self.treatment_list:
      total += treatment.treatment.price
      total += treatment.room.price
      # print(total)
      # print("add_on",treatment.add_onList)
      for add_on in treatment.add_on_list:
          total += add_on.price

      discount = total * self.__customer.discount
      total -= discount

    return total

  def pay_expenses(self,payment,total,**kwargs):
    self.__status = "Completed"
    return payment.pay_expenses(total,**kwargs)

  def pay_deposit(self,payment,deposit,**kwargs):
    self.__status = "Confirmed"
    return payment.pay_deposit(deposit,**kwargs)

class Therapist(Employee):
  def __init__(self, id, name, skill):
    super().__init__(id,name)
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

  spa = Spa(name = "LADKRABANG SPA")


  # Service //
  massage1 = Treatment(id = "TM-01", name = 'Traditional Thai Massage', price = 600, duration = 60,room_type = 'DRY')
  massage2 = Treatment(id = "TM-02", name = 'Traditional Thai Massage', price = 850, duration = 90,room_type = 'DRY')
  massage3 = Treatment(id = "TM-03", name = 'Traditional Thai Massage', price = 1100, duration = 120,room_type = 'DRY')
  massage4 = Treatment(id = "DT-03", name = 'Deep Tissue Massage', price = 1200, duration = 60,room_type = 'DRY')
  aroma = Treatment(id = "AT-02", name = 'Aroma Therapy', price = 1500, duration = 90,room_type = 'DRY')
  pool = Treatment(id = "HP-04", name = 'Hydrotherapy Pool', price = 800, duration = 60,room_type = 'WET')

  #Customer //
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
  


  #Employee // 
  t1 = Therapist(id="T0001", name="John", skill="Massage")
  t2 = Therapist(id="T0002", name="Anna", skill="Massage")
  t3 = Therapist(id="T0003", name="Emma", skill="Massage")
  t4 = Therapist(id="T0004", name="Olivia", skill="Massage")
    
    # Skill Aroma 4 คน
  t5 = Therapist(id="T0005", name="Justin", skill="Aroma")
  t6 = Therapist(id="T0006", name="Sophia", skill="Aroma")
  t7 = Therapist(id="T0007", name="Mary", skill="Aroma")
  t8 = Therapist(id="T0008", name="Matha", skill="Aroma")
    
    # Skill Pool 3 คน
  t9 = Therapist(id="T0009", name="Ben", skill="Pool")
  t10 = Therapist(id="T0010", name="Jane", skill="Pool")
  t11 = Therapist(id="T0011", name="May", skill="Pool")

  #Room //
    # ห้องแห้งส่วนตัว 3 ห้อง
  dr_p1 = Dry_private_room(id="ROOM-DRY-PV-001",price = 300)
  dr_p2 = Dry_private_room(id="ROOM-DRY-PV-002", price = 300)
  dr_p3 = Dry_private_room(id="ROOM-DRY-PV-003", price = 300)
    # ห้องแห้งรวม 1 ห้อง
  dr_s1 = Dry_shared_room(id="ROOM-DRY-SH-001", price = 0)
    
    # ห้องเปียกส่วนตัว 3 ห้อง
  wr_p1 = Wet_private_room(id="ROOM-WET-PV-001", price = 300)
  wr_p2 = Wet_private_room(id="ROOM-WET-PV-002", price = 300)
  wr_p3 = Wet_private_room(id="ROOM-WET-PV-003", price = 300)
    # ห้องเปียกรวม 1 ห้อง
  wr_s1 = Wet_shared_room(id="ROOM-WET-SH-001", price = 0)




  #Resource //
  res1 = Resource(id="RES-0001-BED", name="Massage Bed",amount=1)
  res2 = Resource(id="RES-0002-BED", name="Massage Bed",amount=1)
  res3 = Resource(id="RES-0003-BED", name="Massage Bed",amount=1)
  res4 = Resource(id="RES-0004-BED", name="Massage Bed",amount=1)
  res5 = Resource(id="RES-0005-BED", name="Massage Bed",amount=1)
  res6 = Resource(id="RES-0006-BED", name="Massage Bed",amount=1)
  res7 = Resource(id="RES-0007-POOL", name="Hydrotherapy Pool",amount=1)
  res8 = Resource(id="RES-0008-POOL", name="Hydrotherapy Pool",amount=1)
  res9 = Resource(id="RES-0009-POOL", name="Hydrotherapy Pool",amount=1)


  #add_on//
  add_on1 = Add_on(id = "OIL-P", name = "Premium Essential Oil", price = 350)
  add_on2 = Add_on(id = "CMP-H", name = "Herbal Compress", price = 250)
  add_on3 = Add_on(id = "SCRB-D", name = "Detox Scrub", price = 450) 
  add_on4 = Add_on(id = "SNK-S", name = "After-Service Snack Set", price = 150) 

  
  #Create Operation Officer//
  Reg1 = Registration_officer(id = "0001", name = "Kevin", Spa = spa, password = "12345")
  Ad1 = Administrative(id = "0002", name = "Paul", password = "12345")



  #Add them self//
  Reg1.add_employee(Reg1)
  Reg1.add_employee(Ad1)  

  #Login//
  # Reg1.verifyPassword(spa,"1234")
  spa.verify_admin(Reg1.id,"12345")

 
  
  #Add service//
  Reg1.add_treatment(massage1)
  Reg1.add_treatment(massage2)
  Reg1.add_treatment(massage3)
  Reg1.add_treatment(massage4)
  Reg1.add_treatment(aroma)
  Reg1.add_treatment(pool)


  #Add customer//
  Reg1.add_customer(c1)
  Reg1.add_customer(c2)
  Reg1.add_customer(c3)
  Reg1.add_customer(c4)
  Reg1.add_customer(c5)
  Reg1.add_customer(c6)
  Reg1.add_customer(c7)
  Reg1.add_customer(c8)
  Reg1.add_customer(c9)
  Reg1.add_customer(c10)


  # Add employee //
  end_date_month = date(2026,1,31)

  Reg1.add_employee(t1)
  Reg1.add_slot(end_date_month, t1, 1)
  Reg1.add_employee(t2)
  Reg1.add_slot(end_date_month, t2, 1)
  Reg1.add_employee(t3)
  Reg1.add_slot(end_date_month, t3, 1)
  Reg1.add_employee(t4)
  Reg1.add_slot(end_date_month, t4, 1)
  Reg1.add_employee(t5)
  Reg1.add_slot(end_date_month, t5, 1)
  Reg1.add_employee(t6)
  Reg1.add_slot(end_date_month, t6, 1)
  Reg1.add_employee(t7)
  Reg1.add_slot(end_date_month, t7, 1)
  Reg1.add_employee(t8)
  Reg1.add_slot(end_date_month, t8, 1)
  Reg1.add_employee(t9)
  Reg1.add_slot(end_date_month, t9, 1)
  Reg1.add_employee(t10)
  Reg1.add_slot(end_date_month, t10, 1)

  Reg1.add_room(dr_p1)
  Reg1.add_slot(end_date_month, dr_p1, 1)
  Reg1.add_room(dr_p2)
  Reg1.add_slot(end_date_month, dr_p2, 1)
  Reg1.add_room(dr_p3)
  Reg1.add_slot(end_date_month, dr_p3, 1)
  Reg1.add_room(wr_p1)
  Reg1.add_slot(end_date_month, wr_p1, 1)
  Reg1.add_room(wr_p2)
  Reg1.add_slot(end_date_month, wr_p2, 1)
  Reg1.add_room(wr_p3)
  Reg1.add_slot(end_date_month, wr_p3, 1)
  Reg1.add_room(dr_s1)
  Reg1.add_slot(end_date_month, dr_s1, 10)
  Reg1.add_room(wr_s1)
  Reg1.add_slot(end_date_month, wr_s1, 10)

  Reg1.add_resource(dr_p1.id,res1)
  Reg1.add_resource(dr_p2.id,res2)
  Reg1.add_resource(dr_p3.id,res3)
  Reg1.add_resource(dr_s1.id,res4)
  Reg1.add_resource(wr_p1.id,res5)
  Reg1.add_resource(wr_p2.id,res6)
  Reg1.add_resource(wr_p3.id,res7)
  Reg1.add_resource(wr_s1.id,res8)
  Reg1.add_resource(wr_s1.id,res9)
  
  Reg1.add_add_on(add_on1)
  Reg1.add_add_on(add_on2)
  Reg1.add_add_on(add_on3)
  Reg1.add_add_on(add_on4)
   
  return spa

spa = init_system()

@app.get("/getSlot/{customer_id}/{therapist_id}/{date}/{treatment_id}/{room_type}")
# @mcp.tool
def findFreeSlot(customer_id: str,therapist_id:str,date_ :str,treatment_id:str,room_type:str):
    YMD = date_.split('-')
    day = int(YMD[2])
    month = int(YMD[1])
    year = int(YMD[0])
    dateClass = date(year,month,day)
    customer = spa.search_customer_by_id(customer_id)
    therapist = spa.search_employee_by_id(therapist_id)
    therapist_slot = spa.get_employee_slot(therapist,dateClass)
    treatment = spa.search_treatment_by_id(treatment_id)
    room_type = f'ROOM-{treatment.room_type}-{room_type}'
    room_list = spa.get_room_by_room_type(room_type)
    free_slot_from_find_intersect_free_slot = []
    for room in room_list:
       roomSlot = spa.get_room_slot(room,dateClass)
       free_slot_from_find_intersect_free_slot.append((room,spa.find_intersect_free_slot(roomSlot,therapist_slot)))
    print(free_slot_from_find_intersect_free_slot)
    return free_slot_from_find_intersect_free_slot

# freeSlot  = findFreeSlot("C0001","T0005",date(2026,1,10),"TM-01","PV")

@app.post("/cancleBooking/{booking_id}/{customer_id}")
def cancleBooking(booking_id,customer_id):
    customer = spa.search_customer_by_id(customer_id)
    booking = customer.search_booking_by_id(booking_id)
    customer.cancleBooking(booking_id)
    for treatment in booking.treatment_list:
      room = spa.search_room_by_id(treatment.room.id)
      therapist = spa.search_employee_by_id(treatment.therapist.id)
      time_slot_list = treatment.timeSlot
      roomSlot = spa.get_room_slot(room,treatment.date)
      therapist_slot = spa.get_employee_slot(therapist,treatment.date)
      for time in time_slot_list:
        for slot_ in roomSlot:
            if slot_.slot_order == time:
                slot_.vacancy += 1
                # print(slot_.slot_order)
                # print(slot_.vacancy)
        for slot_ in therapist_slot:
            if slot_.slot_order == time:
                slot_.vacancy = 1
                # print(slot_.slot_order)
                # print(slot_.vacancy)
    return "Cancle Sucsess✅"


# def cancleBook(bookId,customer_id):
#    spa.requestToCancleBook(bookId,customer_id)


@app.post("/requestBooking/{customer_id}/{treatment_id_list}/{room_id_list}/{date_booking}/{time_slot_list}/{add_on_list}/{therapist_id_list}")
def requestBooking(customer_id,treatment_id_list_,room_id_list_,date_booking_,time_slot_list_,add_on_list_,therapist_id_list_):
    YMD = date_booking_.split('-')
    day = int(YMD[2])
    month = int(YMD[1])
    year = int(YMD[0])
    date_booking = date(year,month,day)
    time_slot_list = time_slot_list_.split('-')
    manage_slot = []
    slot = []
    treatment_id_list = treatment_id_list_.split(',')
    room_id_list = room_id_list_.split(',')
    therapist_id_list = therapist_id_list_.split(',')
    add_on_list = add_on_list_.split('&')
    manage_add_on = []
    add_on = []
    for i in range(len(time_slot_list)):
      slot = time_slot_list[i].split(',')
      slot_num = []
      for order in slot:
        slot_num.append(int(order))
      manage_slot.append(slot_num)
    for i in range(len(add_on_list)):
      add_on = add_on_list[i].split(',')
      manage_add_on.append(add_on)
    customer = spa.search_customer_by_id(customer_id)
    if customer.booking_quota <= 0 or customer.missed_count > 2:
      return "CANNOT MAKE BOOKING"
    d = date(2026,1,8) #วันที่ทำการจอง
    booking_id = f'BK-{d.year}{d.month if len(str(d.month)) > 1 else f'0{d.month}'}{d.day if len(str(d.day)) > 1 else f'0{d.day}'}-0001'
    booking = customer.booking(booking_id,customer,d)
    for i in range(len(treatment_id_list)):
      treatment = spa.search_treatment_by_id(treatment_id_list[i])
      room = spa.search_room_by_id(room_id_list[i])
      therapist = spa.search_employee_by_id(therapist_id_list[i])
      preadd_on = []
      for add_on_id in manage_add_on[i]:
          add_onClass = spa.search_add_on_by_id(add_on_id)
          preadd_on.append(add_onClass)
      customer.add_treatment_transaction(booking_id,treatment,date_booking,room,manage_slot[i],therapist,preadd_on)
      slot = manage_slot[i]
      roomSlot = spa.get_room_slot(room,date_booking)
      therapist_slot = spa.get_employee_slot(therapist,date_booking)
      for n in range(len(slot)):
        order = slot[n]
        for slot_ in roomSlot:
            if slot_.slot_order == order:
                slot_.vacancy -= 1
                # print(slot_.slot_order)
                # print(slot_.vacancy)
        for slot_ in therapist_slot:
            if slot_.slot_order == order:
                slot_.vacancy = 0
                # print(slot_.slot_order)
                # print(slot_.vacancy)
    #   print(customer.search_booking_by_id(bookId).treatment__list[0].treatment.name)
      return f"Booking Sucsess✅ - {booking_id}"


@app.get("/requestToPay/{customer_id}/{booking_id}/{payment_type}/{payment_value}")
def request_to_pay(customer_id,booking_id,payment_type,payment_value):
    customer = spa.search_customer_by_id(customer_id)
    booking = customer.search_booking_by_id(booking_id)
    total = booking.calculate_total()
    if payment_type == "Cash":
      cash = Cash()
      return booking.pay_expenses(cash,deposit,money=int(payment_value))
    elif payment_type == "Promptpay":
      promptpay = Promptpay()
      return booking.pay_expenses(promptpay,total,number=payment_value)  


# requestBooking("C0001",["TM-01"],["ROOM-DRY-PV-002"],date(2026,1,10),[[1,2]],[["OIL-P"]],["T0005"])
# cancleBooking("BK-20260108-0001","C0001")
# Total = request_to_pay("C0001","0002","BK-20260108-0001")
# print(Total)

if __name__ == "__main__":
  uvicorn.run("spa:app",host="127.0.0.1",port=8000,log_level="info")
#   mcp.run()













