# DANI

DANI is Daniela Algerydh's AI-powered portfolio assistant.

It is part of her personal website and gives visitors another way to explore her background, education, skills and projects: instead of only navigating a traditional portfolio or CV, they can ask questions directly.

DANI is also a project in its own right. Daniela built the system as a practical RAG and MLOps/LLMOps application, including the knowledge pipeline, backend API, vector search, model routing, observability, containerisation and production deployment.

## What DANI does

DANI answers questions about Daniela using a curated knowledge base.

Typical questions include:

* What has Daniela studied?
* What projects has she worked on?
* What experience does she have with RAG?
* Which technologies has she used?
* How was DANI built?
* What has she worked with in MLOps or LLMOps?
* What kind of roles is she interested in?

DANI is designed to answer from retrieved information about Daniela rather than treating the language model's general knowledge as the source of truth.

The API returns both the generated answer and information about the knowledge-base sources that were retrieved for the question.

## RAG architecture

DANI uses retrieval-augmented generation, or RAG.

Its knowledge base consists of Markdown documents containing structured information about Daniela, including her profile, education, experience, skills, FAQs and individual projects.

The RAG system has two main flows: ingestion and retrieval.

### Knowledge ingestion

During ingestion:

1. Markdown documents are loaded from the knowledge directory.
2. Documents are split into sections using their Markdown headings.
3. Longer sections are divided into smaller overlapping chunks.
4. Each chunk is converted into an embedding.
5. The chunks, embeddings and metadata are stored in Qdrant.

Each stored chunk includes metadata such as:

* source file
* document title
* section
* chunk index
* original text content

Point IDs are generated deterministically from the chunk's identity and content. This makes the stored representation reproducible when the same knowledge is ingested again.

The embedding model is OpenAI's `text-embedding-3-small`, using 1536-dimensional vectors.

### Retrieval and answer generation

When someone asks DANI a question:

1. The question is normalised and converted into an embedding.
2. Qdrant performs semantic similarity search against the knowledge base.
3. The most relevant chunks are returned.
4. Those chunks are assembled into a context containing their source information and content.
5. The context and user question are sent to the selected language model.
6. The generated answer is returned together with the retrieved sources.

The default retrieval limit is five knowledge chunks.

If retrieval returns no relevant sources, DANI does not attempt to invent an answer. Instead, it reports that it could not find enough relevant information in Daniela's knowledge base.

## Backend

The DANI backend is written in Python using FastAPI.

The main chat endpoint accepts a user message, resolves the user's access tier, runs the RAG service and returns a structured response.

A response contains:

* the generated answer
* the retrieved sources
* the active access tier

Incoming chat messages are validated before entering the RAG pipeline.

The API also includes application health checking and structured HTTP request logging.

Each request receives a request ID. An incoming `X-Request-ID` can be reused, otherwise the backend creates one and includes it in the response. This makes individual HTTP requests easier to trace through logs.

Production logs can be emitted as structured JSON.

## Vector database

DANI uses Qdrant as its vector database.

Qdrant stores the embedded knowledge chunks together with their source metadata and performs the semantic similarity search used during retrieval.

The application checks that embedding dimensions match the configured vector collection before inserting or querying vectors.

Qdrant runs as a separate Docker service and uses a persistent Docker volume so the vector database is not tied to the lifetime of an individual container.

## Embeddings

DANI uses OpenAI's `text-embedding-3-small` model for embeddings.

The embedding service supports both individual texts and batches of texts.

Batch embedding is used during knowledge ingestion so the complete knowledge base does not have to be submitted in a single API request.

The embedding layer validates returned vector dimensions before they are stored or used for search.

## Model providers

DANI supports different language-model providers depending on the user's access tier.

There are currently two tiers:

* free
* premium

The free tier uses a model accessed through OpenRouter.

The premium tier uses OpenAI directly.

The actual chat models are configurable through environment variables rather than being hard-coded throughout the application.

Embedding generation currently uses OpenAI independently of the chat access tier.

## Free and premium access

Visitors without a valid premium access key use the free tier.

