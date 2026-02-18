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
    self.__customerList = []
    self.__employeeList = []
    self.__roomList = []
    self.__transactionList = []
    self.__treatmentList = []
    self.__resourceList = []
    self.__addOnList = []

  @property
  def employeeList(self):
    return self.__employeeList

  def searchCustomerById(self,id):
    for customer in self.__customerList:
      if customer.id == id:
        return customer

  def searchEmployeeById(self,id):
    for employee in self.__employeeList:
      if employee.id == id:
        return employee

  def searchTreatmentById(self,id):
    for treatment in self.__treatmentList:
      if treatment.id == id:
        return treatment

  def searchAddOnById(self,id):
    for addOn in self.__addOnList:
      if addOn.id == id:
        return addOn

  def searchRoomById(self,id):
    for room in self.__roomList:
      if room.id == id:
        return room

  def getRoomByRoomType(self,type):
    resultList = []
    for room in self.__roomList:
      # print(room.id,type)
      if room.id.startswith(type):
        resultList.append(room)
    return resultList

  # def requestToPay(self,admin,customer,bookId):
  #   return admin.calculateTotal(customer,bookId)

  def getEmployeeSlot(self,Employee,date):
    slotAll = Employee.slot
    slotInDate = []
    for slot in slotAll:
        if slot.date == date:
            slotInDate.append(slot)
    return slotInDate

  def getRoomSlot(self,Room,date):
    slotAll = Room.slot
    slotInDate = []
    for slot in slotAll:
        if slot.date == date:
            slotInDate.append(slot)
    return slotInDate

  def verifyAdmin(self,employeeId,inputPassword):
    employee = self.searchEmployeeById(employeeId)
    password = employee.password
    if password == inputPassword:
      employee.login = True

  def addEmployee(self,Employee):
    self.__employeeList.append(Employee)

  def addTreatment(self,Treatment):
    self.__treatmentList.append(Treatment)

  def addCustomer(self,Customer):
    self.__customerList.append(Customer)

  def addRoom(self,Room):
    self.__roomList.append(Room)

  def addAddOnList(self,AddOn):
    self.__addOnList.append(AddOn)

  def requesToCancleBook(self,bookId,customerId):
    customer = self.searchCustomerById(customerId)
    book = customer.searchBookingById(bookId)
    customer.cancleBook(bookId)
    for treatment in book.treatmentList:
      room = self.searchRoomById(treatment.room.id)
      therapist = self.searchEmployeeById(treatment.therapistId)
      timeSlotList = treatment.timeSlot
      for time in timeSlotList:
        therapist.slot[treatment.date.day].slotList[time][1] = 1 
        room.slot[treatment.date.day].slotList[time][1] += 1

  def findIntersectFreeSlot(self,roomSlot,therapistSlot):
    listOfIntersectFreeSlot = []
    for i in range(0,16):
        if roomSlot[i].vacancy > 0 and therapistSlot[i].vacancy > 0:
            listOfIntersectFreeSlot.append(roomSlot[i])
    return listOfIntersectFreeSlot
        
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

class RegistrationOfficer(Admin):
  def __init__(self,id,name,Spa,password):
    super().__init__(id,name,password)
    self.__spa = Spa

#   def addSlot(self,Entity,vacancy):
#     if self.login:
#       for i in range(1,32):
#         slot = Slot(date(2026,1,i),vacancy)
#         Entity.slot.append(slot)

  def addSlot(self,endDateMonth,Entity,vacancy):
    year = endDateMonth.year
    month = endDateMonth.month
    endDate = endDateMonth.day
    if self.login:
      for i in range(1,endDate + 1):
        for n in range(1,17):
            slot = Slot(date(year,month,i),n,vacancy)
            Entity.slot.append(slot)
  
  def addCustomer(self,Customer):
    if self.login:
        self.__spa.addCustomer(Customer)
        Customer.addNoticeList(Message(Customer.id,"OTP-005",datetime.now()))
  
  def addEmployee(self,Employee):
    if isinstance(Employee,RegistrationOfficer) or isinstance(Employee,Administrative) or self.login:
      self.__spa.addEmployee(Employee)

  def addRoom(self,Room):
    if self.login:
      self.__spa.addRoom(Room)

  def addResource(self,roomId,Resource):
    if self.login:
      room = self.__spa.searchRoomById(roomId)
      room.resourceList.append(Resource)

  def addAddOn(self,AddOn):
    if self.login:
      self.__spa.addAddOnList(AddOn)

  def addTreatment(self,Treatment):
    if self.login:
      self.__spa.addTreatment(Treatment)

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
    self.__bookingList = []
    self.__freeSlotFromFindIntersectFreeSlot = []
    self.__noticeList = []
    self.__missedCount = 0

  @property
  def id(self):
    return self.__id
    
  @property
  def name(self):
    return self.__name

  @property
  def bookingList(self):
    return self.__bookingList

  @property
  def missedCount(self):
    return self.__missedCount

  def addNoticeList(self,Message):
    self.__noticeList.append(Message)

  def searchBookingById(self,id):
    for  booking in self.__bookingList:
      if booking.id == id:
        return booking

  def book(self,id,customerId,date):
    book = Booking(id,self,date)
    self.__bookingList.append(book)
  
  def addTreatmentTransaction(self,bookId,treatmentId,date,roomId,timeSlot,therapist,addOnList):
    book = self.searchBookingById(bookId)
    book.treatmentList.append(TreatmentTransaction(treatmentId,date,roomId,timeSlot,therapist,addOnList))
  
  # d1 = date(2026, 2, day)
  def cancleBook(self,bookId):
    book = self.searchBookingById(bookId)
    book.status = "CANCLE"
    if book.treatmentList[0].date - date.today() > timedelta(days=1):
    #Compare Time
      self.__noticeList.append(Message(self.__id,"Refund deposit 50%", datetime.now()))
    else:
      self.__noticeList.append(Message(self.__id,"No refund deposit", datetime.now()))

