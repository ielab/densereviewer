# DenseReviewer

DenseReviewer is a screening prioritisation tool for medical systematic reviews based on dense retrieval and relevance feedback. It helps medical researchers and librarians efficiently screen titles and abstracts of studies by prioritizing relevant ones using state-of-the-art dense retrieval methods.


## Features

- **Dense Retrieval & Relevance Feedback**: Uses customised PICO queries and iteratively updates rankings based on screener feedback
- **Dual Screening Modes**: 
  - Ranking mode: View studies in a paginated ranked list
  - Focus mode: Review studies individually with keyboard controls
- **Real-time Progress Tracking**: Visual analytics showing review progress and relevance discovery curves
- **Open Source Python Library**: Enables experimentation with existing datasets and custom dense retrievers
- **Docker Containerized**: Easy deployment with all components packaged in Docker containers

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) NVIDIA GPU with CUDA support for accelerated processing

### Installation


### Using the Python Library

The [Python library](https://github.com/ielab/dense-screening-feedback) from our SIGIR paper supports experimentation with dense retrieval and active learning methods.


## System Architecture

DenseReviewer consists of six Docker containers:
1. Web-based front end
2. REST API backend
3. Database for storing user activity and corpus data
4. Message broker for task queues
5. Service for parsing, encoding, and initial ranking
6. Service for handling re-ranking

## Citation

If you use DenseReviewer in your research, please cite our paper:

```bibtex
@inproceedings{mao2024densereviewer,
  title={Dense Retrieval with Continuous Explicit Feedback for Systematic Review Screening Prioritisation},
  author={Mao, Xinyu and Zhuang, Shengyao and Koopman, Bevan and Zuccon, Guido},
  booktitle={Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval},
  pages={2357--2362},
  year={2024}
}
```


## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) with additional clauses - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

We extend our gratitude to the engineering team of AI DETA Technologies Co. for their consultation and support in developing the web application.

## Contact

For questions and feedback, please open an issue on GitHub or contact the authors directly.

## Demo

A live demo of DenseReviewer is available at https://densereviewer.ielab.io
