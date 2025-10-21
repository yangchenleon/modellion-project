FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com && npm i
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
