# Dev-mode container (Vite dev server). A production build stage
# (vite build → static hosting) is added at deploy time (Phase 6).
FROM node:22-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

USER node
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
