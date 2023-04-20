#!/bin/sh

rm -rf models/*
rasa train

docker-compose down --volumes
docker-compose up --build