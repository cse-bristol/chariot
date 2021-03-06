#!/usr/bin/env bash

envFile="./.env"
conf=""
if ! [ -r "$envFile" ]
then
    read -p "Secure Domains (space separated, leave empty for none): " DOMAINS
    if [[ ! ${DOMAINS} = "" ]]
    then
		read -p "Email address: " EMAIL
		docker run -v "$(pwd)/cert:/etc/letsencrypt" -p "443:443" -e "EMAIL=${EMAIL}" -e "DOMAINS=${DOMAINS}" chariot_cert

		if [ -r "cert/certs/fullchain.pem" ]
        then
            conf="-ssl"
        fi
	fi

	echo "EMAIL=$EMAIL"$'\n'"DOMAINS=$DOMAINS"$'\n'"CONF_TAG=$conf" >> ".env"
fi

docker-compose up -d