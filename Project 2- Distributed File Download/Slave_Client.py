import socket
import threading
import time

# Global variables
server_ip = "10.17.51.115"  
server_port = 9801
max_lines = 1000
lines_received = [0]*max_lines
full_text = [""]*max_lines
lines_count = 0
client_host = '10.184.63.57'  # Replace with master client's IP address
client_port = 10001
done = 0
connect = 0

def connect_fn(c):
    global connect
    while connect == 0:
        try:
            c.connect((client_host, client_port))
            print("Established a connection with master client\n")
            connect = 1
        except:
            continue

def receive_messages(c):
    global done,connect
    while connect ==1:
        try:
            curr = c.recv(1024)
            if curr:
                line = curr.decode().split('\n')
                if line[0] == "DONE":
                    done = 1
                    break
        except:
            continue
    # exception related to connection being broken off handled
    if (connect == 0):
        print("Connection broke off from master")
        connect_fn(c)
        receive_thread = threading.Thread(target=receive_messages, args=(c,))
        receive_thread.start()

def main():
    global done, lines_count,connect
    print("Started connecting with master\n")
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_fn(c)
    receive_thread = threading.Thread(target=receive_messages, args=(c,))
    receive_thread.start()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_time = time.time()
    client_socket.connect((server_ip, server_port))
    print('Established a connection with server\n')
    while True:
        try:
            client_socket.send("SENDLINE\n".encode())
            curr = client_socket.recv(1024)
        except socket.timeout:
                continue
        except:
            print("Connection lost from server")
            client_socket.close()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
        if done == 0 and connect == 1 :
            try:
                c.send(curr)
            except socket.timeout:
                continue
            except:
                connect = 0
        else:
            break
    print("Master received all lines")
    prev = -1
    worthy = 0
    num = ""
    while lines_count < max_lines:  
        curr = b''
        if connect ==1:
            c.settimeout(0.01)
            try:
                curr = c.recv(1024)
            except socket.timeout:
                continue
            except Exception as e:
                connect = 0
            if lines_count == max_lines:
                lines_count +=1
            line = curr.decode()
            line_list = line.split('\n')
            if (len(line_list) >=2):
                i = 0
                while (i<len(line_list)):
                    curr_element = line_list[i]
                    if (curr_element.isdigit()):
                        num = num + curr_element
                        if (int(num) == prev+1):
                            prev = prev +1
                            num = ""
                            lines_count = lines_count +1
                            print(prev)
                            lines_received[prev] = 1
                            if (i != len(line_list) -1):
                                full_text[prev] = line_list[i+1]
                                i += 1
                            worthy = 1
                    elif worthy == 1 and curr_element != "-1":
                        full_text[prev] = full_text[prev] + curr_element  ## Doubt
                    else:
                        worthy = 0  
                    i+=1
            elif (line_list != ['-1'] and worthy == 1):
                full_text[prev] = full_text[prev] + line_list[0]
            else:
                worthy = 0
        else:
            connect_fn(c)
    print("All lines received from master\n")   
    ans  = "SUBMIT\n"
    ans +="codebenders@67\n" + "1000\n"
    i = -1
    while i<max_lines:
        try:
            if (i== -1):
                client_socket.send(ans.encode())
            else:
                client_socket.send((str(i)+"\n").encode())
                client_socket.send((full_text[i]+"\n").encode())
            i+=1
        except socket.timeout:
            continue
        except:
            client_socket.close()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
    
    output = ""
    while True:
        try:
            curr = client_socket.recv(1024)
            if curr:
                line = curr.decode().strip()
                if (line[0:6]== "SUBMIT"):
                    output = line
                    break
        except:
            continue
    print(output)
    client_socket.close()
    print('Time: ', time.time()- start_time)
    c.close()
main()
