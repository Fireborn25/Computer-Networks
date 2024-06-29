In this assignment, we will try to mimic a scenario of multiple nodes cooperating with one another to 
download a large file. 
You will organize yourselves into groups of up to four students, or fewer if you can manage up to four 
devices amongst yourselves. A server has been setup to which each client can connect to download 
parts of the file. Each group will have to write a client program and run it on multiple devices (up to four 
devices) which can collaborate amongst themselves to exchange distinct parts of the file each of them 
have received and reassemble the entire file.
Some complexities to make this interesting: 
- The server is rate limited, i.e. it does not respond to more than a pre-specified maximum rate of 
requests per unit time. 
- The server also allows only one connection per IP address. 
- The server is state-less – it responds with a random part of the file and may send the same parts 
again to a client. The clients will thus be able to reassemble the file quicker when working in 
cooperation, than if each of them was to download the entire file from the server by itself. 
Your job will be to implement the client program and reassemble the file in the shortest possible time. 
The clients running on each device will connect with the server, download parts of the file, share these 
parts with one another, reassemble the file, and submit the reassembled file. You will be tracked on how 
soon you were able to reassemble the file. 
To keep it simple, we will use a text file and the server will respond to a client by sending one line at a 
time in response to requests to fetch a line each time.
