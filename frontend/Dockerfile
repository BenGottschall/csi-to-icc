# Frontend Dockerfile for Next.js application

# ============================================
# Dependencies Stage
# ============================================
FROM node:20-alpine AS deps

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# ============================================
# Builder Stage
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

# Set environment variable for build
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application
RUN npm run build

# ============================================
# Development Stage
# ============================================
FROM node:20-alpine AS development

WORKDIR /app

# Copy package files and install all dependencies (including dev)
COPY package.json package-lock.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variable
ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=development

# Run in development mode with hot reload
CMD ["npm", "run", "dev"]

# ============================================
# Production Runner Stage
# ============================================
FROM node:20-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only production dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy built application from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts

# Ensure public directory exists (Next.js expects it)
RUN mkdir -p ./public

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start Next.js in production mode
CMD ["npm", "start"]
