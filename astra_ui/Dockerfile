# Dependencies
FROM node:22-slim AS base
WORKDIR /app
COPY package*.json ./
RUN npm install

# Dev mode
FROM base AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build for prod
FROM base AS build-step
COPY . .
RUN npm run build

# Prod mode
FROM node:22-alpine AS prod
WORKDIR /app
COPY --from=build-step /app/build ./build
COPY --from=build-step /app/package*.json ./
RUN npm ci --omit=dev 
EXPOSE 5173
ENV NODE_ENV=production
ENV PORT=5173
CMD ["node", "build/index.js"]
