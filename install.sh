#!/bin/bash 

docker compose create

echo "alias sublimate='docker compose -f ${PWD}/docker-compose.yml run sublimate'" >> ${HOME}/.bashrc