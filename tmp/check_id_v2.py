import requests

TOKEN = "EAARpqF7rfooBRFscEGgvbwIuTz5xsm3kIVmanw5vOpfr5qnL90ZBuWMnPzYXvEa1QWCHidZA5ZAva5VjGEzzs4SM22hjaSwc63CJL8KrveY1I3u90jObcpZBrgbf2AiQklKb6s5sZCi3yZAPCVZAR5VvxyplN8QAAkLg6jOFlyj2fcdVIsWsB564ZAR6OEu6MY9964TIvkFddNdt951qBeoBOVqCXvNwb7iyGMXrrd8ysEw6jILU35JHZCiC2SNS77IvLIgIFsp4sfyaorcrpFoUz"

def check_id():
    # Tenta descobrir o que é esse ID
    id_to_check = "17841440746815302"
    url = f"https://graph.facebook.com/v20.0/{id_to_check}?fields=name,username,metadata{{type}}&access_token={TOKEN}"
    res = requests.get(url).json()
    print(f"Resultado para {id_to_check}: {res}")

if __name__ == "__main__":
    check_id()
