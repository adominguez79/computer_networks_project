
/*NOTES: Ports from 54000 to 54150 on http://ns-mn1.cse.nd.edu/cse30264/ads/file1.html*/


#include </usr/include/python3.12/Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>




int check_message(char* clientMsg, int client_socket);
void sigchld_handler(int s);
void *get_in_addr(struct sockaddr *sa);

int main(int argc, char const* argv[])
{
    if (argc < 3){
        fprintf(stderr, "Usage: %s PORT DIRECTORY\n", argv[0]);
        return EXIT_FAILURE;
    }

    int tmp = atoi(argv[1]);

    if (tmp < 54000 || tmp > 54150){
        fprintf(stderr, "Port %d is out of range. Must be between 54000-54150.\n", tmp);
        return EXIT_FAILURE;
    }

    char port[sizeof(argv[1])];
    int sockfd, new_fd;
	struct addrinfo hints, *servinfo, *p;
	struct sockaddr_storage their_addr; // connector's address info
	socklen_t sin_size;
	struct sigaction sa;
	int yes=1;
	char s[INET6_ADDRSTRLEN];
	int rv;
    char clientMsg[255]; // string to store data from client
    strcpy(port, argv[1]);


    memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE; // use my IP


    // Retrieve the address information pointer to browse what choices might be
    //  available
    if ((rv = getaddrinfo(NULL, port, &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
    }

    // bind socket to the specified IP and port
    for(p = servinfo; p != NULL; p = p->ai_next) {
        
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) {
            perror("server: socket");
            continue;
        }

        if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes,
				sizeof(int)) == -1) {
			perror("setsockopt");
			exit(1);
		}

		if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
			close(sockfd);
			perror("server: bind");
			continue;
		}

		break;
	}

    freeaddrinfo(servinfo); // all done with this structure

    if (p == NULL)  {
		fprintf(stderr, "server: failed to bind\n");
		exit(1);
	}

    //listen for connections
    printf("Listening for connections...\n");
	if (listen(sockfd, 1) == -1) {
		perror("listen");
		exit(1);
	}

	sa.sa_handler = sigchld_handler; // reap all dead processes
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = SA_RESTART;
	if (sigaction(SIGCHLD, &sa, NULL) == -1) {
		perror("sigaction");
		exit(1);

	}


    // integer to hold client socket.
     printf("server: waiting for connections...\n");

	while(1) {  // main accept() loop
		sin_size = sizeof their_addr;
		new_fd = accept(sockfd, (struct sockaddr *)&their_addr,&sin_size);
		if (new_fd == -1) {
			perror("accept");
			continue;
		}

        inet_ntop(their_addr.ss_family,
		get_in_addr((struct sockaddr *)&their_addr), s, sizeof s);
		printf("server: got connection from %s\n", s);

        if (!fork()) { // this is the child process
			close(sockfd); // child doesn't need the listener
            if (recv(new_fd,clientMsg, sizeof(clientMsg), 0) == -1) perror("rcecv");
            printf("Message from client: %s\n", clientMsg);
            
            int result = check_message(clientMsg, new_fd);
            if (result == 200){
                printf("Valid message\n");
                if (Py_IsInitialized()) {
                printf("Python interpreter initialized successfully.\n");}

                PyObject *name, *load_module,*func,*callfunc, *args;

                name = PyUnicode_FromString("scanner" );  
                load_module = PyImport_Import(name); 
                Py_DECREF(name);

                func = PyObject_GetAttrString(load_module,(char *)"main");
                PyObject *arg0 = PyUnicode_FromString(clientMsg);
                args = PyTuple_Pack(1, arg0);
                Py_DECREF(arg0);

                callfunc = PyObject_CallObject(func,args);
                const char *pyfunc = PyUnicode_AsUTF8(callfunc);
                
                Py_DECREF(callfunc);
                Py_DECREF(args);
                Py_DECREF(func);
                Py_DECREF(load_module);
                Py_Finalize();

                send(new_fd, pyfunc, sizeof(pyfunc), 0);  // send to the client
            } else {
                printf("Invalid message\n");
                exit(0);
            }
            

			// if (send(new_fd, "Hello, world!", 13, 0) == -1) perror("send");
			close(new_fd);
			exit(0);
		}

		close(new_fd);  // parent doesn't need this
    }

    return 0;
}

void sigchld_handler(int s)
{
	(void)s; // quiet unused variable warning

	// waitpid() might overwrite errno, so we save and restore it:
	int saved_errno = errno;

	while(waitpid(-1, NULL, WNOHANG) > 0);

	errno = saved_errno;
}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa){
	if (sa->sa_family == AF_INET) {
		return &(((struct sockaddr_in*)sa)->sin_addr);
	}

	return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int check_message(char* message, int client_socket) {
    char errMsg[255] = "400 ERROR: Incorrect number of arguments.\n";     
    
    char *copy = strdup(message);
    if (copy == NULL){
        send(client_socket, errMsg, sizeof(errMsg), 0);
        return 400;
    }

    int count = 0;
    char *tok = strtok(copy, " ");
    if (strcmp(tok,"CHECK")){
        strcpy(errMsg, "404 ERROR: First argument must be CHECK.\n");
        send(client_socket, errMsg, sizeof(errMsg), 0);
        return 400;
    }
    while (tok != NULL) {
        count++;
        printf("Token %d: %s\n", count, tok);
        tok = strtok(NULL, " ");
    }

    if (count == 0 || count > 4){ 
        send(client_socket, errMsg, sizeof(errMsg), 0);
        return 400;
    }
    return 200;
}