# Skills

## Technical Profile

Daniela is an MLOps Engineering student with practical experience building Python-based machine-learning and AI applications.

Her strongest current areas are:

* Python
* FastAPI
* retrieval-augmented generation
* AI and LLM applications
* Docker
* Linux
* Git and GitHub
* model serving
* MLflow
* working with APIs and connected services

She has also gained practical experience with cloud deployment, CI/CD and running a live AI backend on AWS.

Daniela is still early in her technical career and does not present every technology she has encountered as an area of expertise.

This document distinguishes between technologies she uses regularly, technologies she has used in projects and areas where her experience is still introductory.

## Programming

### Python

**Level: Strong practical foundation**

Python is Daniela's primary programming language.

She has used it to build complete applications and workflows involving:

* backend APIs
* machine learning
* deep learning
* model training
* model inference
* retrieval-augmented generation
* embeddings
* vector search
* AI agents
* LLM applications
* evaluation
* automation
* data processing
* testing
* command-line tools

Her recent projects use Python as the main language for both AI logic and backend application development.

She is comfortable structuring Python applications across multiple modules rather than working only in notebooks.

She is continuing to develop deeper knowledge of software architecture, testing patterns, asynchronous programming and production Python.

### C#

**Level: Foundational**

Daniela completed Programming 1 using C# and received grade A.

Her experience includes:

* variables and data types
* conditions
* loops
* methods
* classes and objects
* basic object-oriented programming
* debugging
* program structure

C# is not her current primary language.

### SQL

**Level: Foundational practical experience**

Daniela has used SQL through education and project work.

Her experience includes:

* queries
* relational data
* filtering
* joins
* basic schema work
* using databases from applications

She has worked with technologies including PostgreSQL, DuckDB and SQLite.

## Backend Development

### FastAPI

**Level: Practical project experience**

FastAPI is Daniela's main backend framework.

She has used it for both machine-learning inference services and generative-AI applications.

Her experience includes:

* API route design
* request and response schemas
* Pydantic validation
* dependency injection
* REST endpoints
* health endpoints
* model-inference endpoints
* multipart file uploads
* RAG chat endpoints
* error handling
* middleware
* CORS
* connecting APIs to frontend applications
* structured API responses

In DANI, FastAPI is used as the production backend for the RAG service.

### Pydantic

Daniela uses Pydantic for:

* request validation
* response schemas
* structured application data
* application configuration
* environment-based settings

She has also used PydanticAI in generative-AI coursework.

### REST APIs

Daniela has practical experience building and consuming HTTP APIs.

She understands concepts including:

* HTTP methods
* request and response bodies
* headers
* status codes
* JSON responses
* validation
* stateless services
* separation between frontend and backend

### SQLAlchemy

**Level: Introductory**

Daniela has limited practical exposure to SQLAlchemy and understands its role in Python applications that interact with relational databases.

It is not currently one of her strongest tools.

## Machine Learning

### Classical Machine Learning

**Level: Foundational practical experience**

Daniela has studied and implemented classical machine-learning workflows.

Her experience includes:

* supervised learning
* regression
* classification
* preprocessing
* feature engineering
* train/validation/test separation
* model evaluation
* comparing model performance
* reproducibility

She has used scikit-learn in coursework and projects.

### Deep Learning

**Level: Practical project experience**

Daniela has practical experience training neural networks and integrating trained models into applications.

Her strongest deep-learning experience comes from PyTorch.

She has worked with:

* convolutional neural networks
* training loops
* validation loops
* loss functions
* optimizers
* checkpointing
* hyperparameter experiments
* reproducible data splitting
* test evaluation
* CPU and GPU execution
* model serialization
* inference

### PyTorch

**Level: Practical project experience**

Daniela built a modular PyTorch training pipeline for CIFAR-10 image classification.

She experimented with learning rates, batch sizes and training duration and selected the final model using validation performance.

The trained model was later reused in a model-serving project.

She has also worked with:

* saved PyTorch weights
* TorchScript export
* `torch.jit.load`
* inference preprocessing
* logits
* softmax
* confidence scores

