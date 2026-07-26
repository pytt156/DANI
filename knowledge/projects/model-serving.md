# CIFAR-10 Image Classification Service

## Summary

CIFAR-10 Image Classification Service is a containerized machine learning application for serving image predictions from a trained PyTorch convolutional neural network.

The project demonstrates how a trained model can be exported, loaded for inference, exposed through a FastAPI service and accessed through a separate Streamlit interface.

The application is divided into two isolated services that run in separate Docker containers and communicate over an internal network.

## Purpose

The purpose of the project was to move beyond model training and focus on model serving, integration and deployment structure.

The main goals were to:

- serve a trained PyTorch model through an API
- keep preprocessing consistent during inference
- separate the user interface from the inference service
- containerize the complete application
- create a stateless API
- use a collaborative Git workflow
- structure the project in a way that resembles a small production service

## Project Context

This was a collaborative educational project completed by Daniela Algerydh and Ömer Aytug.

The work was divided through feature branches and pull requests.

The main development areas included:

- model integration
- TorchScript export
- FastAPI inference service
- Streamlit frontend
- Docker containerization
- Docker Compose networking
- project configuration
- documentation
- testing and verification

## Problem

A trained machine learning model is not directly useful to an end user.

It needs a reliable inference workflow, input validation, preprocessing, a service interface and a way for another application or user to access the result.

This project addressed the question:

How can a trained PyTorch image-classification model be converted into a reusable, containerized service with a separate user interface?

## Architecture

The system consists of three main layers:

1. A Streamlit user interface
2. A FastAPI inference service
3. A PyTorch model loaded through TorchScript

The Streamlit application accepts an uploaded image and sends it to the FastAPI service.

The FastAPI service validates and preprocesses the image, runs inference through the PyTorch model and returns the predicted class together with a confidence score.

The frontend and backend run in separate Docker containers.

## Service Design

### Streamlit Frontend

The frontend is responsible for:

- accepting image uploads
- displaying an image preview
- sending the image to the API
- displaying the predicted label
- displaying the confidence score
- showing the raw JSON response when requested

The frontend does not load the machine learning model directly.

It communicates with the inference service over HTTP.

### FastAPI Inference Service

The FastAPI service is responsible for:

- exposing health and prediction endpoints
- receiving uploaded image files
- validating the request
- preprocessing the image
- loading the TorchScript model
- running inference
- calculating confidence
- returning structured JSON

The API is stateless.

Each request contains everything needed for the prediction, and the service does not depend on user sessions or stored request state.

### PyTorch Model

The trained convolutional neural network performs image classification on the CIFAR-10 classes.

The original trained weights are stored separately from the exported TorchScript model.

The TorchScript artifact is used during inference.

## System Flow

The application follows this sequence:

1. The user uploads an image through Streamlit.
2. The frontend sends the image as a multipart request.
3. FastAPI receives and validates the file.
4. The image is resized and normalized.
5. The TorchScript model generates logits.
6. Softmax converts the output into class probabilities.
7. The service selects the most likely class.
8. The API returns the class index, label and confidence.
9. Streamlit displays the result.

## Model Details

The model is a convolutional neural network trained on CIFAR-10.

The model architecture is defined in the application code and used during TorchScript export.

The original model weights are stored as:

- best_model.pt

The exported inference artifact is stored as:

- model.torchscript.pt

The inference service loads the scripted model using torch.jit.load.

## TorchScript Export

TorchScript was used to convert the trained PyTorch model into a serialized artifact suitable for inference.

The export process is handled through a dedicated script.

This separates:

- the original training artifact
- the model architecture
- the export step
- the final inference artifact

The original weights are only required when generating the TorchScript model.

The running API uses the exported TorchScript artifact.

## Preprocessing

The inference pipeline applies the same image transformations expected by the trained model.

The preprocessing steps are:

- resize the image to 32 by 32 pixels
- convert the image to a tensor
- normalize using the CIFAR-10 mean values
- normalize using the CIFAR-10 standard deviation values

The normalization values are:

- mean: 0.4914, 0.4822, 0.4465
- standard deviation: 0.2470, 0.2435, 0.2616

Using consistent preprocessing is essential because the model was trained on data prepared with the same transformation logic.

## Confidence Calculation

The model produces logits rather than direct probabilities.

Softmax is applied to convert the logits into class probabilities.

The highest probability is returned as the confidence score.

The response contains:

- predicted class index
- predicted class label
- confidence score