Premium access is selected through the `X-DANI-Access-Key` request header.

Premium access keys are not configured as plaintext values in the backend. The server is instead configured with SHA-256 hashes of accepted keys.

When a key is supplied:

1. The input is normalised.
2. The supplied key is hashed using SHA-256.
3. The resulting hash is compared with the configured premium-key hashes.
4. A matching key selects the premium tier.
5. A missing, blank or unrecognised key falls back to the free tier.

Hash comparisons use constant-time digest comparison.

The tier system allows DANI to remain publicly accessible through a lower-cost model while Daniela can provide selected visitors with access to the premium model.

The current implementation identifies valid premium keys but does not yet implement one-time activation, device binding or server-side usage tracking for individual keys.

## Prompt management

DANI uses a dedicated system prompt that controls how the assistant behaves and how it should use retrieved knowledge.

The production system prompt is managed through MLflow's prompt registry rather than being hard-coded inside the RAG service.

The backend loads the prompt named `dani-system-prompt` using its `production` alias when generating an answer.

This separates prompt configuration from the core application code and allows the production prompt to be managed independently from the RAG implementation.

## MLflow and observability

DANI uses MLflow for prompt management and optional RAG experiment tracking.

When MLflow tracking is enabled, a RAG request can record configuration and performance information including:

* access tier
* model provider
* chat model
* embedding model
* retrieval limit
* retrieval score threshold
* question length
* number of retrieved sources
* highest retrieval score
* retrieval latency
* language-model latency
* total request latency
* answer length
* runtime environment

This provides a way to inspect how changes to retrieval settings, models and application configuration affect the system.

## Testing and code quality

The backend has automated tests using pytest.

The API tests cover behaviour including:

* successful chat responses
* source metadata in responses
* free-tier behaviour
* missing messages
* empty messages
* messages exceeding the maximum length
* application errors
* service-unavailable errors
* health responses
* request ID creation
* reuse of incoming request IDs

Ruff is used for static analysis and linting.

Project dependencies are managed with `uv` and locked through the project's dependency lock file.

## Frontend and website integration

DANI is integrated into Daniela's personal website.

The website interface is built with React and TypeScript, while the AI and RAG system runs as a separate Python service.

Keeping the frontend and backend separate means the portfolio interface can evolve independently from the AI service, model configuration and vector database.

The website communicates with the DANI API rather than running the RAG pipeline directly in the browser.

## Containerisation

DANI is containerised with Docker.

The backend image is based on Python and installs its dependencies with `uv`.

Uvicorn serves the FastAPI application inside the backend container on port 8000.

Docker Compose is used to run the backend together with Qdrant.

In the deployed configuration, the FastAPI container is published only on the EC2 host's loopback interface:

`127.0.0.1:8000`

This means the backend container's port is not directly exposed on every network interface of the server.

## AWS infrastructure

DANI runs on an AWS EC2 instance.

Daniela configured the EC2 server herself through the Linux terminal rather than deploying the backend through a fully managed application-hosting platform.

The server hosts the Docker-based DANI backend and its supporting services.

The deployment also uses AWS Identity and Access Management and AWS Systems Manager.

The AWS infrastructure is hosted in the `eu-north-1` region.

## Reverse proxy and production API

Caddy runs directly on the EC2 instance as the reverse proxy in front of the DANI API.

The public API hostname is:

`api.daniela.algerydh.com`

Caddy receives requests for that hostname and reverse-proxies them to:

`127.0.0.1:8000`

The corresponding Caddy configuration is conceptually:

`api.daniela.algerydh.com -> 127.0.0.1:8000`

This gives the public API a dedicated hostname while the FastAPI application itself remains bound behind the reverse proxy.

## Continuous integration

DANI uses GitHub Actions for continuous integration.

The CI workflow runs when code is pushed to `main` and when a pull request targets `main`.

For the backend, the CI pipeline:

1. Checks out the repository.
2. Installs `uv`.
3. Installs the exact locked project dependencies using `uv sync --locked`.
4. Runs Ruff against the application and test code.
5. Runs the pytest test suite.

