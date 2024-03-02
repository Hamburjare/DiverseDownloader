# DiverseDownloader
Unlock a universe of content with DiverseDownloader—an API designed for fetching media from a wide array of platforms, offering unparalleled flexibility.

## Requirements
- Docker
- Docker Compose

## Usage
To start the server, run the following command:
```bash
docker compose up -d --build
```
The server will be available at `http://localhost:5353`.
To change the port, modify the `ports` section in the `docker-compose.yml` file.

To stop the server, run the following command:
```bash
docker compose down
```