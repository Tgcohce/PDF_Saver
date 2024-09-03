#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'
echo -e "${YELLOW}Enter your bot token:${NC}"
read -r TOKEN
if [ ! -f ".env" ]; then
    echo -e "${RED}.env file not found! Copying .env.example to .env...${NC}"

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created from .env.example.${NC}"
    else
        echo -e "${RED}.env.example file not found! Cannot create .env file.${NC}"
        exit 1
    fi
fi
sed -i "s/BOT_TOKEN=CHANGE_ME/BOT_TOKEN=${TOKEN}/" .env
echo -e "${GREEN}Token has been updated in the .env file.${NC}"
