import os
import threading
import time

print('█░░░█ █▀▀ █░░ █▀▀ █▀▀█ █▀▄▀█ █▀▀   ▀▀█▀▀ █▀▀█   █▀▀█ █░░█ █▀▀ █░░█ █▀▀█ ▀▀█▀▀')
print('█▄█▄█ █▀▀ █░░ █░░ █░░█ █░▀░█ █▀▀   ░░█░░ █░░█   █░░█ █▄▄█ █░░ █▀▀█ █▄▄█ ░░█░░')
print('░▀░▀░ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀░░░▀ ▀▀▀   ░░▀░░ ▀▀▀▀   █▀▀▀ ▄▄▄█ ▀▀▀ ▀░░▀ ▀░░▀ ░░▀░░')
print('\t\t\t\t\t\t\t\tBy Shivam Singh')

print("{If you want to run on internet  go to  ngrok folder (you have to install ngrok)}")

def main():


    print("\n\t\t\t\t1: Start Server...")
    print("\t\t\t\t2: Start Client to Connect to the server...")
    print("\t\t\t\t3: Exit...\n\n")

    check_user_input = input("Select [1], [2] or [3]: ")

    if check_user_input=='1':

        t1 = threading.Thread(target=os.system,args=("python chat_server.pyw",),daemon=True)
        time.sleep(4)
        os.system("start chat_client.py",)
        t1.start()
        time.sleep(2)


    elif check_user_input=='2':

        os.system('start chat_client.py')
       

    elif check_user_input=='3':

        os.system("taskkill /f /im python.exe >> nul")
       

    else:

        print("Please enter correct option")


if __name__ == '__main__':

    while True:
        
        main()
        
