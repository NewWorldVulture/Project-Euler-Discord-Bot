from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Nothing interesting here. Just running a bot.\n Check https://repl.it/@Dersyx/Project-Euler-Discord-Bot for the interesting stuff."

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()
