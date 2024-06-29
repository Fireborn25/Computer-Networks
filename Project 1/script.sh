#!/bin/bash

read -p "Enter the destination IP or hostname: " destination

max_ttl=30

output=$(ping -c 1 -t 1 $destination 2>&1)

last_ip=$(echo "$output" | awk '/^PING/{print $3}' | sed 's/[():]//g')
echo "Traceroute to $destination ($last_ip), 30 hops max , 60 byte packets"

for ttl in $(seq 1 $max_ttl); do
    output=$(ping -c 1 -t $ttl $destination 2>&1)

    from_ip=$(echo "$output" | awk '/^From/{print $2}' | sed 's/[():]//g')

    curr=$(ping -c 1 -t $ttl $from_ip 2>&1)
    rtt1=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
    curr=$(ping -c 1 -t $ttl $from_ip 2>&1)
    rtt2=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
    curr=$(ping -c 1 -t $ttl $from_ip 2>&1)
    rtt3=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
    if [ "$from_ip" == "" ]; then
        ip=$(echo "$output" | awk '/^64/{print $5}' | sed 's/[():]//g')
        rtt1=$(echo "$output" | awk '/time=/{print $7}' | cut -d '=' -f 2)
        curr=$(ping -c 1 -t $ttl $ip 2>&1)
        rtt2=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
        curr=$(ping -c 1 -t $ttl $ip 2>&1)
        rtt3=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
	IFS=" " read -ra rip  <<< "$ip"
        if [ "${rip[0]}" == "$last_ip" ]; then
		rtt1=$(echo "$output" | awk '/time=/{print $7}' | cut -d '=' -f 2)
        	curr=$(ping -c 1 -t $ttl $ip 2>&1)
        	rtt2=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
       		curr=$(ping -c 1 -t $ttl $ip 2>&1)
        	rtt3=$(echo "$curr" | awk '/time=/{print $7}' | cut -d '=' -f 2)
		echo "$ttl:  $last_ip  $rtt1 ms  $rtt2 ms  $rtt3 ms"
                break
	else
		echo "$ttl:  ***"
        fi
    else
	if [ "$rtt1" == "" ]; then
		echo "$ttl:  $from_ip  Router could not be timed"
	else
        	echo "$ttl:  $from_ip  $rtt1 ms  $rtt2 ms  $rtt3 ms"
	fi
    fi
done
