FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Dev server with hot reload (used by docker-compose.yml).
FROM deps AS dev
COPY . .
RUN chown -R node:node /app
USER 1000
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM deps AS build
COPY . .
RUN npm run build

# Production: static files served by nginx, /api proxied to the backend.
FROM nginx:1.30-alpine AS prod
# Pick up Alpine security fixes released since the nginx image was built.
RUN apk upgrade --no-cache
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
