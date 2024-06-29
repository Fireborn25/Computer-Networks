import socket
import threading
import time

# Global variables
server_ip = '10.17.51.115'
server_port = 9801
max_lines = 1000
lines_received = [0]*max_lines
sent_lines  = [0]*max_lines
full_text = [""]*max_lines
lines_count = 0
lock = threading.Lock()
connect = [0,0,0]
c = [None,None,None]
n = 3 # number of slave clients

def connect_fn(s,k):
    global n
    if (n>k):
        c[k], addr1 = s.accept()
        print(f"Connection received from {addr1}")
        connect[k] = 1


def receive_messages(s,k):
    global lines_count,n
    prev = -1
    worthy = 0
    while lines_count <= max_lines:
        if connect[k] == 1:
            curr = b''
            while True:
                c[k].settimeout(0.01)
                try:
                    received_data = c[k].recv(1024)
                    curr+=received_data
                except socket.timeout:
                    break
                except:
                    print('Connection lost from slave')
                    connect[k] = 0
                    break
            if lines_count >= max_lines:
                lines_count +=1
            line = curr.decode()
            line_list = line.split('\n')
            if (len(line_list) >=2):
                i = 0
                while (i<len(line_list)):
                    curr_element = line_list[i]
                    if (curr_element.isdigit()):
                        line_num = int(curr_element)
                        if lines_received[line_num] == 0:
                            prev = line_num
                            lines_count = lines_count +1
                            lines_received[line_num] = 1
                            if (i != len(line_list) -1):
                                full_text[prev] = line_list[i+1]
                                i += 1
                            worthy = 1
                            print("no")
                            print(lines_count)
                        else:
                            worthy = 0
                    elif worthy == 1 and curr_element != "-1":
                        full_text[prev] = full_text[prev] + curr_element  ## Doubt
                    else:
                        worthy = 0  
                    i += 1
            elif (line_list != ['-1'] and worthy == 1):
                full_text[prev] = full_text[prev] + line_list[0]
            else:
                worthy = 0
        elif n<=k:
            break
        else:
            print('Reconnecting to slave')
            connect_fn(s,k)
            
def main():
    global lines_count,n
    host = '10.184.63.57'
    port = 10001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket binded to %s:%s" % (host, port))
    s.listen(5)
    print("Socket is listening for incoming connections")
    
    receive_thread = [None,None,None]
    for i in range(0,n):
        connect_fn(s,i)
        receive_thread[i] = threading.Thread(target=receive_messages, args=(s,i))
        receive_thread[i].start()
        
    prev = -1
    worthy = 0
    start_time = time.time()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    while lines_count <= max_lines:
        curr = b''
        if lines_count < max_lines:
            client_socket.send("SENDLINE\n".encode())
            curr = client_socket.recv(1024)
        else: 
            lines_count +=1
            while True:
                client_socket.settimeout(0.03)
                try:
                    received_data = client_socket.recv(1024)
                    if not received_data:
                        break
                    curr+=received_data
                except socket.timeout:
                    break
        line = curr.decode()
        line_list = line.split('\n')
        if (len(line_list) >=2):
            i = 0
            while (i<len(line_list)):
                curr_element = line_list[i]
                if (curr_element.isdigit()):
                    line_num = int(curr_element)
                    if lines_received[line_num] == 0:
                        prev = line_num
                        lines_count = lines_count +1
                        lines_received[line_num] = 1
                        if (i != len(line_list) -1):
                            full_text[prev] = line_list[i+1]
                            i += 1
                        worthy = 1
                        print("yes")
                        print(lines_count)
                    else:
                        worthy = 0
                elif worthy == 1 and curr_element != "-1":
                    full_text[prev] = full_text[prev] + curr_element  ## Doubt
                else:
                    worthy = 0  
                i+=1
        elif (line_list != ['-1'] and worthy == 1):
            full_text[prev] = full_text[prev] + line_list[0]
        else:
            worthy = 0
    i = 0       
    while i < n:
        if connect[i] == 1:
            try:
                c[i].send("DONE\n".encode())
                i += 1
            except socket.timeout:
                continue
            except:
                print('Connection lost from slave')
                connect_fn(s,i)
        else:
            connect_fn(s, i)
                
    for j in range(0,n):
        i = 0
        while i<max_lines:
            if connect[j] == 1:
                try:
                    line = str(i) + "\n" + full_text[i] + "\n"
                    c[j].send(line.encode())
                    i+=1
                except socket.timeout:
                    continue
                except:
                    print('Connection lost from slave')
                    connect_fn(s,j)
            else:
                connect_fn(s,j)
    ans  = "SUBMIT\n"
    ans +="codebenders@67\n" + "1000\n"
    i = -1
    while i<max_lines:
        try:
            if (i== -1):
                client_socket.send(ans.encode())
            else:
                if (i < 1000):
                    client_socket.send((str(i)+"\n").encode())
                    client_socket.send((full_text[i]+"\n").encode())
            i+=1
        except socket.timeout:
            continue
        except:
            print('Connection lost from server')
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
    print('Time: ', time.time()-start_time)
    client_socket.close()
    #time.sleep(10)

main()