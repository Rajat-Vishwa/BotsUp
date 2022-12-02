import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import sys, os, threading
import mysql.connector
from cryptography.fernet import Fernet

from selenium import webdriver
import urllib
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoSuchWindowException
import time, json

LOG_PATH = "invalid.txt"
timeout = 20
msg_sent = 0
alive = True
webdriver_running = False

try:
    config_file = open('config.json', 'r+')
    config  = json.load(config_file)
    server_creds = config['Database'][0]
    webpage_data = config['WebPage'][0]
    key = b'VH5wkUrclI6AUkzm4-FuPPdRwsJC2vl1Obyz02BrFbQ='
    fernet = Fernet(key)
    timeout = config['timeout']
except Exception as e:
    messagebox.showerror("Error", f"Error reading config..\n{e}")
    sys.exit()

def update_json(object):
    config_file.seek(0)
    json.dump(object, config_file, indent=4, separators=(", ", ": "), sort_keys=True)
    config_file.truncate()

def decrypt(val):
    dcryp = fernet.decrypt(val.encode())
    return dcryp.decode()



def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def element_presence(by, xpath, time):
    element_present = EC.presence_of_element_located((By.XPATH, xpath))
    WebDriverWait(driver, time).until(element_present)

def send_message(url,index):
    ANCHOR_XPATH = webpage_data['ANCHOR_XPATH']
    INVALID_XPATH = webpage_data['INVALID_XPATH']
    MSGBOX_XPATH = webpage_data['MSGBOX_XPATH']
    SPAN_XPATH = webpage_data['SPAN_XPATH']
    IMGBOX_XPATH = webpage_data['IMGBOX_XPATH']
    SEND_XPATH = webpage_data['SEND_XPATH']

    driver.get(url)
    time.sleep(delay_parameter/2)

    info_text.config(text="Loading...")
    element_presence(By.XPATH, ANCHOR_XPATH, timeout)
    time.sleep(delay_parameter)

    info_text.config(text="Checking for invalidity...")
    print("Checking for invalidity")

    if check_exists_by_xpath(INVALID_XPATH):
        print(str(index) + " --> " + str(data[index]))
        log.write(str(data[index]) + '\n')
        info_text.config(text=f"Number {str(data[index])} is invalid!")
        return

    print("Finding msg box")
    info_text.config(text="Finding message box...")
    element_presence(By.XPATH, MSGBOX_XPATH, timeout)
    msg_box = driver.find_element(By.XPATH, MSGBOX_XPATH)
    msg_box.send_keys('\n')

    time.sleep(delay_parameter/4)
    info_text.config(text="Sending attachments...")
    span = driver.find_element(By.XPATH, SPAN_XPATH)
    span.click()
    
    time.sleep(delay_parameter/4)
    img_box = driver.find_element(By.XPATH, IMGBOX_XPATH)
    try:
        img_box.send_keys(IMG_PATH)
        element_presence(By.XPATH, SEND_XPATH, timeout)
        send_button = driver.find_element(By.XPATH, SEND_XPATH)
        send_button.click()
    except:
        pass
    info_text.config(text="Message sent!")
    time.sleep(delay_parameter/2)


def prepare_msg(data, _msg, _from_index):
    base_msg = _msg
    base_url = 'https://web.whatsapp.com/send?phone={}&text={}'
    for i in range(_from_index,len(data)) :
        phone_no = '91' + str(data[i])
        message = urllib.parse.quote(base_msg)
        url_msg = base_url.format(phone_no, message)
        info_text.config(text=f"Sending message to {data[i]}..")
        send_message(url_msg,i)
        from_index_entry.delete(0, tk.END)
        print("Updating index")
        from_index_entry.insert(0,str(i+1))
        #win.update()
        time.sleep(delay_parameter)

###############################################################################

def start_driver():
    global log, alive, webdriver_running
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir-Session")
    chrome_options.add_argument("--profile-directory=Default")
    global driver
    driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
    alive = True
    webdriver_running = True
    log = open(LOG_PATH, 'a+')
    info_text.config(text="Webdriver running")
    

