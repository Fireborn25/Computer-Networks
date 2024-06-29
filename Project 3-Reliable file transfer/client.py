import socket
import threading
import hashlib
import time
import matplotlib.pyplot as plt

def receive_messages(s):
    global rate,change
    rtt = 0.01
    start_time = time.time()
    global lines_received,full_text,lines_count,time_line, rate_change
    check_window = 10
    correct_window = 5
    c = 0
    inc = 0
    while (lines_count >0):
        time1 = time.time()
        s.settimeout(rtt)
        try:
            c +=1
            curr = s.recv(4096)
            time2 = time.time()
            rtt = max(min(rtt,time2-time1),0.0001)
            line = curr.decode().split("\n\n",1)
            suffix = line[0].split('\n')
            offset = ((suffix[0]).split(" "))[1]
            j = int(offset)//1448
            if (lines_received[j] == 1):
                continue
            if (len(suffix)==2):
                change = 0
            else:
                if (change == 0):
                    rate/=2
                    change =1
            full_text[j] = line[1]
            lines_received[j] =1
            lines_count = lines_count -1
            time_line[j] = time.time()-start_time
        except:
            inc += 1
        if (c + inc > check_window):
            if (c>= correct_window):
                rate +=1
            else:
                rate /=2
            correct_window = c-1
            c = 0
            inc = 0
    

def main():
    ip = 'vayu.iitd.ac.in' # enter ip of server here.
    port = 9802
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.connect((ip,port))
    server.send("SendSize\nReset\n\n".encode())
    size_package = b''
    while True:
        server.settimeout(1)
        try:
            size_package = server.recv(1024)
            break
        except:
            server.send("SendSize\nReset\n\n".encode())
    size = int(size_package.decode()[6:])
    count = int((size+1447)/1448)
    global lines_received,full_text,lines_count , time_line,rate,change, rate_change
    change = 0
    rate = 100
    rate_change = [0]*count
    time_line = [0]*count
    lines_received = [0]*count
    full_text = [""]*count
    lines_count = count
    receive_thread = threading.Thread(target=receive_messages, args=(server,))
    receive_thread.start()
    while (lines_count >0):
        for i in range(count):
            if (change ==1):
                time.sleep(1)
                change = 2
            if lines_received[i] == 0:
                num = 1448
                if i== count-1:
                    num = size - i*1448
                server.send(("Offset: " + str(i*1448) + "\nNumBytes: " +str(num) + "\n\n").encode())
                time.sleep(1/rate)
    # Concatenate the list of strings into a single string
    concatenated_string = "".join(full_text)
    # Calculate the MD5 hash
    md5_hash = hashlib.md5(concatenated_string.encode()).hexdigest()
    # Convert the MD5 hash to lower case and print it
    formatted_md5_hash = md5_hash.lower()
    result = "Submit: bhupesh@101\nMD5: " + formatted_md5_hash +"\n\n"
    server.send(result.encode())
    res = b''
    while True:
        server.settimeout(0.1)
        try:
            res = server.recv(1024)
            break
        except:
            server.send(result.encode())
    server.close()
    print(res)
    # Create a list of x values (i values) and y values (time_line values)
    # y_values= time_line
    # x_values = range(0,count)

    # Create and display the graph
    # plt.scatter(y_values, x_values,marker = 'o')
    # plt.xlabel('Time')
    # plt.ylabel('Sequence Number')
    # plt.title('Sequence Number vs Time')
    # plt.show()

main()
