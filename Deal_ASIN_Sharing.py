import os
import pandas as pd
import win32com.client as win32
from selenium import webdriver
import time
from time import sleep
from selenium.webdriver.common.by import By
import mysql.connector


#fetching midway cookie
def get_mwinit_cookie():
    MidwayConfigDir = os.path.join(os.path.expanduser("~"), ".midway")
    MidwayCookieJarFile = os.path.join(MidwayConfigDir, "cookie")
    fields = []
    keyfile = open(MidwayCookieJarFile, "r")
    for line in keyfile:
        # parse the record into fields (separated by whitespace)
        fields = line.split()
        if len(fields) != 0:
            # get the yubi session token and expire time
            if fields[0] == "#HttpOnly_midway-auth.amazon.com":
                session_token = fields[6].replace("\n", "")
                expires = fields[4]
            # get the user who generated the session token
            elif fields[0] == "midway-auth.amazon.com":
                username = fields[6].replace("\n", "")
    keyfile.close()
    # make sure the session token hasn't expired
    if time.gmtime() > time.gmtime(int(expires)):
        raise SystemError("Your Midway token has expired. Run mwinit to renew")
    # construct the cookie value required by calls to k2
    cookie = {"username": username, "session": session_token}
    return cookie


# Create the webdriver object. Here the
# chromedriver is present in the driver
# folder of the root directory.
# driver = webdriver.Chrome(r"D:\Users\skathir\Desktop\Python code for oncall daily data\chromedriver_win\chromedriver.exe")
driver = webdriver.Chrome()
# time.sleep(15)
# options = webdriver.ChromeOptions()
# options.add_experimental_option('w3c', False)
# driver = webdriver.Chrome(r'./chromedriver.exe', options=options)
midway_url = 'https://midway-auth.amazon.com'
cookie = get_mwinit_cookie()
driver.get(midway_url)
cookie_dict1 = {'domain': '.midway-auth.amazon.com',
                'name': 'user_name',
                'value': cookie['username'],
                'path': '/',
                'httpOnly': False,
                'secure': True}

cookie_dict2 = {
    'domain': '.midway-auth.amazon.com',
    'name': 'session',
    'value': cookie['session'],
    'path': '/',
    'httpOnly': True,
    'secure': True}

driver.add_cookie(cookie_dict1)
driver.add_cookie(cookie_dict2)

match = False
while not match:
    driver.get(midway_url)
    if driver.current_url == 'https://midway-auth.amazon.com/':
        match = True
    sleep(1)
    driver.refresh()
driver.maximize_window()

##################################

driver.get("https://issues.amazon.com/")
time.sleep(55)
# Maximize the window and let code stall
# for 10s to properly maximise the window.
# driver.maximize_window()
# time.sleep(10)

# Obtain button by link text and click.
button = driver.find_elements(By.XPATH, '//*[@id="view-content-left"]/div[1]/div[1]/div[1]/div/button[1]')
button[0].click()
time.sleep(1)

button = driver.find_elements(By.XPATH, '//*[@id="view-content-left"]/div[1]/div[1]/div[1]/div/ul/li[1]/a')
button[0].click()
time.sleep(1)

button = driver.find_elements(By.XPATH, '//*[@id="submit-custom-export-job"]')
button[0].click()
time.sleep(190)

button = driver.find_elements(By.XPATH, '//*[@id="job-details"]/div/section/div/div/table/tbody/tr/td[1]/a')
button[0].click()
time.sleep(2)
button = driver.find_elements(By.XPATH, '//*[@id="job-details"]/div/section/div/div/table/tbody/tr/td[1]/a')
time.sleep(3)

mydata = pd.read_csv(r"D:\Users\skathir\Downloads\documentSearch_skathir.csv")
# print(mydata['Description'])
# mydata[['Description','Description1']] = mydata['Description'].str.split('and lister All',expand=True)
# print(mydata['Description'])
# mydata['asin'] = mydata['Description'].str.split(' ').str[9]
# mydata.to_excel(r"D:\Users\skathir\Downloads\documentSearch_skathir.xlsx")
# mydata.to_csv('oncal_data.csv')

mydata['Description1'] = mydata['Description'].str.split('and lister All').str[0]
mydata['ASIN'] = mydata['Description'].str.split(' ').str[9]
mydata['marketplace_id'] = mydata['Description'].str.split(' ').str[12].str.replace(",", "")
mydata['merchant_id'] = mydata['Description'].str.split(' ').str[14]
mydata['Concat'] = mydata['ASIN'] + mydata['marketplace_id'] + mydata['merchant_id'] + mydata['RequesterIdentity']

mydata = pd.DataFrame(data=mydata, columns=['ShortId','IssueUrl','Title','RequesterIdentity','CreateDate','ASIN','marketplace_id','merchant_id','Concat'])
# print(mydata['Description'])

mydata.to_excel(r"D:\Users\skathir\Downloads\oncall_base.xlsx")

