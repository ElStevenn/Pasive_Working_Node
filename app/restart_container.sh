#!/bin/bash

# Stop and remove container
docker stop pasive_income_v2
docker rm pasive_income_v2

# Remove container
docker image rm pasive_income

echo "Build and Run container? (y/n)"
read response

if [ "$response" == "y" ]; then
    # Build container 
    docker build -t pasive_income .

    # Run container
    docker run -d -p 80:80 --name pasive_income_v2 pasive_income

    # Get relevant data
    ip=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_name)
    host_port=$(docker inspect --format='{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' $container_name)
    host=$(curl ifconfig.me)

    echo "----------------------------------------------------"
    echo "Container Name: $container_name"
    echo "Container running in http://${host}:$port" 


else
    echo "Ok."
fi
