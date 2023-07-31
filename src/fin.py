from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import threading
global numupdated
numupdated = 0

ratte = "" # Enter the "rat" cookie from the Sea of Thieves website here. Use Cookie Editor by cgagnier for example.
sheet_id = "" # The ID of your Google spreadsheet, found in the URL 
path_to_credentials = "" # The path to the credentials the Google API provides. Should end in \credentials.json

def firstauth():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path_to_credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

def update_values(spreadsheet_id, range_name, value_input_option,
                  values, fishies):

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path_to_credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # pylint: disable=maybe-no-member
    try:

        service = build('sheets', 'v4', credentials=creds)

        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells of {fishies.capitalize()} updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error} while handling {fishies.capitalize()}")
        return error
    
def getsauce(fishies, bonus):
    try:

        cookies = {
            'rat': ratte
        }

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

        # Set up the WebDriver with headers and cookies
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run the browser in headless mode (without UI)

        for header, value in headers.items():
            chrome_options.add_argument(f"--header={header}: {value}")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)  # Replace "Chrome" with the appropriate driver for your browser
        
        url = f"https://www.seaofthieves.com/profile/reputation/HuntersCall/{fishies}"  # Replace with the URL of your target website
        driver.get(url)

        # Add cookies to the WebDriver
        for cookie_name, cookie_value in cookies.items():
            driver.add_cookie({"name": cookie_name, "value": cookie_value})

        # Load the website
        driver.get(url)

        # Wait for the dynamic content to load (polling the API)
        time.sleep(5+bonus)  # Wait for 5 seconds (you can change this value as needed)

        # Extract the data from the dynamically loaded page
        page_source = driver.page_source
        # Now you can use a parser like BeautifulSoup to extract the required data from the page_source
        # Close the WebDriver when you're done
        driver.quit()

        sauce = (str(page_source.encode("utf-8")))
        return sauce
    except Exception as e:
        print(f"There was an error while trying to scrape the website for {fishies}.")
        print(e)

def findachievements(src, start, end):
    try:
        if start < 0 or end < 0:
            print("start or end index to low")
            return
        if end < start:
            print("end index before start index")
            return
        result = []
        while src.find("<div class=\"emblem-item__progress-text\">") != -1:
            divindex = src.find("<div class=\"emblem-item__progress-text\">")
            src = src[divindex+40:len(src)]
            result.append(src[:src.find("/")])
        if end > len(result) -1:
            return
        return result[start:end+1]
    except Exception as e:
        print("There was an error while fetching some fishes from the html text.")
        print(e)

if __name__ == '__main__':

    
    if ratte == "":
        print("You forgot to enter the 'ratte' cookie! Code will stop executing")
        exit()
    
    if sheet_id == "":
        print("You forgot to enter the 'sheet_id'! Code will stop executing")
        exit()

    if path_to_credentials == "":
        print("You forgot to enter the path to the Google API credentials! Code will stop executing")
        exit()

    firstauth()
    def getfinlist(fishies, end):
        try:
            global numupdated
            print(f"Updating {fishies.capitalize()}")
            fishcaught = findachievements(getsauce(fishies, 0), 0, end)
        
            if fishcaught == None:
                print(f"Retrying to load the {fishies.capitalize()} with a longer timeout threshold.")
                problem = True
                fishcaught = findachievements(getsauce(fishies, 5), 0, end)
                if (fishcaught == None) and (problem == True):
                    (print(f"The website failed to scrape the {(fishies.capitalize())}. The {fishies.capitalize()} will not be updated."))
                    numupdated += 1
                    exit()
            fishlist = []
            for i in range(len(fishcaught)):
                fishlist.append([fishcaught[i]])
                
            return fishlist 
        except Exception as e:
            print(f"There was an error.")
            print(e)
            exit()

    def updatesplashes():        
        fishlist = getfinlist("splashtails", 4)
        update_values(sheet_id,
                    "B2:B6", "USER_ENTERED",
                    fishlist, "splashtails")
    
    def updatewilds():
        fishlist = getfinlist("wildsplashes", 4)
        update_values(sheet_id,
                    "B8:B12", "USER_ENTERED",
                    fishlist, "wildsplashes")
    
    def updatepondies():
        fishlist = getfinlist("pondies", 4)
        update_values(sheet_id,
                    "B14:B18", "USER_ENTERED",
                    fishlist, "pondies")
    
    def updatewreck():
        fishlist = getfinlist("wreckers", 4)
        update_values(sheet_id,
                    "B20:B24", "USER_ENTERED",
                    fishlist, "wreckers")
    
    def updatecook():
        fishlist = getfinlist("cooking", 5)
        update_values(sheet_id,
                    "B28:B33", "USER_ENTERED",
                    fishlist, "cooking")
    
    def updateplenti():
        fishlist = getfinlist("plentifins", 4)
        update_values(sheet_id,
                    "E2:E6", "USER_ENTERED",
                    fishlist, "plentifins")
    
    def updatedevil():
        fishlist = getfinlist("devilfishes", 4)
        update_values(sheet_id,
                    "E8:E12", "USER_ENTERED",
                    fishlist, "devilfishes")
    
    def updatebattle():
        fishlist = getfinlist("battlegills", 4)
        update_values(sheet_id,
                    "E14:E18", "USER_ENTERED",
                    fishlist, "battlegills")
    
    def updateancient():
        fishlist = getfinlist("ancientscales", 4)
        update_values(sheet_id,
                    "H2:H6", "USER_ENTERED",
                    fishlist, "ancientscales")
    
    def updatehopper():
        fishlist = getfinlist("islehoppers", 4)
        update_values(sheet_id,
                    "H8:H12", "USER_ENTERED",
                    fishlist, "islehoppers")
    
    def updatestorm():
        fishlist = getfinlist("stormfishes", 4)
        update_values(sheet_id,
                    "H14:H18", "USER_ENTERED",
                    fishlist, "stormfishes")
    
    def updateplunder():
        fishlist = getfinlist("merrick's-accolades", 0)
        update_values(sheet_id,
                    "E22", "USER_ENTERED",
                    fishlist, "merrick's-accolades")
    thread = []
    thread.append(threading.Thread(target=updatesplashes))
    thread.append(threading.Thread(target=updatewilds))
    thread.append(threading.Thread(target=updatepondies))
    thread.append(threading.Thread(target=updatewreck))
    thread.append(threading.Thread(target=updatecook))
    thread.append(threading.Thread(target=updateplenti))
    thread.append(threading.Thread(target=updatedevil))
    thread.append(threading.Thread(target=updatebattle))
    thread.append(threading.Thread(target=updateplunder))
    thread.append(threading.Thread(target=updateancient))
    thread.append(threading.Thread(target=updatehopper))
    thread.append(threading.Thread(target=updatestorm))

    i = 0
    for i in range(len(thread)):
        try:
            thread[i].start()
        except Exception as e: 
            print(f"Thread number {i} not started correctly")
            print(e)
        time.sleep(2)

    def ihateglobalvariables():
        global numupdated
        for i in thread:
            i.join()
        if numupdated == len(thread):
            print("Couldn't update any fishes. Your 'ratte' cookie is probably wrong or has expired.")
        elif numupdated == 0:
            print("Everything updated succefully!")
        else:
            print("One or more fishes not updated correctly. Please check.")

    ihateglobalvariables() 
        
    