### TensorFlow

**Level: Introductory practical experience**

Daniela has used TensorFlow during her machine-learning studies.

Her PyTorch experience is currently more extensive.

### NumPy and pandas

Daniela has used NumPy and pandas for data handling, experimentation and machine-learning workflows.

## Model Serving

**Level: Practical project experience**

Daniela has experience taking a trained model beyond the training stage and integrating it into an application.

Her CIFAR-10 project covered:

`training -> checkpoint -> TorchScript artifact -> FastAPI inference -> Streamlit client -> Docker`

She understands the importance of separating:

* training code
* saved model artifacts
* inference logic
* preprocessing
* API serving
* user interfaces
* runtime configuration

She has built stateless inference APIs and containerized model-serving applications.

## Generative AI and LLM Applications

### Large Language Models

**Level: Practical project experience**

Daniela has built applications that use large language models through APIs.

Her work has included:

* OpenAI
* OpenRouter
* prompt design
* system prompts
* structured outputs
* context construction
* source-grounded answers
* fallback behaviour
* model-provider configuration

She focuses primarily on integrating models into larger applications rather than training foundation models.

### Retrieval-Augmented Generation

**Level: Strong practical project experience**

RAG is one of Daniela's most developed areas within generative AI.

She has built multiple RAG systems and worked with the complete retrieval flow:

1. document loading
2. text structuring
3. chunking
4. embeddings
5. vector storage
6. query embedding
7. semantic retrieval
8. context construction
9. LLM generation
10. source attribution

Her work includes both the collaborative Wired-AI project and DANI.

She has worked with retrieval concerns such as:

* chunk size
* chunk boundaries
* metadata
* retrieval relevance
* result limits
* similarity scores
* fallback behaviour
* grounding
* source presentation

### Embeddings and Semantic Search

Daniela has practical experience with embedding-based retrieval.

She has used:

* OpenAI embeddings
* Cohere multilingual embeddings
* vector similarity search
* Qdrant
* LanceDB

DANI currently uses OpenAI `text-embedding-3-small` embeddings with Qdrant.

### Vector Databases

Daniela has practical experience with:

* Qdrant
* LanceDB

She has used vector stores to persist document chunks, metadata and embeddings and retrieve relevant information through semantic similarity search.

### AI Agents and Multi-Agent Systems

**Level: Practical educational experience**

Daniela has built agent-based workflows during her generative-AI studies.

She has worked with systems where agents had responsibilities such as:

* planning
* execution
* critique
* validation
* human approval

Her experience includes both LangChain and PydanticAI.

A major lesson from this work was that multi-agent systems introduce additional complexity, latency, cost and failure points and should be used only when that complexity provides a clear benefit.

### LangChain

**Level: Practical educational exposure**

Daniela has used LangChain when building AI-agent workflows.

It is not currently a central dependency in her main personal projects.

### PydanticAI

**Level: Practical project experience**

Daniela has used PydanticAI for structured generative-AI workflows, schemas and agent logic.

It was used in the Wired-AI project.

## LLMOps and Evaluation

Daniela has practical experience thinking about AI applications as systems that need to be evaluated and observed rather than only demonstrated.

Her work has included:

* prompt evaluation
* RAG evaluation
* retrieval quality
* structured experiment tracking
* comparing changes
* latency measurements
* source counts
* retrieval scores
* fallback behaviour

### MLflow

**Level: Practical project experience**

Daniela has used MLflow in several contexts.

Her experience includes:

* experiment tracking
* logging evaluation results
* shared remote MLflow environments
* RAG metrics
* model and configuration metadata
* prompt management

DANI uses MLflow both for optional RAG observability and for managing its production system prompt.

## Testing and Code Quality

Daniela has practical experience with automated testing and code-quality tooling.

She currently uses:

* pytest
* Ruff

DANI's backend test suite covers API behaviour such as:

* successful requests
* validation failures
* expected errors
* unexpected service errors
* health endpoints
* request IDs

GitHub Actions runs linting and tests before production deployment.

Daniela is continuing to develop deeper knowledge of testing strategies and production-quality test coverage.