#SQL Access
con = mysql.connector.connect(host="cmtlabs-db-pr.aka.amazon.com", user="pr_reader", password="4w9O658tfVCw",database="price_rejects")
# def sql_query(self):
res = con.cursor()
# sql = "SELECT marketplaceId,merchantId,asin,competitorName,rejectReason,recommendedPrice,rejectTime,rejectedBy,glName,categoryCode,competitorURL,competitorPrice,loadStatus,loadDate FROM price_rejects.price_reject_inflow where date(tableLoadDate) between DATE_SUB(CURDATE(), INTERVAL 1 DAY) and DATE_SUB(CURDATE(), INTERVAL 1 DAY);"
sql = 'SELECT marketplaceId,merchantId,asin,competitorName,rejectReason,recommendedPrice,rejectTime,rejectedBy,glName,categoryCode,competitorURL,competitorPrice,loadStatus,loadDate FROM price_rejects.price_reject_inflow where marketplaceId != 44571  and date(tableLoadDate) between DATE_SUB(CURDATE(), INTERVAL 12 DAY) and DATE_SUB(CURDATE(), INTERVAL 1 DAY);'

res.execute(sql)
result = res.fetchall()
# print(result)
        # Fetaching the SQL data
df_base = pd.DataFrame(data=result, columns=["marketplaceId", "merchantId", "asin", "competitorName", "rejectReason","recommendedPrice", "rejectTime", "rejectedBy", "glName","categoryCode", "competitorURL", 'competitorPrice','loadStatus','loadDate'])

df_base['Concat'] = df_base['asin'] + df_base['marketplaceId'].astype(str) + df_base['merchantId'].astype(str) + df_base['rejectedBy']
print(df_base)
# df_base.to_excel(r"D:\Users\skathir\Downloads\test1_final_output.xlsx")


df = pd.merge(mydata, df_base, on='Concat')
df.to_excel(r"D:\Users\skathir\Downloads\oncall_vs_PR-DB.xlsx")




#Deal ASIN file reading
df1 = pd.concat(pd.read_excel(r"D:\Users\skathir\Downloads\DEAL_ASIN_base.xlsx", sheet_name=None), ignore_index=True)
mydata = pd.merge( df1, df, on= 'asin')
mydata.to_excel(r"D:\Users\skathir\Downloads\oncall_deal_ASIN.xlsx")

# construct Outlook application instance
olApp = win32.Dispatch('Outlook.Application')
olNS = olApp.GetNameSpace('MAPI')

# construct the email item object
mailItem = olApp.CreateItem(0)
mailItem.Subject = 'Automatic mail for Oncall team ticket data attachment.'
mailItem.BodyFormat = 1
mailItem.Body = '''Hi Team,

I have provided Oncall ticket data, which includes ASIN, MKPL, and MerchantID. And oncall vs. PR-DB file, which contains all rejection information, as well as the Deal ASIN file for priority. Please use the attachment for allocation and further analysis, such as repeat rejection finding and bulk closing.  

Regards,
KATHIRESAN S

NOTE :
*** This is an automatically generated email. DO NOT Reply to this mail ***
*** Please contact skathir for queries and issues related to these automated reports ***
'''
mailItem.To = 'pricerejects-team@amazon.com'
# mailItem.To = 'skathir@amazon.com'
mailItem.CC = 'pr-managers@amazon.com;priamp@amazon.com;msasibal@amazon.com;lokel@amazon.com;anitaa@amazon.com;palaniav@amazon.com'

# mailItem.Attachments.Add(os.path.join(os.getcwd(), 'documentSearch_skathir.xlsx'))
# mailItem.Attachments = "D:\Users\skathir\Downloads\documentSearch_skathir.xlsx"
attach = r"D:\Users\skathir\Downloads\oncall_base.xlsx"
attach1 = r"D:\Users\skathir\Downloads\oncall_deal_ASIN.xlsx"
attach2 = r"D:\Users\skathir\Downloads\oncall_vs_PR-DB.xlsx"
mailItem.Attachments.Add(attach)
mailItem.Attachments.Add(attach1)
mailItem.Attachments.Add(attach2)


mailItem.Display()

mailItem.Save()
mailItem.Send()

# File deleting
myfile = (r"D:\\Users\\skathir\\Downloads\documentSearch_skathir.xlsx")
if os.path.isfile(myfile):
    os.remove(myfile)
    print('Successfully deleted')
else:
    # If it fails, inform the user.
    print("Error: %s file not found")

myfile = (r"D:\\Users\\skathir\\Downloads\documentSearch_skathir.csv")
if os.path.isfile(myfile):
    os.remove(myfile)
    print('Successfully deleted')
else:
    # If it fails, inform the user.
    print("Error: %s file not found")

myfile = (r"D:\\Users\\skathir\\Downloads\oncall_deal_ASIN.xlsx")
if os.path.isfile(myfile):
    os.remove(myfile)
    print('Successfully deleted')
else:
    # If it fails, inform the user.
    print("Error: %s file not found")

myfile = (r"D:\\Users\\skathir\\Downloads\oncall_vs_PR-DB.xlsx")
if os.path.isfile(myfile):
    os.remove(myfile)
    print('Successfully deleted')
else:
    # If it fails, inform the user.
    print("Error: %s file not found")

myfile = (r"D:\\Users\\skathir\\Downloads\oncall_base.xlsx")
if os.path.isfile(myfile):
    os.remove(myfile)
    print('Successfully deleted')
else:
    # If it fails, inform the user.
    print("Error: %s file not found")