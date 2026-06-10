# Build the SPA, then serve the static files with nginx.
FROM node:24-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
# npm install (not ci) tolerates platform-specific optional deps that a
# Windows-generated lockfile omits for the Linux build image.
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
