# DenseReviewer

DenseReviewer is a screening prioritization tool for medical systematic reviews based on dense retrieval and relevance feedback. It helps medical researchers and librarians efficiently screen titles and abstracts of studies by prioritizing relevant ones using state-of-the-art dense retrieval methods.


## Features

- **Dense Retrieval & Relevance Feedback**: Uses PICO queries and iteratively updates rankings based on screener feedback
- **Dual Screening Modes**: 
  - Ranking mode: View studies in a paginated ranked list
  - Focus mode: Review studies individually with keyboard controls
- **Real-time Progress Tracking**: Visual analytics showing review progress and relevance discovery curves

## Installation

#### Prerequisites:
 [Docker](https://docs.docker.com/get-started/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) (+ NVIDIA GPU & CUDA optional)
#### Compatibility Checklist:

- [x] **Linux (x86_64)** – Tested ✅

- [x] **Windows (x86_64)** – Tested ✅

- [ ] **macOS (Apple Silicon)** – Under Testing 🚧

### 1. Get the Code

```bash
git clone https://github.com/ielab/densereviewer.git

cd densereviewer
```


### 2. Launch DenseReviewer

****CPU Users****:

```bash
# build the backend service
docker compose build backend --no-cache

# start the app
docker compose up -d
```

****GPU Users****:

```bash
# build the backend service with gpu support
docker compose -f docker-compose-gpu.yml build backend --no-cache

# start the app with gpu support
docker compose -f docker-compose-gpu.yml down && docker compose -f docker-compose-gpu.yml up -d
```

### Using the Python Library

The [Python library](https://github.com/ielab/dense-screening-feedback) from our research paper ["Dense Retrieval with Continuous Explicit Feedback for Systematic Review Screening Prioritisation"](https://dl.acm.org/doi/10.1145/3626772.3657921) supports experiments with customized dense retrievers and relevance feedback methods.

## System Architecture

DenseReviewer consists of six Docker containers:
1. Web-based front end
2. REST API backend
3. Database for storing user activity and corpus data
4. Message broker for task queues
5. Service for parsing, encoding, and initial ranking
6. Service for handling re-ranking

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) with additional clauses - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

We extend our gratitude to the engineering team of AI DETA Technologies Co. for their consultation and support in developing DenseReviewer.

## Contact

For questions and feedback, please open an issue on GitHub or contact the authors directly.
