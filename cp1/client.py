# client.py : Have the a worker server fetch the content and check to see if has our
# advertising ID
#
# Syntax:
#  python3 client.py URL AdID SiteID -port 41000 -server 127.0.0.1 -tries 5 -gap 1
#
# URL is required and is the URL to check
# AdID is the string to look for (must be contiguous)
# SiteID is a string (must be contiguous)
#
# --port   Optionally changes the port from 54000 to a specific value
# --server The IP or hostname of the server, default is localhost
# --tries  The number of times to fetch this site from the server (default is one)
# --gap    The gap between tries (default is 1 second)
#

import argparse
import os
import time
import socket

parsedArgs = argparse.ArgumentParser(description='Python client for confirming ad states')
parsedArgs.add_argument('URL', type=str, help='The URL to access', default='none')
parsedArgs.add_argument('AdID', type=str, help='The search string for our ads', default='none')
parsedArgs.add_argument('SiteID', type=str, help='The site ID to use for logging', default='XXX')
parsedArgs.add_argument('--port', type=int, help='Port for the server', default=54000)
parsedArgs.add_argument('--server', type=str, help='Hostname or IP address of server', default='127.0.0.1')
parsedArgs.add_argument('--tries', type=int, help='Number of times to check the site', default=1)
parsedArgs.add_argument('--gap', type=float, help='Gap between queries (in seconds)', default=1.0)
parsedArgs.add_argument('--showTime', help='Show the time elapsed for each run', action="store_true")
parsedArgs.add_argument('--verbose', help='Enable verbose output', action="store_true")
args = parsedArgs.parse_args()

# Note the current time
beginTime = time.time()

# Tally various results
numTests = 0
numTestsSuccess = 0
numTestsDetected = 0

if(args.verbose):
   print('Iterating over ' + str(args.tries) + ' query / queries to the server')

for theTry in range(args.tries):
   if(args.verbose):
      print('=====================')
      print('. Attempt ' + str(theTry+1) + ' out of ' + str(args.tries))

   # Note the current time
   startTryTime = time.time()

   numTests = numTests + 1

   # Protect the castle from socket errors
   try:

      if(args.verbose):
         print('. Attempting to create the socket')

      # Set up the socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         if(args.verbose):
            print('. Socket created - attempting to connect to ' + str(args.server) + ' on port ' + str(args.port))

         # Connect to the server
         s.connect((args.server, args.port))

         if(args.verbose):
            print('. Connection successful')

         # Construct the string to send
         theRequest = "CHECK " + args.URL + " " + args.AdID + " " + args.SiteID

         if(args.verbose):
            print('. Sending string |' + theRequest + '|')
            print('. String is of length ' + str(len(theRequest)))
         
         # Send the request
         s.send(theRequest.encode('utf-8'))

         if(args.verbose):
            print('. Send successful')


         if(args.verbose):
            print('. Waiting for up to 1024 bytes')

         data = s.recv(1024)

         # Note the completion time
         responseTime = time.time()

         elapsedTime = startTryTime - responseTime

         if (args.showTime):
            print('Receive a response in ' + str(elapsedTime) + ' s')

         print(' Msg Received: ' + str(data.decode()))

         # Wait (if needed) between scan requests
         if theTry + 1 <= args.tries:
            if(args.verbose):
               print('. Sleeping for ' + str(args.gap))

            time.sleep(args.gap)

   except socket.error as e:
      print(f"Socket error: {e}")
      print('Requested Host: ' + str(args.server))
      print('Requested Port: ' + str(args.port))

# Note the overall time and summarize the success / failures
# TBA