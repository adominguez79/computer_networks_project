import requests
import socket
import os
import re
import sys
from datetime import datetime
from time import sleep


def main(identifier, website, siteID, sockfd, delim):
    result_time = None
    hits = []
    #create dir if it doesn't exist 
    try:
        os.chdir(siteID)
    except FileNotFoundError:
        os.mkdir(siteID)
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
                hits.append((identifier, website,siteID, delim, result_time))
                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                        sleep(1) #wait for unique timestamp
                    print(f"[{identifier}] Image downloaded and saved as {filename}")
                else:
                    print(f"[{identifier}] Failed to download image. Status code: {img_response.status_code}")
            else:
                print("No next line (end of text)")

    #send results to clients            
    if result_time is None:
        return None
    else:
        return result_time

            

if __name__ == "__main__":
    tokens = sys.argv[1].split(" ")
    website = tokens[1]
    delim = tokens[2]
    siteID = tokens[3]
    new_fd = socket.socket(fileno=int(sys.argv[2])) #reuse socket from server
    dir = sys.argv[3]
    main()