## Docker and Containers

### Docker

**Level: Practical project experience**

Daniela has used Docker across several projects.

She has containerized:

* FastAPI backends
* machine-learning inference APIs
* Streamlit frontends
* RAG applications
* multi-service systems

She understands concepts including:

* Dockerfiles
* container images
* ports
* environment variables
* volumes
* isolated runtimes

### Docker Compose

**Level: Practical project experience**

Daniela uses Docker Compose to run applications containing multiple connected services.

Her projects have included combinations such as:

* FastAPI + Streamlit
* FastAPI + Qdrant
* backend + vector database + supporting services

She has worked with:

* service networking
* volumes
* port publishing
* service dependencies
* local and production Compose configurations

## CI/CD

### GitHub Actions

**Level: Practical project experience**

Daniela has configured GitHub Actions workflows for continuous integration and deployment.

In DANI, pushes and pull requests targeting `main` run automated backend validation.

The CI workflow includes:

* dependency installation with `uv`
* Ruff
* pytest

A successful CI run on `main` can trigger the production deployment workflow.

### Continuous Deployment

Daniela has built an automated deployment flow for DANI.

The production path includes:

`GitHub -> GitHub Actions -> AWS authentication -> AWS Systems Manager -> EC2 -> Docker Compose`

The workflow uses OpenID Connect to assume an AWS IAM role rather than relying on long-lived AWS access credentials stored in GitHub.

AWS Systems Manager is then used to execute the deployment on the EC2 instance.

This deployment work was configured by Daniela as part of the DANI project.

## Cloud and Infrastructure

### AWS

**Level: Practical introductory-to-intermediate project experience**

Daniela has practical experience operating an application on AWS.

For DANI, she configured an EC2 instance through the Linux terminal and uses it to host the production backend and supporting services.

Her current AWS experience includes:

* EC2
* IAM
* OpenID Connect integration
* Systems Manager
* Linux server administration
* application deployment
* environment configuration

Her AWS experience is project-based rather than broad expertise across the full AWS platform.

### AWS EC2

Daniela has configured and operates a Linux EC2 instance for DANI.

She has worked directly with the server through the terminal to configure the runtime environment and services needed by the application.

### AWS IAM and OIDC

Daniela has configured a deployment approach where GitHub Actions assumes an AWS IAM role using OpenID Connect.

This allows the deployment workflow to obtain temporary AWS credentials instead of storing permanent AWS access keys in the repository.

### AWS Systems Manager

DANI's deployment workflow uses AWS Systems Manager to execute deployment commands on the EC2 instance.

This avoids requiring GitHub Actions to connect directly to the production server over SSH.

### Azure

**Level: Introductory practical experience**

Daniela has worked with Azure during her MLOps and cloud studies.

Her AWS experience is currently more developed because DANI is actively deployed there.

## Reverse Proxy and Web Infrastructure

### Caddy

**Level: Practical project experience**

Daniela uses Caddy as the reverse proxy in front of the production DANI API.

Requests to:

`api.daniela.algerydh.com`

are forwarded to the FastAPI service running on the EC2 host at:

`127.0.0.1:8000`

### Cloudflare

**Level: Practical project experience**

Daniela uses Cloudflare as part of the infrastructure around her personal website and DANI deployment.

Her experience is focused on the configuration required for her own deployed services rather than broad Cloudflare platform expertise.

## Data and Databases

### PostgreSQL

**Level: Foundational practical experience**

Daniela has worked with PostgreSQL through coursework and projects.

It has also been used as part of supporting infrastructure in project environments.

### DuckDB

**Level: Foundational practical experience**

Daniela has used DuckDB in data-oriented coursework and workflows.

### SQLite

**Level: Foundational practical experience**

Daniela has used SQLite as a lightweight relational database in development and educational contexts.

### Qdrant

**Level: Practical project experience**

Qdrant is the vector database used by DANI.

Daniela has worked with:

* creating collections
* vector dimensions
* cosine similarity
* point payloads
* upserts
* semantic queries
* similarity scores
* persistent storage
* health checks

### LanceDB

