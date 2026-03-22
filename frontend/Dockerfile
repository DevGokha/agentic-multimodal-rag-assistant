# Step 1: Build stage — install dependencies and build the React app
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Step 2: Production stage — serve the built files with a lightweight server
FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

# Step 3: Expose port 5173 and serve the built React app
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
