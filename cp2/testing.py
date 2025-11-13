import argparse
import requests
import numpy
import time

def main(connection):

    d_data = []
    m_data = []
    p_data = []
    
    for i in range(0,15):  
        start = time.perf_counter()  
        d = requests.get("http://129.74.152.143:54079/data")
        end = time.perf_counter()  
        d_data.append(end - start)
        start = time.perf_counter()
        m = requests.get("http://129.74.152.143:54079/dl/stat/mean?m=05&y=2024&dir=downlink&if=wlan0")
        end = time.perf_counter()  
        m_data.append(end - start)
        start = time.perf_counter()
        p = requests.get("http://129.74.152.143:54079/dl/stat/peak?m=05&y=2024&dir=downlink&if=wlan0")
        end = time.perf_counter()  
        p_data.append(end - start)
    
    d_min, d_max,d_median, d_mean, d_std = min(d_data), max(d_data), numpy.median(d_data), numpy.mean(d_data),  numpy.std(d_data)
    m_min, m_max,m_median, m_mean, m_std = min(m_data), max(m_data), numpy.median(m_data), numpy.mean(m_data),  numpy.std(m_data)
    p_min, p_max,p_median, p_mean, p_std = min(p_data), max(p_data), numpy.median(p_data), numpy.mean(p_data),  numpy.std(p_data)

    if connection == "bad":
        with open("bad.txt", "w") as f:
            f.write(f"Data Min:{d_min:.4}\nData Max:{d_max:.4}\nData Median:{d_median:.4}\nData Mean:{d_mean:.4}\nData Standard Deviation:{d_std:.4}\n")
            f.write(f"Mean Min:{m_min:.4}\nMean Max:{m_max:.4}\nMean Median:{m_median:.4}\nMean Mean:{m_mean:.4}\nMean Standard Deviation:{m_std:.4}\n")
            f.write(f"Peak Min:{p_min:.4}\nPeak Max:{p_max:.4}\nPeak Median:{p_median:.4}\nPeak Mean:{p_mean:.4}\nPeak Standard Deviation:{p_std:.4}\n")
    elif connection == "good":
        with open("good.txt", "w") as f:
            f.write(f"Data Min:{d_min:.4}\nData Max:{d_max:.4}\nData Median:{d_median:.4}\nData Mean:{d_mean:.4}\nData Standard Deviation:{d_std:.4}\n")
            f.write(f"Mean Min:{m_min:.4}\nMean Max:{m_max:.4}\nMean Median:{m_median:.4}\nMean Mean:{m_mean:.4}\nMean Standard Deviation:{m_std:.4}\n")
            f.write(f"Peak Min:{p_min:.4}\nPeak Max:{p_max:.4}\nPeak Median:{p_median:.4}\nPeak Mean:{p_mean:.4}\nPeak Standard Deviation:{p_std:.4}\n")
    else:
        print("Not a valid connection")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split up the JSON')
    parser.add_argument('Connection', type=str, help='Choose good or bad connection')
    args = parser.parse_args()

    main(args.Connection)