class Bronze(Customer):
  def __init__(self,id,name):
    super().__init__(id,name)
    self.__discount = 0
    self.__bookingQuota = 1
    self.__fee = 0
  @property
  def discount(self):
    return self.__discount

  @property
  def bookingQuota(self):
    return self.__bookingQuota

class Silver(Customer):
  def __init__(self,id,name):
      super().__init__(id,name)
      self.__discount = 0.05
      self.__bookingQuota = 2
      self.__fee = 1000
  @property
  def discount(self):
    return self.__discount
  
  @property
  def bookingQuota(self):
    return self.__bookingQuota
  
class Gold(Customer):
  def __init__(self,id,name):
      super().__init__(id,name)
      self.__discount = 0.1 
      self.__bookingQuota = 3
      self.__fee = 1500
  @property
  def discount(self):
    return self.__discount
  
  
  @property
  def bookingQuota(self):
    return self.__bookingQuota

class Platinum(Customer):
  def __init__(self,id,name):
      super().__init__(id,name)
      self.__discount = 0.2
      self.__bookingQuota = 5
      self.__fee = 2500

  @property
  def discount(self):
    return self.__discount
  
  @property
  def bookingQuota(self):
    return self.__bookingQuota

class TreatmentTransaction():
    def __init__(self,treatment,date,room,timeSlot,therapist,addOnList):
      self.__treatment = treatment
      self.__date = date
      self.__room = room
      self.__timeSlot = timeSlot
      self.__addOnList = addOnList
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
    def timeSlot(self):
      return self.__timeSlot

    @property  
    def addOnList(self):
      return self.__addOnList

    @property
    def therapist(self):
      return self.__therapist
 

class Treatment():
    def __init__(self,id,name,price,duration,roomType):
      self.__name = name
      self.__id = id
      self.__price = price
      self.__duration = duration
      self.__roomType = roomType

    @property
    def id(self):
      return self.__id

    @property
    def price(self):
      return self.__price

    @property
    def roomType(self):
      return self.__roomType

    @property
    def name(self):
      return self.__name

class AddOn():
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
    self.__resourceList = []

  @property
  def id(self):
    return self.__id
  
  @property
  def slot(self):
    return self.__slot

  @property
  def resourceList(self):
    return self.__resourceList

  @resourceList.setter
  def resourceList(self, value):
    self.__resourceList.append(value)

