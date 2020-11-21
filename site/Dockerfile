FROM node:12
WORKDIR /var/www

COPY package*.json ./

RUN npm install
COPY . .
EXPOSE 8080
CMD [ "node", "index.js" ]
