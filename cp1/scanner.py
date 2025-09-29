import requests
import socket
import os
import re
import sys
from datetime import datetime
from time import sleep


def main():
    tokens = sys.argv[1].split(" ")
    website = tokens[1]
    delim = tokens[2]
    siteID = tokens[3]
    new_fd = socket.socket(fileno=int(sys.argv[2])) #reuse socket from server
    dir = sys.argv[3]
    result_time = None

    #create dir if it doesn't exist 
    if(not os.path.isdir(dir)):
        os.mkdir(dir)
        os.chdir(dir)
    else:
        os.chdir(dir)
    
    #create siteID dir if it doesn't exist
    if(not os.path.isdir(siteID)):
        os.mkdir(siteID)
        os.chdir(siteID)
    else:
        os.chdir(siteID)

    #fetch website
    response = requests.get(website)
    text = response.text.splitlines()
    for i in range(len(text)):
        line = text[i]
        if re.search(delim, line):
            now = datetime.now()
            result_time = now.strftime("%Y-%m-%d-%H-%M-%S")

            if i + 1 < len(text):  # check to avoid going out of bounds

                #get image url from next line
                img_tags = re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', text[i+1], re.IGNORECASE)
                filename =  result_time + ".jpg"   
                img_response = requests.get(img_tags[0])

                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                        sleep(1) #wait for unique timestamp
                    print(f"Image downloaded and saved as {filename}")
                else:
                    print(f"Failed to download image. Status code: {img_response.status_code}")
            else:
                print("No next line (end of text)")

    #send results to clients            
    if result_time is None:
        message = "200 NO"
        new_fd.sendall(message.encode())
    else:
        message = "200 YES " + tokens[3] + " " + result_time
        print
        new_fd.sendall(message.encode())
    return 0
            

if __name__ == "__main__":
    print("Python script running")
    main()