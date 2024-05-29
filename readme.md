# Snowcaloid Discord bot

Created using Python.

## Requirements

### docker

Create a docker network `sudo docker network create --scope=swarm --attachable -d overlay krile_network`

To start the production version, `docker-compose up --build -d`

If debugging from a seperate host, create an uphold service, so that the network is accessible `sudo docker service create --name krile_network_uphold --network krile_network alpine sh -c "while true; do sleep 3600; done"`

If you're using a different host for the production version than development, connect them using `sudo docker swarm init --advertise-addr <IP of current device>`, then connect to it using the returned command.