class DryPrivateRoom(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

  @property
  def price(self):
    return self.__price

class DrySharedRoom(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class WetPrivateRoom(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class WetSharedRoom(Room):
  def __init__(self,id,price):
    super().__init__(id)
    self.__price = price

class Slot:
  def __init__(self,date,slotOrder,vacancy):
      self.__date = date
      self.__slotOrder = slotOrder
      self.__vacancy = vacancy

  @property
  def date(self):
      return self.__date

  @property
  def slotOrder(self):
      return self.__slotOrder

  @property
  def vacancy(self):
      return self.__vacancy

  @vacancy.setter
  def vacancy(self,value):
      self.__vacancy = value

class Administrative(Admin):
  def __init__(self,id,name,password):
      super().__init__(id,name,password)
  
  def getBookingById(self,customer,bookingId):
      for booking in customer.bookingList:
          if booking.id == bookingId:
              return booking

  def calculateTotal(self,customer,bookingId):
    booking = self.getBookingById(customer,bookingId)            
    return booking.calculateTotal()

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
    self.__treatmentList = []
    self.__status = "Waiting deposit"

  @property
  def id(self):
    return self.__id

  def getTreatmentList(self):
    return self.__treatmentList

  @property
  def treatmentList(self):
    return self.__treatmentList

  @property
  def date(self):
    return self.__date
  
  @property
  def status(self):
    return self.__status

  @status.setter
  def status(self,value):
    self.__status = value

  def calculateTotal(self):
    total = 0

    for treatment in self.treatmentList:
      total += treatment.treatment.price
      total += treatment.room.price
      # print(total)
      # print("Addon",treatment.addOnList)
      for addon in treatment.addOnList:
          total += addon.price

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
  massage1 = Treatment(id = "TM-01", name = 'TraditionalThaiMassage', price = 600, duration = 60,roomType = 'DRY')
  massage2 = Treatment(id = "TM-02", name = 'TraditionalThaiMassage', price = 850, duration = 90,roomType = 'DRY')
  massage3 = Treatment(id = "TM-03", name = 'TraditionalThaiMassage', price = 1100, duration = 120,roomType = 'DRY')
  massage4 = Treatment(id = "DT-03", name = 'Deep Tissue Massage', price = 1200, duration = 60,roomType = 'DRY')
  aroma = Treatment(id = "AT-02", name = 'Aroma Therapy', price = 1500, duration = 90,roomType = 'DRY')
  pool = Treatment(id = "HP-04", name = 'Hydrotherapy Pool', price = 800, duration = 60,roomType = 'WET')

  #Customer //
  c1 = Silver(id="C0001", name="Batman")
  c10 = Silver(id="C0010", name="Aquaman")
  c2 = Bronze(id="C0002", name="Superman")
  c3 = Gold(id="C0003", name="Iron Man")
  c4 = Platinum(id="C0004", name="Spider-Man")
  c5 = Gold(id="C0005", name="Wonder Woman")
  c6 = Silver(id="C0006", name="Black Widow")
  c7 = Bronze(id="C0007", name="Thor")
  c8 = Platinum(id="C0008", name="Hulk")
  c9 = Bronze(id="C0009", name="Flash")


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
  dr_p1 = DryPrivateRoom(id="ROOM-DRY-PV-001",price = 300)
  dr_p2 = DryPrivateRoom(id="ROOM-DRY-PV-002", price = 300)
  dr_p3 = DryPrivateRoom(id="ROOM-DRY-PV-003", price = 300)
    # ห้องแห้งรวม 1 ห้อง
  dr_s1 = DrySharedRoom(id="ROOM-DRY-SH-001", price = 0)
    
    # ห้องเปียกส่วนตัว 3 ห้อง
  wr_p1 = WetPrivateRoom(id="ROOM-WET-PV-001", price = 300)
  wr_p2 = WetPrivateRoom(id="ROOM-WET-PV-002", price = 300)
  wr_p3 = WetPrivateRoom(id="ROOM-WET-PV-003", price = 300)
    # ห้องเปียกรวม 1 ห้อง
  wr_s1 = WetSharedRoom(id="ROOM-WET-SH-001", price = 0)




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


  #Addon//
  addOn1 = AddOn(id = "OIL-P", name = "Premium Essential Oil", price = 350)
  addOn2 = AddOn(id = "CMP-H", name = "Herbal Compress", price = 250)
  addOn3 = AddOn(id = "SCRB-D", name = "Detox Scrub", price = 450) 
  addOn4 = AddOn(id = "SNK-S", name = "After-Service Snack Set", price = 150) 

  
  #Create Operation Officer//
  Reg1 = RegistrationOfficer(id = "0001", name = "Kevin", Spa = spa, password = "12345")
  Ad1 = Administrative(id = "0002", name = "Paul", password = "12345")



  #Add them self//
  Reg1.addEmployee(Reg1)
  Reg1.addEmployee(Ad1)  

  #Login//
  # Reg1.verifyPassword(spa,"1234")
  spa.verifyAdmin(Reg1.id,"12345")

 
  
  #Add service//
  Reg1.addTreatment(massage1)
  Reg1.addTreatment(massage2)
  Reg1.addTreatment(massage3)
  Reg1.addTreatment(massage4)
  Reg1.addTreatment(aroma)
  Reg1.addTreatment(pool)


  #Add customer//
  Reg1.addCustomer(c1)
  Reg1.addCustomer(c2)
  Reg1.addCustomer(c3)
  Reg1.addCustomer(c4)
  Reg1.addCustomer(c5)
  Reg1.addCustomer(c6)
  Reg1.addCustomer(c7)
  Reg1.addCustomer(c8)
  Reg1.addCustomer(c9)
  Reg1.addCustomer(c10)


  # Add employee //
  endDateMonth = date(2026,1,31)

  Reg1.addEmployee(t1)
  Reg1.addSlot(endDateMonth, t1, 1)
  Reg1.addEmployee(t2)
  Reg1.addSlot(endDateMonth, t2, 1)
  Reg1.addEmployee(t3)
  Reg1.addSlot(endDateMonth, t3, 1)
  Reg1.addEmployee(t4)
  Reg1.addSlot(endDateMonth, t4, 1)
  Reg1.addEmployee(t5)
  Reg1.addSlot(endDateMonth, t5, 1)
  Reg1.addEmployee(t6)
  Reg1.addSlot(endDateMonth, t6, 1)
  Reg1.addEmployee(t7)
  Reg1.addSlot(endDateMonth, t7, 1)
  Reg1.addEmployee(t8)
  Reg1.addSlot(endDateMonth, t8, 1)
  Reg1.addEmployee(t9)
  Reg1.addSlot(endDateMonth, t9, 1)
  Reg1.addEmployee(t10)
  Reg1.addSlot(endDateMonth, t10, 1)

  Reg1.addRoom(dr_p1)
  Reg1.addSlot(endDateMonth, dr_p1, 1)
  Reg1.addRoom(dr_p2)
  Reg1.addSlot(endDateMonth, dr_p2, 1)
  Reg1.addRoom(dr_p3)
  Reg1.addSlot(endDateMonth, dr_p3, 1)
  Reg1.addRoom(wr_p1)
  Reg1.addSlot(endDateMonth, wr_p1, 1)
  Reg1.addRoom(wr_p2)
  Reg1.addSlot(endDateMonth, wr_p2, 1)
  Reg1.addRoom(wr_p3)
  Reg1.addSlot(endDateMonth, wr_p3, 1)
  Reg1.addRoom(dr_s1)
  Reg1.addSlot(endDateMonth, dr_s1, 10)
  Reg1.addRoom(wr_s1)
  Reg1.addSlot(endDateMonth, wr_s1, 10)

  Reg1.addResource(dr_p1.id,res1)
  Reg1.addResource(dr_p2.id,res2)
  Reg1.addResource(dr_p3.id,res3)
  Reg1.addResource(dr_s1.id,res4)
  Reg1.addResource(wr_p1.id,res5)
  Reg1.addResource(wr_p2.id,res6)
  Reg1.addResource(wr_p3.id,res7)
  Reg1.addResource(wr_s1.id,res8)
  Reg1.addResource(wr_s1.id,res9)
  
  Reg1.addAddOn(addOn1)
  Reg1.addAddOn(addOn2)
  Reg1.addAddOn(addOn3)
  Reg1.addAddOn(addOn4)
   
  return spa

spa = init_system()

@app.get("/getSlot/{customerId}/{therapistId}/{date}/{treatmentId}/{roomType}")
# @mcp.tool
def findFreeSlot(customerId: str,therapistId:str,date_ :str,treatmentId:str,roomType:str):
    YMD = date_.split('-')
    day = int(YMD[2])
    month = int(YMD[1])
    year = int(YMD[0])
    dateClass = date(year,month,day)
    customer = spa.searchCustomerById(customerId)
    therapist = spa.searchEmployeeById(therapistId)
    therapistSlot = spa.getEmployeeSlot(therapist,dateClass)
    treatment = spa.searchTreatmentById(treatmentId)
    roomType = f'ROOM-{treatment.roomType}-{roomType}'
    roomList = spa.getRoomByRoomType(roomType)
    freeSlotFromFindIntersectFreeSlot = []
    for room in roomList:
       roomSlot = spa.getRoomSlot(room,dateClass)
       freeSlotFromFindIntersectFreeSlot.append((room,spa.findIntersectFreeSlot(roomSlot,therapistSlot)))
    print(freeSlotFromFindIntersectFreeSlot)
    return freeSlotFromFindIntersectFreeSlot

# freeSlot  = findFreeSlot("C0001","T0005",date(2026,1,10),"TM-01","PV")

@app.post("/cancleBook/{bookId}/{customerId}")
def cancleBook(bookId,customerId):
    customer = spa.searchCustomerById(customerId)
    book = customer.searchBookingById(bookId)
    customer.cancleBook(bookId)
    for treatment in book.treatmentList:
      room = spa.searchRoomById(treatment.room.id)
      therapist = spa.searchEmployeeById(treatment.therapist.id)
      timeSlotList = treatment.timeSlot
      roomSlot = spa.getRoomSlot(room,treatment.date)
      therapistSlot = spa.getEmployeeSlot(therapist,treatment.date)
      for time in timeSlotList:
        for slot_ in roomSlot:
            if slot_.slotOrder == time:
                slot_.vacancy += 1
                # print(slot_.slotOrder)
                # print(slot_.vacancy)
        for slot_ in therapistSlot:
            if slot_.slotOrder == time:
                slot_.vacancy = 1
                # print(slot_.slotOrder)
                # print(slot_.vacancy)
    return "Cancle Sucsess✅"


# def cancleBook(bookId,customerId):
#    spa.requestToCancleBook(bookId,customerId)


@app.post("/requestBooking/{customerId}/{treatmentIdList}/{roomIdList}/{dateBook}/{timeSlotList}/{addOnListList}/{therapistIdList}")
def requestBooking(customerId,treatmentIdList_,roomIdList_,dateBook_,timeSlotList_,addOnListList_,therapistIdList_):
    YMD = dateBook_.split('-')
    day = int(YMD[2])
    month = int(YMD[1])
    year = int(YMD[0])
    dateBook = date(year,month,day)
    timeSlotList = timeSlotList_.split('-')
    manageSlot = []
    slot = []
    treatmentIdList = treatmentIdList_.split(',')
    roomIdList = roomIdList_.split(',')
    therapistIdList = therapistIdList_.split(',')
    addOnListList = addOnListList_.split('&')
    manageAddOn = []
    addOn = []
    for i in range(len(timeSlotList)):
      slot = timeSlotList[i].split(',')
      slotNum = []
      for order in slot:
        slotNum.append(int(order))
      manageSlot.append(slotNum)
    for i in range(len(addOnListList)):
      addOn = addOnListList[i].split(',')
      manageAddOn.append(addOn)
    customer = spa.searchCustomerById(customerId)
    if customer.bookingQuota <= 0 or customer.missedCount > 2:
      return "CANNOT MAKE BOOKING"
    d = date(2026,1,8) #วันที่ทำการจอง
    bookId = f'BK-{d.year}{d.month if len(str(d.month)) > 1 else f'0{d.month}'}{d.day if len(str(d.day)) > 1 else f'0{d.day}'}-0001'
    book = customer.book(bookId,customer,d)
    for i in range(len(treatmentIdList)):
      treatment = spa.searchTreatmentById(treatmentIdList[i])
      room = spa.searchRoomById(roomIdList[i])
      therapist = spa.searchEmployeeById(therapistIdList[i])
      preAddOn = []
      for addOnId in manageAddOn[i]:
          addOnClass = spa.searchAddOnById(addOnId)
          preAddOn.append(addOnClass)
      customer.addTreatmentTransaction(bookId,treatment,dateBook,room,manageSlot[i],therapist,preAddOn)
      slot = manageSlot[i]
      roomSlot = spa.getRoomSlot(room,dateBook)
      therapistSlot = spa.getEmployeeSlot(therapist,dateBook)
      for n in range(len(slot)):
        order = slot[n]
        for slot_ in roomSlot:
            if slot_.slotOrder == order:
                slot_.vacancy -= 1
                # print(slot_.slotOrder)
                # print(slot_.vacancy)
        for slot_ in therapistSlot:
            if slot_.slotOrder == order:
                slot_.vacancy = 0
                # print(slot_.slotOrder)
                # print(slot_.vacancy)
    #   print(customer.searchBookingById(bookId).treatmentList[0].treatment.name)
      return f"Booking Sucsess✅ - {bookId}"


@app.get("/requestToPay/{customerId}/{bookId}/{payment_type}/{payment_value}")
def request_to_pay(customerId,bookId,payment_type,payment_value):
    customer = spa.searchCustomerById(customerId)
    booking = customer.searchBookingById(bookId)
    total = booking.calculateTotal()
    if payment_type == "Cash":
      cash = Cash()
      return booking.pay_expenses(cash,deposit,money=int(payment_value))
    elif payment_type == "Promptpay":
      promptpay = Promptpay()
      return booking.pay_expenses(promptpay,total,number=payment_value)  


# requestBooking("C0001",["TM-01"],["ROOM-DRY-PV-002"],date(2026,1,10),[[1,2]],[["OIL-P"]],["T0005"])
# cancleBook("BK-20260108-0001","C0001")
# Total = request_to_pay("C0001","0002","BK-20260108-0001")
# print(Total)

if __name__ == "__main__":
  uvicorn.run("spa:app",host="127.0.0.1",port=8000,log_level="info")
#   mcp.run()













