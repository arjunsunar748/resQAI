# ==============================================================================
# RESQ AGENT - Frontend Production Dockerfile (Nginx multi-stage)
# ==============================================================================
FROM node:22-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY . .
RUN npm run build

FROM nginx:alpine-slim AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
