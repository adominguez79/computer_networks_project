# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -Wextra -O2 `python3-config --cflags` 

# Linker flags
LDFLAGS = `python3-config --ldflags` -lpython3.12

# Source and output
SRC = server.c
OUT = server

# Default target
all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -o $(OUT) $(SRC) $(LDFLAGS)

# Clean up compiled files
clean:
	rm -f $(OUT)