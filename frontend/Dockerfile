FROM node:20-alpine AS builder

RUN npm install -g pnpm

WORKDIR /app

ADD package.json pnpm-lock.yaml /app
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM nginx:stable-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
