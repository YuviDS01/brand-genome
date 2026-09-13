# Single-stage build -- fine for a prototype; a production image would
# split deps/build/runtime stages to cut final image size.
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# NEXT_PUBLIC_* variables are inlined into the client-side JS bundle at
# `next build` time -- setting them via docker-compose's `environment:` at
# container *runtime* is too late; the browser bundle would already be
# built without them. A build ARG is the correct mechanism here.
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]