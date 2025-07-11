FROM node:18-alpine

WORKDIR /app

# Set Node.js memory limit
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Copy package files
COPY package.json ./
COPY yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile --network-timeout 300000

# Copy application code
COPY . .

# Create public directory
RUN mkdir -p public

# Expose port
EXPOSE 3000

# Start in development mode (no build step to avoid memory issues)
CMD ["yarn", "start"]
