import logging
import csv
import hashlib
import azure.functions as func
from io import StringIO
from datetime import datetime
import random
import pandas as pd
import pypyodbc
import xlrd

def main():
    csv_file = open('C:/Users/Alex/Desktop/Budget/test.csv')
    test = list(csv.reader(csv_file, delimiter=','))

    transactions = processTransactions(test)
    uploadToSQL(transactions)

    logging.info("TransactionsProcessed")

def uploadToSQL(transacitonData):
    
    df = pd.DataFrame(transacitonData, columns=['transDate', 'merchant', 'amount', 'account', 'transID', 'type'])
    df = df[['transID', 'transDate', 'merchant', 'amount', 'type', 'account']]

    server = 'adbudget.database.windows.net' 
    database = 'adbudgetdb' 
    username = 'Thamous' 
    password = 'CHMqcJbIMmqlBwxMKRoT2BBc0E8We9vaUfJS0s' 

    cnxn = pypyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()

    for row in df.itertuples():
        cursor.execute('''
            INSERT INTO adbudgetdb.dbo.transactions (transID, transDate, merchant, amount, type, account)
                VALUES (?,?,?,?,?,?)
                ''',
                row.transID, 
                row.transDate,
                row.merchant,
                row.amount, 
                row.type,
                row.account
        )

    cnxn.commit()
    
    return 0

def processTransactions(myblob):
    transactionsData = myblob
    # transactionString = myblob.read().decode("utf-8")

    #transactionsData = []

    #f = StringIO(transactionString)
    #transactionsData = list(csv.reader(f))
    transactionsData.pop(0)
    if(transactionsData[len(transactionsData)-1][0]) == '':
        transactionsData.pop()

    for index, data in enumerate(transactionsData):
        transactionsData[index] = processRecordExcel(data)
        print(index)
    
    return transactionsData

def processRecordExcel(data):
    tempData = data
    tempData[0] = convertToDate(int(tempData[0]))
    tempData.pop(2)
    tempData.pop(2)
    tempData.pop()
    tempData.pop()
    tempData.pop()
    tempData.pop()
    tempData.pop(7)
    tempData.pop(7)
    tempData.pop(4)
    tempData.pop(4)
    tempData[3] = accountCodes[tempData[3]]
    tempData[5] = typeCodes[tempData[5]]
    tempData[2] = tempData[2].replace('-', '')


    return tempData

def convertToDate(dateInt):
    datetime_date = xlrd.xldate_as_datetime(dateInt, 0)
    date_object = datetime_date.date()
    string_date = date_object.isoformat()
    return string_date

def prcoessRecord(data):
    tempData = []
    tempData = data
    tempData.pop()
    tempData.pop()
    tempData.pop(5)
    tempData.pop(2)
    tempData.append(hashlib.md5((tempData[0]+tempData[1]+tempData[2]+tempData[3]+tempData[4] + datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + str(random.randint(0,200))).encode()).hexdigest())

    tempData[4] = accountCodes[tempData[4]]
    tempData[3] = typeCodes[tempData[3]]

    return tempData

accountCodes = {
    "Barclays - Savings":1,
    "401k - Microsoft":2,
    "401k - Capgemini":3,
    "Citi - AA Platinum":4,
    "Citi - AA Miles Up":5,
    "USAA - Visa":6,
    "USAA - Checking":7,
    "Chase - Sapphire":8,
    "Chase - Amazon Prime":9,
    "Chase - Checking":10,
    "Amex - Marriot":11,
    "Amex - Blue Cash Preferred":12,
    "CapitalOne - Auto Loan":13
}

typeCodes = {
    "debit": 1,
    "credit": 2,
    "Expense": 1,
    "Income": 3,
    "Transfer": 4
}

main()