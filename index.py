import telebot
import os
from dotenv import load_dotenv
import json
import requests
import time

load_dotenv()
token = os.getenv('token')
bot = telebot.TeleBot(token)
running = False

def main():

        @bot.message_handler(commands=['start', 'hello'])
        def send_welcome(message):
            bot.reply_to(message, "Howdy, how are you 😊?")
            bot.reply_to(message,'''
/pre_open : Pre Opening details of BankNifty and Nifty
/current  : Gives current Price
/stop     : Stop the Loop
            ''')
            bot.reply_to(message,'''
current parameter required:
/current Symbol(e.g BANKNIFTY) Expiry Date(21-Jun-2023) Strike Price(e.g 43500) Option(CE/PE)  
            ''')

        @bot.message_handler(commands=['pre_open'])
        def pre_opening(message):
            baseurl = "https://www.nseindia.com/"
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            url2 = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
            headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'}


            session = requests.Session()
            request = session.get(baseurl, headers=headers, timeout=10)
            cookies = dict(request.cookies)
            response = session.get(url, headers=headers, timeout=10, cookies=cookies)
            response2=session.get(url2,headers=headers,timeout=10,cookies=cookies)


            print(response)
            print(response2)


            response_text=response.text
            response2_text=response2.text
        

            nifty_object = json.loads(response_text)
            banknifty_object = json.loads(response2_text)


            open_nifty = nifty_object['data'][0]['open']
            nifty_change= nifty_object['data'][0]['change']


            open_banknifty=banknifty_object['data'][0]['open']
            banknifty_change= banknifty_object['data'][0]['change']
           

            print(f'''
Market Open Update
Nifty50 open at {open_nifty} ({round(nifty_change,2)})
Banknifty open at {open_banknifty} ({round(banknifty_change,2)})
            ''')
            if(nifty_change > 0 or banknifty_change  > 0):
                 x = "Positive Opening"
               
            else:
                 x="Negative Opening"
               
            

            bot.reply_to(message,f'''
Market Open Update
Nifty50 open at {open_nifty} ({round(nifty_change,2)})
Banknifty open at {open_banknifty} ({round(banknifty_change,2)})
{x}
            ''')
          


            session.close()
     
        @bot.message_handler(commands=['stop'])
        def stop_loop(message):
            chat_id=message.chat.id
            stop = message.text
            global running
            if running :
                 running = False
            

            return stop
        

        @bot.message_handler(commands=['current'])
        def get_data(message):
             msg = bot.reply_to(message,"What is the Symbol:")
             bot.register_next_step_handler(msg,get_symbol)

        def get_symbol(message):
             chat_id = message.chat.id
             symbol=message.text
             msg=bot.reply_to(message,"What are the option")
             bot.register_next_step_handler(msg,get_option,symbol)

        def get_option(message,symbol):
            chat_id=message.chat.id
            option = message.text
            
            msg=bot.reply_to(message,"What is the Strike Price:")
            bot.register_next_step_handler(msg,get_expiry,symbol,option)
        
        def get_expiry(message,symbol,option):
             
             chat_id= message.chat.id
             strike_price = message.text
             msg=bot.reply_to(message,"The Expiry Date:")
             bot.register_next_step_handler(msg,current,symbol,option,strike_price)

        def current(message,symbol,option,strike):
                
                chat_id = message.chat.id
                expiry_date = message.text
                strike_price= int(strike)
                stop = stop_loop(message)
                print(stop)
                if(stop == "/stop"):
                    key = False
                    print("Stop worked")
                else:
                     key = True
                global running
                running=True
                
              
             
                while running:
                
                    baseurl = "https://www.nseindia.com/"
                    url=f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
                    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'}

                    session = requests.Session()
                    request = session.get(baseurl, headers=headers, timeout=10)
                    cookies = dict(request.cookies)

                    response = session.get(url, headers=headers, timeout=10, cookies=cookies)
                    print(response)
                    response_text=response.text
                    json_object=json.loads(response_text)
                    data = json_object['records']['data']
                    for i in range(0,len(data)): 
                        if (data[i]["strikePrice"] == strike_price and data[i]["expiryDate"] == expiry_date) :
                            if option == "CE":
                                print(data[i]["CE"]["askPrice"])
                                bot.reply_to(message,data[i]["CE"]["askPrice"])
                                time.sleep(10)
                               
                            else:
                                print(data[i]["PE"]["askPrice"])
                                bot.reply_to(message,data[i]["PE"]["askPrice"])
                                time.sleep(10)
                    
                    session.close()

        bot.infinity_polling()

main()


