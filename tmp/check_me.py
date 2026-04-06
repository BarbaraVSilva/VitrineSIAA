import requests

TOKEN = "EAARpqF7rfooBRFscEGgvbwIuTz5xsm3kIVmanw5vOpfr5qnL90ZBuWMnPzYXvEa1QWCHidZA5ZAva5VjGEzzs4SM22hjaSwc63CJL8KrveY1I3u90jObcpZBrgbf2AiQklKb6s5sZCi3yZAPCVZAR5VvxyplN8QAAkLg6jOFlyj2fcdVIsWsB564ZAR6OEu6MY9964TIvkFddNdt951qBeoBOVqCXvNwb7iyGMXrrd8ysEw6jILU35JHZCiC2SNS77IvLIgIFsp4sfyaorcrpFoUz"

def check_me():
    url = f"https://graph.facebook.com/v20.0/me?fields=name,id&access_token={TOKEN}"
    res = requests.get(url).json()
    print(f"Me: {res}")
    
    url_accounts = f"https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}"
    res_accounts = requests.get(url_accounts).json()
    print(f"Accounts: {res_accounts}")

if __name__ == "__main__":
    check_me()
