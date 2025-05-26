FROM alt:p11 

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y npm glibc
COPY package-lock.json package-lock.json
COPY package.json package.json

WORKDIR "/frontik/"
RUN npm install
CMD ["npm", "install", "&&", "npm", "run", "dev"]
