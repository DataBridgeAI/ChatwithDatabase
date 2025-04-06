FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the code
COPY . .

# Expose React development server port
EXPOSE 3000

# Start the React development server
CMD ["npm", "start"]