import sys
import socket
import getopt
import threading
import subprocess
from pyfiglet import Figlet
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    # Create ASCII art title
    fig = Figlet(font='slant')
    print(fig.renderText('notcat v1.0'))
    print("Created by @nicoleman0")
    print("=" * 50)
    print()
    print("Usage: notcat.py -t target_host -p port")
    print()
    print("-l   --listen - listen on [host]:[port] for incoming connections")
    print("-e   --execute=file_to_run - execute the given file upon receiving a connection")
    print("-c   --command - initialize a command shell")
    print(
        "-u   --upload=destination - upon receiving connection upload a file and write to [destination]")
    print()
    print("Examples:\nnotcat.py -t 192.168.0.1 -p 5555 -l -c\nnotcat.py - t 192.168.0.1 - p 5555 - l - e='cat /etc/passwd'")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", [
                                   "help", "listen", "execute=", "target", "port", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # send data down the socket
        client_sender(buffer)

    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())

        while True:
            # wait for data to be sent back
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break
            print(response)

            # wait for more input
            buffer = input("")
            buffer += "\n"
            # send it off
            client.send(buffer.encode())
    except Exception as e:
        print("[*] Exception! Exiting.")
        print(e)

        client.close()


def server_loop():
    global target
    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # spin off a thread to handle our new client
        client_thread = threading.Thread(
            target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(cmd):
    # trim the newline
    cmd = cmd.rstrip()
    # run the command and get the output back
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        return output
    except:
        return "Failed to execute command.\r\n".encode()


def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):
        # read in all of the bytes and write to our destination
        file_buffer = b""

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that we wrote the file out
            client_socket.send(
                f"Successfully saved file to {upload_destination}\r\n".encode())
        except:
            client_socket.send(
                f"Failed to save file to {upload_destination}\r\n".encode())

    # check to see if we have a command to execute
    if len(execute):
        # run the command
        output = run_command(execute)
        client_socket.send(output)

    # if a command shell was requested
    if command:
        while True:
            # simple prompt
            client_socket.send(b"<notcat:#> ")
            # now we receive until we see a linefeed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            # send back command output
            response = run_command(cmd_buffer)

            # send back response
            client_socket.send(response)


main()