def start_bot():
    if not webdriver_running:
        start_driver()

    global delay_parameter, msg_sent, from_index
    delay_parameter = int(delay_entry.get())
    from_index = int(from_index_entry.get())
    msg_sent = 0
    if not alive:
        return
    try:
        prepare_msg(data, msg, from_index)
        messagebox.showinfo("Done!",  "Your messages were sent.")
        check_connection()
    except NameError or ValueError as e:
        messagebox.showerror("Error!",  f"Please select data files.\n\n{str(e)}")
        print(e)    
    except TimeoutException:
        info_text.config(text="Timeout!")
        if alive:
            start_bot()
        else:
            info_text.config(text="Ideal")
    except NoSuchWindowException as e:
        popup = tk.Toplevel()
        popup.title("Error!")
        print(e)
        tk.Message(popup, text=str(e)+"\n\n Aborting the process in 5 seconds...").pack()
        info_text.config(text="Exception occured..")
        popup.update()
        time.sleep(5)
        popup.destroy()
        abort()
        check_connection()
    except Exception as e:
        try:
            exp_name  = ' '.join(e.msg.split()[0:3])
        except:
            exp_name = " "
        print(exp_name)
        if exp_name == "chrome not reachable":
            popup = tk.Toplevel()
            popup.title("Error!")
            print(e)
            tk.Message(popup, text=str(e)+"\n\n Aborting the process in 5 seconds...").pack()
            info_text.config(text="Exception occured..")
            popup.update()
            time.sleep(5)
            popup.destroy()
            abort()
            check_connection()
        else:
            popup = tk.Toplevel()
            popup.title("Error!")
            print(e)
            tk.Message(popup, text=str(e)+"\n\n Restarting in 5 seconds...").pack()
            info_text.config(text="Exception occured..")
            popup.update()
            time.sleep(5)
            popup.destroy()
            if alive:
                start_bot()
            else:
                info_text.config(text="Ideal")
                

def start_thread():
    global thread, alive
    alive = True
    thread = threading.Thread(target=start_bot)
    thread.daemon = True
    thread.start()

def abort():
    info_text.config(text="Aborting the process..", fg='blue')
    global alive, webdriver_running
    alive = False
    try:
        driver.quit()
        webdriver_running = False
    except:
        pass
    info_text.config(text="Process aborted...", fg='blue')
    check_connection()

#############################################################################

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

DRIVER_PATH = resource_path('./driver/chromedriver.exe')
#DRIVER_PATH = 'chromedriver.exe'

def set_log_path():
    global LOG_PATH
    LOG_PATH = filedialog.askopenfilename()

def read_msg():
    global msg
    msg_path = filedialog.askopenfilename()
    try:
        msg = open(msg_path).read()
        msg_label.config(text='Msg File : '+ msg_path, fg='green')
        win.update()
    except Exception as e:
        messagebox.showerror("Error!",  e)

def set_data():
    global data
    data = []
    data_path = filedialog.askopenfilename(filetypes=(("xlsx", "*.xlsx"),("xls", "*.xls")))
    try:
        df = pd.read_excel(data_path, header=None)
        df.fillna(0,inplace=True)
        excel_data = df.values.tolist()
        print(excel_data)
        for row in excel_data:
            for dt in row:
                if dt != 0:
                    try:
                        data.append(str(int(dt)))
                    except:
                        pass
        data_label.config(text='Data File : '+ data_path, fg='green')
        print(data)
        win.update()
    except Exception as e:
        messagebox.showerror("Error!",  e)

def set_img():
    global IMG_PATH 
    IMG_PATH_TUP = filedialog.askopenfilenames(filetypes=(("JPG", "*.jpg"),("PNG", "*.png")))
    IMG_PATH = '\n'.join(IMG_PATH_TUP)
    img_label.config(text='Image : '+ IMG_PATH, fg='green')
    win.update()

##########################################################################################

win = tk.Tk()
win.title("BotsUp")
win.geometry("600x600")
win.minsize(600,600)

Header = tk.Frame(win)

head_label = tk.Label(text=" ",font=("Arial Bold",25), fg='green')
head_label.pack()