## API Endpoints

## Health Endpoint

The health endpoint is available at:

GET /health

It returns a simple status response confirming that the API is running.

Expected response:

{"status": "ok"}

This endpoint can be used for:

- manual verification
- container health checks
- deployment checks
- monitoring integrations

## Prediction Endpoint

The prediction endpoint is available at:

POST /predict

It accepts an uploaded image through multipart form data.

Supported formats include:

- JPG
- JPEG
- PNG

A successful response contains:

- predicted_index
- predicted_label
- confidence

Example response:

{
  "predicted_index": 3,
  "predicted_label": "cat",
  "confidence": 0.87
}

## Frontend

The Streamlit interface provides a simple manual testing environment for the model-serving API.

The user can:

- upload an image
- preview the selected file
- send the image for prediction
- view the predicted class
- view the confidence score
- inspect the raw API response

The frontend communicates with the FastAPI service through the prediction endpoint.

## Containerization

The application is containerized using Docker.

The frontend and backend run in separate containers.

Docker Compose is used to:

- build both services
- start both containers
- connect them through an internal network
- manage service startup
- provide a consistent local environment

The service separation demonstrates how the interface and inference layer can be deployed and managed independently.

## Docker Networking

The Streamlit container communicates with the FastAPI container through the Docker Compose network.

This means that the frontend does not need to access the model directly.

The internal service connection keeps the responsibilities separated:

- Streamlit handles presentation
- FastAPI handles inference
- PyTorch handles prediction

## Stateless API Design

The inference API is stateless.

It does not store uploaded images, predictions or user sessions between requests.

This design makes the service easier to:

- scale horizontally
- restart
- test
- replace
- deploy behind a load balancer

Each prediction request is handled independently.

## CPU-Compatible Runtime

The application is designed to run on CPU.

This makes local development and testing easier and avoids requiring GPU infrastructure.

The model is small enough to support practical inference in a CPU-based environment.

## Project Structure

The project is organised into:

- application code
- model artifacts
- export scripts
- frontend code
- Docker configuration
- project dependencies
- documentation assets

The main application package includes:

- configuration
- FastAPI entrypoint
- model architecture
- model loading
- preprocessing
- inference logic

The TorchScript export logic is kept in a separate script.

## Separation of Responsibilities

The project separates several concerns clearly.

### Configuration

Class labels and shared configuration are stored separately from application logic.

### API Entrypoint

The FastAPI entrypoint defines the service and routes.

### Model Architecture

The original architecture is kept in a dedicated module and is primarily used during export.

### Inference Logic

Model loading, preprocessing and prediction are handled separately from the API route definitions.

### Frontend

The Streamlit interface is separated from the backend service and model logic.

### Export Logic

TorchScript conversion is performed through a dedicated script rather than during normal application startup.

## Technologies

- Python
- PyTorch
- TorchScript
- FastAPI
- Streamlit
- Docker
- Docker Compose
- Pydantic
- Pillow
- uv
- Git
- GitHub

## Development Process

The project used a feature-branch workflow.

Changes were developed in separate branches and integrated through pull requests.

The main branch was protected, and pull request reviews were required before merging.

Key development areas included:

- model integration
- containerization
- frontend integration

This workflow helped the collaborators review changes and keep the main branch stable.

## Pull Request Workflow

The pull request process required each collaborator to:

- create a dedicated feature branch
- implement and verify the change
- push the branch
- open a pull request
- review changes
- resolve conflicts when necessary
- merge only after approval

This created practical experience with collaborative software development rather than working directly on the main branch.

## Merge Conflicts and Branch Management

One challenge was keeping feature branches synchronized with the main branch.

When several related changes were developed at the same time, outdated branches could create merge conflicts.

The team handled this through:

- regularly updating branches
- rebasing when required
- reviewing changed files
- resolving conflicts before merging
- using pull requests to make integrations visible

This reinforced the importance of small, focused branches and frequent synchronization.

## Verification

The system was verified through:

- the health endpoint
- manual image uploads
- API requests
- Swagger UI
- Streamlit testing
- command-line requests
- container startup checks

The health endpoint confirmed that the API was available.

The prediction endpoint confirmed that the complete flow from image upload to model response worked.

## Running the Application

The complete application can be built and started through Docker Compose.

After startup:

- the FastAPI service is available on port 8000
- the Streamlit interface is available on port 8501

The user can interact with the system through the browser or call the API directly.

## Key Design Decisions

