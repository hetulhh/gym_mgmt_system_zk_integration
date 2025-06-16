from ctypes import *
from win32com.client import Dispatch
import pythoncom

class zksdk:

    def __init__(self,ip, port,machine_number):

        self.zkhandle = Dispatch("zkemkeeper.ZKEM",pythoncom.CoInitialize())
        self.bIsConnected = False
        self.iMachineNumber = machine_number
        self.idwErrorCode = 0
        self.iDeviceTpye = 1
        self.bAddControl = True
        self.ip = ip
        self.port = port

    @property
    def getConnectState(self) -> bool:
        """Return True if connection is active"""
        return bool(self.bIsConnected is not None)

    def setConnectState(self, state):
        self.bIsConnected = state

    def connectDevice(self):
        self.bIsConnected = self.zkhandle.Connect_Net(self.ip, self.port)
        if self.bIsConnected:
            print("Device connected")
        else:
            print("Device is not connected")
        return self.bIsConnected

    def disconnectDevice(self):
        if self.bIsConnected:
            self.zkhandle.Disconnect()
            print("Device Disconnected")

    def getDeviceTime(self):
        resultado = self.zkhandle.GetDeviceTime(self.iMachineNumber)
        data = '/'.join(map(str,resultado[1:4]))
        hora = ':'.join(map(str,resultado[4:7]))
        return data +" "+ hora

     
    def setDeviceTime2(self,year,month,day,hour,minute,second):
        print(self.zkhandle.SetDeviceTime2(self.iMachineNumber,year,month,day,hour,minute,second))

    def setDeviceTime(self):
        print(self.zkhandle.SetDeviceTime(self.iMachineNumber))

    def getSerialNumber(self):
        print(self.zkhandle.GetSerialNumber(self.iMachineNumber))

    def getFirmwareVersion(self):
        print(self.zkhandle.GetFirmwareVersion(self.iMachineNumber))

    # def getDeviceStatus(self):
    #         print(self.zkhandle.GetDeviceStatus(self.iMachineNumber))

    def getAllUserInfo(self):
        self.zkhandle.ReadAllUserID(self.iMachineNumber);
        users=[()]
        while True:
            row = self.zkhandle.GetAllUserInfo(self.iMachineNumber)             
            if row[0] == False:
                return users
                break             
            sCardnumber = self.zkhandle.GetStrCardNumber()
            row += tuple(sCardnumber)
            users.append(row)            

    def getUserInfo(self,userId):
        self.zkhandle.GetUserInfo(self.iMachineNumber,userId);
    
    def deleteUserInfoEx(self,userId):
        self.zkhandle.DeleteUserInfoEx(self.iMachineNumber,userId);

    def enableDevice(self):
        self.zkhandle.EnableDevice(self.iMachineNumber,1)

    def disableDevice(self):
        self.zkhandle.EnableDevice(self.iMachineNumber,0)

    def enableUser(self,userId,enable):
        self.zkhandle.EnableUser(self.iMachineNumber,userId,0,0,enable)

    def getCardNumber(self):
        self.zkhandle.GetStrCardNumber()

    def setCardNumber(self,card_number):
        self.zkhandle.SetStrCardNumber(card_number)

    def getAllGLogData(self):
        self.zkhandle.ReadAllGLogData(self.iMachineNumber);
        logData = [()]
        while True:
            #GetGeneralLogDataStr
            #GetAllGLogData
            row = self.zkhandle.GetGeneralLogDataStr(self.iMachineNumber)
            logData.append(row)
            if row[0]== False:
                print(logData)
                return logData
                break

    def setUserInfo(self,user_id,username,password,user_privilege,enable):
        return self.zkhandle.SetUserInfo(self.iMachineNumber,user_id,username,password,user_privilege,enable);

    def refreshData(self):
        self.zkhandle.RefreshData(self.iMachineNumber)

    def deleteUser(self,userId):    
        return self.zkhandle.DeleteEnrollData(self.iMachineNumber,userId,1,12)
    
    def getSysOption(self,option):
        return self.zkhandle.GetSysOption(self.iMachineNumber,option)
    
    def unlockDoor(self):
        return self.zkhandle.ACUnlock(self.iMachineNumber,10)

    # def setUserValidDate(self,user_id,expires,validCount,startDate,endDate):
    #     return self.zkhandle.SetUserValidDate(self.iMachineNumber,user_id,expires,validCount, startDate,endDate)     
    
    # def getUserValidDate(self, userId):
    #      return self.zkhandle.GetUserValidDate(self.iMachineNumber,userId)

class Utils:
    def notify(notification_title,notification_type,notification_message,sticky):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': notification_title,
                    'message': notification_message,
                    'type': notification_type,
                    'sticky': sticky,  
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }