# ShopHub — Full-Stack E-commerce Platform

ShopHub is a full-stack e-commerce application built with Django REST Framework and Vue 3. It supports product browsing, shopping cart management, order processing, simulated payments, and inventory management.

The project uses Docker to run backend services, Celery for asynchronous task processing, Redis as a message broker and result backend, and Nginx as a reverse proxy.

## Features

- **User Authentication** — User registration and login.
- **Product Management** — Browse products, view product details, and explore product categories.
- **Product Images** — Display product images stored in the media directory.
- **Shopping Cart** — Add products to the cart and manage quantities.
- **Order Management** — Create orders and view order details and statuses.
- **Simulated Payments** — Simulate order payments for demonstration purposes.
- **Payment Timestamps** — Record the payment time when an order is paid.
- **Order Cancellation** — Cancel pending orders.
- **Inventory Management** — Restore product stock when a pending order is cancelled.
- **Asynchronous Tasks** — Use Celery and Redis for background task processing.
- **Reverse Proxy** — Use Nginx to forward API requests to Django and serve media files.
- **Containerized Backend** — Run backend services using Docker Compose.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| REST API | Django REST Framework |
| Frontend | Vue 3 |
| Build Tool | Vite |
| HTTP Client | Axios |
| UI Components | Element Plus |
| State Management | Pinia |
| Routing | Vue Router |
| Task Queue | Celery |
| Message Broker and Result Backend | Redis |
| Containerization | Docker, Docker Compose |
| Reverse Proxy | Nginx |
| Version Control | Git, GitHub |

## Project Structure

```text
ShopHub/
├── config/                 # Django project configuration
├── products/               # Product and category management
├── orders/                 # Order processing and payment logic
├── users/                  # User-related functionality
├── frontend/               # Vue 3 frontend application
├── nginx/
│   └── nginx.conf          # Nginx configuration
├── media/                  # Uploaded product images
├── Dockerfile              # Backend Docker image
├── docker-compose.yml      # Backend service configuration
├── .env.docker             # Docker environment variables
└── README.md               # Project documentation
```

## Prerequisites

Install the following software before starting the project:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) and npm
- Git

The backend Python dependencies are installed during the Docker image build.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/111wjh/ShopHub.git
cd ShopHub
```

### 2. Configure Environment Variables

Check the `.env.docker` file and ensure the settings match your local environment.

The configuration must include the Django settings and Redis connection URLs used by the backend and Celery.

For example, if Redis is configured with database 0 as the broker and database 1 as the result backend:

```dotenv
CELERY_BROKER_URL=redis://shophub-redis:6379/0
CELERY_RESULT_BACKEND=redis://shophub-redis:6379/1
```

Use the actual variable names expected by your Django settings.

**Security:** Never commit production passwords, secret keys, or other sensitive credentials to a public repository.

### 3. Start Redis

Redis runs in a separate Docker container and is not included in `docker-compose.yml`.

First, check whether the Redis container already exists:

```powershell
docker ps -a --filter "name=shophub-redis"
```

If the container exists but is stopped, start it:

```powershell
docker start shophub-redis
```

If the container has not been created, create and start it:

```powershell
docker run -d --name shophub-redis --restart unless-stopped redis:7
```

Verify that Redis is running:

```powershell
docker ps --filter "name=shophub-redis"
```

**Important:** Redis must be reachable by the backend and Celery containers through a shared Docker network. The hostname `shophub-redis` must resolve from those containers. If necessary, connect the Redis container to the Docker network used by the application.

### 4. Start the Backend Services

From the project root directory, run:

```powershell
docker compose --env-file .env.docker up -d --build
```

This starts three services:

- **Backend** — Django REST API on port `8000`.
- **Celery** — Background task worker.
- **Nginx** — Reverse proxy on port `8080`.

Check the running containers:

```powershell
docker ps
```

### 5. Start the Frontend

Open a separate terminal window and run:

```powershell
cd frontend
npm install
npm run dev
```

Vite starts the frontend development server. Open the URL shown in the terminal, normally:

http://localhost:5173

## Access the Application

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API through Nginx | http://localhost:8080/api/ |
| Django backend directly | http://localhost:8000/ |

The available API endpoints depend on the application's URL configuration.

## Order Processing

The order workflow supports the following operations:

1. Browse products and add items to the shopping cart.
2. Create an order from the selected products.
3. Pay for an order using the simulated payment workflow.
4. Record the payment timestamp when payment succeeds.
5. Cancel an order while it is still pending.
6. Restore product inventory when a pending order is cancelled.

Order status transitions and inventory updates are handled by the backend.

## Nginx and Media Files

Nginx forwards API requests to the Django backend and provides access to media files.

The Nginx configuration is located at:

```text
nginx/nginx.conf
```

The Docker Compose configuration publishes Nginx on port `8080` and Django directly on port `8000`.

Uploaded media files are persisted using the local `media/` directory mounted into the backend and Nginx containers.

## Useful Docker Commands

### View Running Containers

```powershell
docker ps
```

### View Backend Logs

```powershell
docker logs shophub-backend
```

### View Celery Logs

```powershell
docker logs shophub-celery
```

### View Nginx Logs

```powershell
docker logs shophub-nginx
```

### View Redis Logs

```powershell
docker logs shophub-redis
```

### Restart Redis

```powershell
docker restart shophub-redis
```

### Stop Backend Services

```powershell
docker compose --env-file .env.docker down
```

This command stops the Compose-managed backend, Celery, and Nginx services. It does not stop Redis because Redis is managed separately.

## Important Notes

- Payments are simulated and do not process real transactions.
- Redis must be running and accessible before Celery background tasks can work correctly.
- Redis and the application containers must share a network that supports the configured Redis hostname.
- The frontend development server runs separately from Docker Compose.
- Do not expose Redis publicly unless proper network restrictions and authentication are configured.
- The project is intended for learning, development, and portfolio demonstration.
- Additional security and deployment configuration is required before production use.

## Future Improvements

Potential future enhancements include:

- Automated backend and frontend tests.
- Production-ready deployment configuration.
- Real payment gateway integration.
- Improved logging and monitoring.
- Continuous integration and deployment (CI/CD).

## License

This project is intended for educational and portfolio demonstration purposes. Add a license file if you plan to distribute it under a specific open-source license.