### Use TorchScript for Inference

The trained PyTorch model was exported to TorchScript.

This created a dedicated inference artifact and reduced the dependency on rebuilding the original training setup during application startup.

### Separate Frontend and Backend

The frontend and inference service run as separate applications.

This keeps user-interface concerns separate from model-serving concerns.

### Use Docker Compose

Docker Compose provides a reproducible way to run both services together.

It also demonstrates service discovery and internal networking.

### Keep the API Stateless

The API does not retain data between requests.

This makes the service simpler and easier to scale.

### Keep Preprocessing Close to Inference

The required image transformations are part of the inference logic.

This reduces the risk that clients preprocess images inconsistently.

## Results

The completed project provides a functioning image-classification service.

The application can:

- start through Docker Compose
- expose a health endpoint
- receive uploaded images
- preprocess the input consistently
- run inference through a TorchScript model
- return a predicted class
- return a confidence score
- display results in Streamlit
- run frontend and backend in isolated containers

The full flow from user upload to model response was functional.

## Daniela's Contribution

Daniela contributed to the collaborative development of the service.

Her work included project integration, application development, containerized service design, pull request collaboration, verification and documentation.

The project gave her practical experience with combining a previously trained model with a complete serving architecture.

## What Daniela Learned

The project strengthened Daniela's understanding of the difference between training a model and serving one.

Her main learning included:

- exporting PyTorch models to TorchScript
- loading serialized models for inference
- keeping preprocessing consistent
- building inference endpoints with FastAPI
- accepting multipart file uploads
- returning structured prediction responses
- calculating confidence from logits
- creating a separate Streamlit client
- containerizing multiple services
- configuring communication between containers
- designing stateless APIs
- collaborating through pull requests
- handling merge conflicts

The project also demonstrated that model serving includes much more than calling a prediction function.

The complete system must manage input, validation, preprocessing, artifacts, networking, runtime configuration and user interaction.

## Challenges

### Model Integration

The model had originally been created in a previous assignment.

Integrating it into a new serving project required understanding:

- the architecture
- the saved weights
- the expected input shape
- the preprocessing requirements
- the output format
- how to export it safely

### TorchScript Export

The model architecture and original weights needed to be loaded correctly before export.

The team also needed to verify that the exported artifact produced valid predictions during inference.

### Container Communication

The frontend and backend had to communicate correctly while running in separate containers.

This required understanding:

- Docker networking
- internal service names
- exposed ports
- local versus container addresses
- startup order

### Collaborative Integration

Working in parallel created a need for clear branch boundaries, frequent updates and pull request reviews.

Merge conflicts became part of the practical learning.

## Limitations

The project is educational and not production-ready.

Current limitations include:

- limited input validation
- no authentication
- no rate limiting
- no persistent logging
- no structured monitoring
- no metrics collection
- no CI pipeline for container builds
- no automated deployment
- no model registry
- no model version endpoint
- no drift detection
- no automated performance testing
- limited model optimization
- fixed configuration values
- no GPU-specific runtime

The reused CIFAR-10 model was not heavily optimized for accuracy or inference performance.

## What Could Be Improved

Future improvements could include:

- stronger file validation
- maximum upload-size limits
- structured error responses
- structured logging
- Prometheus-compatible metrics
- request tracing
- latency monitoring
- model-version metadata
- environment-based configuration
- automated tests
- CI for linting and container builds
- automated image scanning
- deployment to a cloud environment
- autoscaling
- model performance optimization
- quantization
- batch inference
- improved frontend feedback
- support for additional image formats
- production-ready health and readiness checks

The model itself could also be improved through:

- architecture experimentation
- additional training
- data augmentation
- hyperparameter tuning
- calibration analysis
- evaluation of confidence reliability

## Use of LLMs

Large language models were used as development support.

They assisted with:

- reviewing project structure
- clarifying architectural decisions
- debugging environment problems
- refining documentation

All implementation, integration and verification were performed manually by the project collaborators.

## Relevance to MLOps

The project demonstrates several important MLOps concepts:

- separation of training and inference
- serialized model artifacts
- reproducible runtime environments
- API-based model serving
- consistent preprocessing
- containerized services
- service isolation
- internal networking
- stateless inference
- collaborative development
- deployment-oriented architecture

It focuses on the transition from a trained model to a usable service.

## Repository

Repository name: mlops-model-serving

## Collaborators

- Daniela Algerydh
- Ömer Aytug