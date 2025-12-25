# Movies Recommendation App (Docker)

This is a Dockerized Streamlit app for movie recommendations, including:

- Top popular movies
- Similar movies
- Collaborative Filtering recommendations

You don't need Python or any dependencies installed locally—just Docker.

---

## Steps to Run

### Step 1: Install Docker
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine (Linux).

---

### Step 2: Pull Docker Image
Open terminal / PowerShell and run:

```bash
docker pull nthaibao1712/movies-recommendation:latest
```

This will download the image from Docker Hub.

---

### Step 3: Run Container
Run the app in a container:

```bash
docker run -p 8501:8501 nthaibao1712/movies-recommendation:latest
```

- `-p 8501:8501` maps container port 8501 to your local machine.
- The app will run inside the container.

---

### Step 4: Open App in Browser
Open your browser and go to:

```
http://localhost:8501
```

The Streamlit app should appear.

---

### Optional: Mount Models/Data
If you want to provide your own models or keep large data outside the Docker image:

```bash
docker run -p 8501:8501 -v /path/to/models:/app/models nthaibao1712/movies-recommendation:latest
```

- Replace `/path/to/models` with the folder path on your machine.

---

Enjoy exploring movie recommendations!