**Level: Practical project experience**

Daniela used LanceDB as the vector database in Wired-AI.

Her work included storing and retrieving embedded knowledge chunks and associated metadata.

### DVC

**Level: Introductory practical experience**

Daniela has used DVC in machine-learning coursework for data or artifact versioning.

It is not currently a central tool in her main projects.

## Linux and Development Environment

### Linux

**Level: Very comfortable**

Linux is Daniela's primary development environment.

She uses Pop!_OS on her own computer and also works with Linux on remote servers.

Her experience includes:

* filesystem navigation
* package and dependency management
* processes
* permissions
* environment variables
* Docker
* Git
* network and service inspection
* remote server work
* application startup and troubleshooting

### Command Line

Daniela is comfortable working primarily through the terminal.

She regularly uses the command line for:

* project navigation
* Python environments
* Git
* Docker
* application startup
* testing
* dependency installation
* server administration
* inspecting logs and services
* deployment work

### Git and GitHub

**Level: Practical everyday use**

Daniela uses Git and GitHub regularly.

Her experience includes:

* repository creation
* commits
* branches
* merging
* rebasing
* pull requests
* resolving merge conflicts
* branch protection
* collaborative workflows
* GitHub Actions

She has worked both independently and in team repositories.

### uv

**Level: Practical everyday use**

Daniela uses `uv` for:

* Python dependency management
* virtual environments
* locked dependencies
* running project commands

Several of her current Python projects use `uv`.

### Jupyter

Daniela uses Jupyter notebooks primarily for:

* experimentation
* data exploration
* machine learning
* comparing model configurations

She prefers application code to live in structured modules when moving beyond exploration.

## Frontend and User Interfaces

Frontend development is not Daniela's main specialisation, but she has practical experience building interfaces for her projects.

### Streamlit

**Level: Practical project experience**

Daniela has built Streamlit interfaces for:

* RAG applications
* machine-learning model serving
* document-based AI applications

She has used Streamlit to collect user input, call backend APIs and display results.

### React

**Level: Practical project experience**

Daniela uses React in her personal website and the DANI interface.

She can work with components, routing, state and API integration in the context of her own applications.

She does not currently position herself as a specialist frontend developer.

### TypeScript

**Level: Practical project experience**

Daniela uses TypeScript in the React-based personal website and DANI frontend.

Her TypeScript experience is primarily application-oriented rather than advanced language or frontend-framework expertise.

### HTML and CSS

**Level: Practical foundation**

Daniela has previous education in web design and currently works directly with HTML/CSS concepts when building her personal website.

She has practical experience with:

* responsive layouts
* component styling
* media queries
* hover and interaction states
* mobile layouts

Frontend development remains secondary to her focus on AI, backend development and MLOps.

## Architecture and System Thinking

Daniela is particularly interested in how different parts of a technical system connect.

Her projects increasingly combine multiple layers such as:

* user interfaces
* APIs
* AI or machine-learning logic
* databases
* vector stores
* containers
* observability
* cloud infrastructure
* CI/CD
* production deployment

She considers questions such as:

* Where does data enter the system?
* How do services communicate?
* Which component owns each responsibility?
* What happens when a dependency fails?
* How is the system deployed?
* How can its behaviour be observed?
* How is quality evaluated?
* How are credentials and configuration handled?

She prefers understanding the full path through an application rather than treating each technology as an isolated tool.

## Strongest Current Areas

Daniela would currently describe her strongest technical areas as:

* Python
* FastAPI
* RAG
* LLM application development
* Docker
* Linux and command-line development
* Git and GitHub
* MLflow
* model serving
* integrating multiple services into a working application

She also has growing practical experience with:

* AWS
* CI/CD
* GitHub Actions
* Qdrant
* deployment
* React and TypeScript

## Areas Still Developing

Daniela is actively developing deeper competence in areas including:

* production backend architecture
* automated testing
* asynchronous Python
* system architecture
* cloud architecture
* infrastructure automation
* monitoring
* observability
* security
* reliability
* scaling
* production AI evaluation

These are areas she is learning and practising rather than claiming as established expertise.
