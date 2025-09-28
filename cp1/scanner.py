import requests
import os
import re
from datetime import datetime
from time import sleep


def main(string):
    tokens = string.split(" ")
    website = tokens[1]
    delim = tokens[2]
    siteID = tokens[3]
    result_time = None

    if(not os.path.isdir("logs")):
        os.mkdir("logs")
        os.chdir("logs")
    else:
        os.chdir("logs")
    
    if(not os.path.isdir(siteID)):
        os.mkdir(siteID)
        os.chdir(siteID)
    else:
        os.chdir(siteID)


    response = requests.get(website)
    text = response.text.splitlines()
    for i in range(len(text)):
        line = text[i]
        if re.search(delim, line):
            now = datetime.now()
            result_time = now.strftime("%Y-%m-%d-%H-%M-%S")

            if i + 1 < len(text):  # check to avoid going out of bounds
                img_tags = re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', text[i+1], re.IGNORECASE)
                filename =  result_time + ".jpg"   # the name to save the image as
                img_response = requests.get(img_tags[0])

                if img_response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                        sleep(1)
                    print(f"Image downloaded and saved as {filename}")
                else:
                    print(f"Failed to download image. Status code: {img_response.status_code}")
            else:
                print("No next line (end of text)")
    if result_time is None:
        return "200 NO"
    else:
        return "200 YES " + tokens[3] + result_time
            

if __name__ == "__main__":
    print("Python script running")
    main()