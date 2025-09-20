
/*NOTES: Ports from 54000 to 54150 on http://ns-mn1.cse.nd.edu/cse30264/ads/file1.html*/



#include <netinet/in.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h> 
#include <sys/types.h>
#include <sys/wait.h>

int check_message(char* clientMsg, int client_socket);


int main(int argc, char const* argv[])
{
    if (argc < 3){
        fprintf(stderr, "Usage: %s PORT DIRECTORY\n", argv[0]);
        return EXIT_FAILURE;
    }

    int port = atoi(argv[1]);

    if (port < 54000 || port > 54150){
        fprintf(stderr, "Port %d is out of range. Must be between 54000-54150.\n", port);
        return EXIT_FAILURE;
    }

    FILE* fptr;
    fptr = fopen(argv[2], "a");

    if (fptr == NULL) {
        fprintf(stderr, "Could not access file");
        return EXIT_FAILURE;
    }

    int servSockD = socket(AF_INET, SOCK_STREAM, 0); // socket descriptor for server
    if(servSockD == -1) {
        perror("socket");
        return -1;
    }
    char serMsg[255] = "Message from the server to the client \'Hello Client\' ";// string store data to send to client
    char clientMsg[255]; // string to store data from client
    struct sockaddr_in servAddr; // define server address

    servAddr.sin_family = AF_INET;
    servAddr.sin_port = htons(port);
    servAddr.sin_addr.s_addr = INADDR_ANY;

    // bind socket to the specified IP and port
    int bindx = bind(servSockD, (struct sockaddr*)&servAddr, sizeof(servAddr));
    if(bindx == -1) {
        perror("bind");
        return -1;
    }

    // listen for connections
    listen(servSockD, 1);
    printf("Listening for connections...\n");

    // integer to hold client socket.
     for(;;) {
        int client_socket = accept(servSockD, NULL, NULL);
        printf("Client connected\n");
        recv(client_socket, clientMsg, sizeof(clientMsg), 0);
        char* token = strtok(clientMsg," ");
        if (check_message(token, client_socket) == 200) {     
        }
    }

    return 0;
}
int check_message(char* tokens, int client_socket) {
    char errMsg[255] = "400 ERROR: Incorrect number of arguments.\n"; 
    
    char *copy = strdup(tokens);
    if (copy == NULL) return 500;

    int count = 0;
    char *tok = strtok(copy, " \t\r\n");
    while (tok != NULL) {
        count++;
        tok = strtok(NULL, " \t\r\n");
    }

    free(copy);

    if (count == 0 || count > 3){ 
        send(client_socket, errMsg, sizeof(errMsg), 0);
        return 400;
    }
    return 200;
}