ButtonFrame = tk.Frame(win)
text_size = 20
msg_open = tk.Button(ButtonFrame, text="Select Message Txt File",command=lambda:read_msg(), bg='#e91f23', font=('Arial Bold',text_size))
msg_open.pack(pady=2)

data_open = tk.Button(ButtonFrame, text="Select Excel Sheet", bg='#06a355',command=lambda:set_data(),  font=('Arial Bold',text_size))
data_open.pack(pady=2)

img_open = tk.Button(ButtonFrame, text="Select Image", bg='#6b8bca',command=lambda:set_img(),  font=('Arial Bold',text_size))
img_open.pack(pady=2)

set_log_button = tk.Button(ButtonFrame, text="Inv Log", bg='#facb13',command=lambda:set_log_path(),  font=('Arial Bold',text_size))
set_log_button.pack(pady=2)

send_button = tk.Button(ButtonFrame, text="Send!", bg='#a5aac9',command=lambda:start_thread(),  font=('Arial Bold',text_size))
send_button.pack(pady=2)


InputFieldFrame = tk.Frame(win)

tk.Label(InputFieldFrame, text="Index : ").grid(row=0,column=0)
from_index_entry = tk.Entry(InputFieldFrame, width=5)
from_index_entry.insert(0,'0')
from_index_entry.grid(row=0,column=1)

tk.Label(InputFieldFrame, text="Delay Parameter : ").grid(row=1,column=0)
delay_entry = tk.Entry(InputFieldFrame, width=5)
delay_entry.insert(0,'4')
delay_entry.grid(row=1,column=1)


InfoFrame = tk.Frame(win)

msg_label = tk.Label(InfoFrame, text='Msg File not selected!', justify='left', fg='red')
msg_label.pack(pady=1)
data_label = tk.Label(InfoFrame, text='Data File not selected!', justify='left', fg='red')
data_label.pack(pady=1)
img_label = tk.Label(InfoFrame, text='Image not selected!', justify='left', fg='red')
img_label.pack(pady=1)
info_text = tk.Label(InfoFrame, text="Ideal", fg='blue')
info_text.pack()

Footer = tk.Frame(win)
watermark = tk.Label(Footer, text="@rajat_vishwa", font=("Arial Bold", 8))
watermark.pack(side='left')

abort_button = tk.Button(Footer, text="Abort!",command=lambda:abort(), font=("Arial", 8), fg='red')
abort_button.pack(side='right')

Header.pack(side='top', pady=10)
ButtonFrame.pack(pady=10)
InputFieldFrame.pack(pady=10)
InfoFrame.pack(pady=10)
Footer.pack(side='bottom', fill='x')

def quit_protocol():
    info_text.config(text='Checking connection...')
    check_connection()
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        try:
            if webdriver_running:
                info_text.config(text="Closing webdriver...", fg='blue')
                top.destroy()
                abort()
                info_text.config(text="Webdriver closed.")
            else:
                pass
        except:
            pass
        try:
            if LoggedIn:
                if not online:
                    info_text.config(text='Trying to connect...')
                    connect_server()
                info_text.config(text='Updating database...')
                query= f"UPDATE Login SET Status='0' WHERE Username='{username}'"
                cursor.execute(query)
                database.commit()
                config['WasServerUpdated'] = 'true'
                update_json(config)
                cursor.close()
                database.disconnect()
                info_text.config(text="Server disconnected.")
                print("Server disconnected.")
                
        except:
            info_text.config(text='Connection failed...')
            #prompt = f"Connection to server failed!.\nPlease send the following error code to admin.\n{''}"
            #messagebox.showerror("Connection error!", prompt)
            config['WasServerUpdated'] = 'false'
            update_json(config)
            
        win.destroy()
        sys.exit()

def on_closing():
    thread = threading.Thread(target=quit_protocol)
    thread.daemon = True
    thread.start()

win.protocol("WM_DELETE_WINDOW", on_closing)


##############################################################################################

LoggedIn = False
online = False