Deployment is therefore separated from basic code validation.

## Continuous deployment

Production deployment is also automated with GitHub Actions.

The deployment workflow does not run simply because code exists on `main`. It is triggered after the CI workflow for `main` completes successfully.

A failed CI run therefore does not trigger the production deployment job.

For authentication with AWS, GitHub Actions uses OpenID Connect to assume an AWS IAM role.

The workflow has permission to request an OIDC identity token and uses that token through the AWS credentials action to obtain temporary AWS credentials.

This avoids placing long-lived AWS access-key credentials directly in the GitHub repository or workflow.

## Deployment through AWS Systems Manager

GitHub Actions does not SSH directly into the EC2 instance during deployment.

Instead, the workflow uses AWS Systems Manager and the `AWS-RunShellScript` SSM document to execute the deployment commands remotely on the EC2 instance.

When deployment runs, the server:

1. Changes to the DANI repository directory.
2. Fetches the latest state from GitHub.
3. Checks out the `main` branch.
4. Pulls from `origin/main` using a fast-forward-only pull.
5. Runs `docker compose up -d --build`.
6. Displays the resulting Docker Compose service state.

GitHub Actions waits for the SSM command to complete and then retrieves its status, standard output and standard error.

The resulting flow is:

`push to main -> CI -> successful CI -> GitHub Actions deployment -> AWS authentication -> SSM command -> EC2 -> Git update -> Docker rebuild/restart`

This allows changes that pass CI to move from source control to the running backend without Daniela manually logging into the production server for every release.

## Configuration and secrets

DANI uses environment-based configuration.

Configuration includes values such as:

* application environment
* log level and log format
* OpenAI API credentials
* OpenAI chat model
* OpenAI embedding model
* OpenRouter API credentials
* OpenRouter chat model
* OpenRouter base URL
* premium access-key hashes
* MLflow tracking configuration
* Qdrant URL
* Qdrant collection
* CORS origins

Secrets such as API keys are read from environment configuration rather than being embedded directly into the application code.

Pydantic Settings is used to load and validate application configuration.

## Technologies used

DANI combines technologies across AI application development, backend engineering and deployment.

### AI and RAG

* Retrieval-augmented generation
* OpenAI
* OpenRouter
* text embeddings
* semantic search
* Qdrant
* MLflow
* prompt management

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* structlog
* pytest
* Ruff
* uv

### Frontend

* React
* TypeScript
* CSS

### Infrastructure and operations

* Linux
* Docker
* Docker Compose
* AWS EC2
* AWS IAM
* AWS Systems Manager
* GitHub Actions
* OpenID Connect
* CI/CD
* Caddy
* Cloudflare

## Why Daniela built DANI

DANI started from the idea that a portfolio does not have to be completely static.

A recruiter or visitor may be interested in a specific technology, project or part of Daniela's background. Instead of requiring them to search through several pages and decide where the relevant information might be, DANI lets them ask directly.

At the same time, Daniela wanted the assistant itself to be a meaningful technical project rather than a chat widget connected directly to a language-model API.

Building DANI has therefore involved working with the whole path from source information to a running AI service:

* structuring a knowledge base
* chunking documents
* creating embeddings
* storing and searching vectors
* building a RAG pipeline
* managing prompts
* routing between model providers
* designing an API
* handling configuration and access tiers
* adding logs and observability
* writing automated tests
* containerising services
* configuring a Linux production server
* configuring a reverse proxy
* setting up AWS access
* building CI/CD workflows
* automating production deployments

DANI is both part of Daniela's portfolio and a project she uses to develop and demonstrate practical MLOps and LLMOps skills.

## What 'DANI' stands for
DANI stands for Daniela's Assistant for Navigating Information


## Current status

DANI is an actively developed project.

The core RAG pipeline, knowledge ingestion, vector retrieval, FastAPI backend, model-tier routing, prompt management, structured logging, automated tests, containerisation and automated EC2 deployment are implemented.

The system is designed to continue evolving as Daniela develops the portfolio and gains more experience with production AI systems.
