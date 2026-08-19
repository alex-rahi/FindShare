FROM node:22-alpine

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
ENV API_INTERNAL_URL=http://api:8000
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=90s --retries=20 CMD node -e "fetch('http://localhost:3000').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["npm", "run", "dev"]