def connect_server():
    try:
        global database, cursor, online
        print("Connecting to mysql server...")
        print('host : ',decrypt(server_creds['host']))
        print('user : ',decrypt(server_creds['user']))
        print('database : ',decrypt(server_creds['database']))
        #print('password : ',decrypt(server_creds['password']))
        LoginFooter.config(text='Connecting...', fg='blue')
        database = mysql.connector.connect(
        host= decrypt(server_creds['host']),
        user= decrypt(server_creds['user']),
        password= decrypt(server_creds['password']),
        database= decrypt(server_creds['database'])
        )
        cursor = database.cursor()
        online = True
        LoginFooter.config(text='Online', fg='green')
        info_text.config(text='Online', fg='green')
        print("Connection Successful")
    except Exception as e:
        LoginFooter.config(text='Offline', fg='red')
        info_text.config(text='Offline', fg='green')
        prompt = "Can't connect to the server.\nPlease check your internet connection.\n" + str(e)
        messagebox.showerror("Error!", prompt)
        online = False

def check_connection():
    global online
    try:
        info_text.config(text="Checking connection...", fg='gray')
        if not database.is_connected():
            online = False
            info_text.config(text="Server Offline", fg='red')
        else:
            online = True
            info_text.config(text="Online", fg='green')
    except:
        pass

def Login(_username, _password):
    if not online:
        connect_server()
    try:
        LoginFooter.config(text='Checking connection...', fg='blue')

        if not database.is_connected() and online:
            print("Connection lost!")
            connect_server()
            return

        LoginFooter.config(text='Logging in...', fg='green')

        query = f"SELECT Username FROM Login WHERE Username='{_username}' AND Password='{_password}'"
        print(query)
        cursor.execute(query)
        if not cursor.fetchone(): 
            print("Login failed")
            messagebox.showerror("Error!", "Invalid username or password. \nPlease try again.")
            LoginFooter.config(text='Online', fg='green')
        else:
            query = f"SELECT Status FROM Login WHERE Username='{_username}'"
            cursor.execute(query)
            status = cursor.fetchall()[0][0]
            if status == 0 or config['WasServerUpdated'] == 'false':
                print("Login Successful")
                global LoggedIn
                LoggedIn = True
                query = f"UPDATE Login SET Status='1' WHERE Username='{username}'"
                cursor.execute(query)
                database.commit()
                win.deiconify()
                top.destroy()
                head_label.config(text=f"Welcome {username}")
            else:
                print("Another Session is already running.")
                LoginFooter.config(text='Online', fg='green')
                messagebox.showerror("Error!", "Another Session is already running.")
                LoggedIn = False
    except Exception as e:
        print(e)
        pass        


top = tk.Toplevel()
top.title("BotsUp Login")
top.geometry("400x200")
top.minsize(400,200)

LoginEntryFrame = tk.Frame(top)
tk.Label(LoginEntryFrame, text="Username : ", fg='blue', font=("Arial Bold",10)).grid(row=0,column=0, pady=2)
tk.Label(LoginEntryFrame, text="Password : ", fg='blue', font=("Arial Bold",10)).grid(row=1,column=0)
entry1 = tk.Entry(LoginEntryFrame, width=40, font=("Arial Bold",10))
entry1.grid(row=0,column=1)
entry2 = tk.Entry(LoginEntryFrame, show='x',width=40, font=("Arial Bold",10))
entry2.grid(row=1,column=1)

LoginButtonFrame = tk.Frame(top)
button1 = tk.Button(LoginButtonFrame, text="Login", command=lambda:command1(), bg='#06a355')
button1.pack(pady=2)
button2 = tk.Button(LoginButtonFrame, text="Cancel", command=lambda:command2(), bg='#e91f23')
button2.pack()

def command1():
    global username, password
    username = entry1.get() 
    password = entry2.get()
    thread = threading.Thread(target = lambda:Login(username, password))
    thread.daemon = True
    thread.start()

def command2():
    on_closing()

tk.Label(top, text="Please login to continue...", font=("Arial Bold", 15), fg='gray').pack(pady=(1,1))
LoginEntryFrame.pack(anchor='center', pady=(10,20))
LoginButtonFrame.pack(anchor='center')
top.protocol("WM_DELETE_WINDOW", on_closing)
LoginFooter = tk.Label(top, text=" ")
LoginFooter.pack(side='bottom')

win.withdraw()
threading.Thread(target=connect_server).start()
win.mainloop()
