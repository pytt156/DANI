# Taxi Price Prediction

## Summary

Taxi Price Prediction is an end-to-end machine learning project for predicting taxi fares from structured trip data.

The project was designed as an educational full-stack ML application with emphasis on correctness, reproducibility and clean software structure rather than maximum predictive performance.

It demonstrates the complete path from raw data and experimentation to a trained model, API-based inference and a user-facing frontend.

## Purpose

The project was created to explore how a machine learning model can be developed as part of a complete application rather than remaining inside a notebook.

The main goals were to:

- build a reproducible machine learning pipeline
- avoid data leakage
- separate experimentation from production code
- keep preprocessing consistent between training and inference
- expose predictions through an API
- create a simple frontend for interacting with the model
- structure the repository according to MLOps-oriented principles

## Project Context

This was an individual educational project.

Daniela built the complete workflow, including:

- exploratory data analysis
- data cleaning
- model comparison
- pipeline construction
- model serialization
- backend API
- frontend application
- project structure
- documentation

The project focused as much on software structure and reproducibility as on the machine learning model itself.

## Problem

Taxi prices depend on several characteristics of a trip.

The goal was to train a regression model that could estimate the expected price of a taxi journey from structured trip information.

The project also addressed a broader engineering question:

How should a small machine learning application be structured so that the model can be trained, saved, loaded and used consistently through an API and frontend?

## Machine Learning Workflow

The project followed an end-to-end workflow:

1. Explore the raw dataset.
2. Perform sanity checks and identify data-quality problems.
3. Clean the data.
4. Export a processed dataset.
5. Compare candidate models.
6. Evaluate model performance.
7. Build a reusable preprocessing and modeling pipeline.
8. Serialize the final pipeline.
9. Load the saved artifact during inference.
10. Expose predictions through FastAPI.
11. Connect a Streamlit frontend to the API.

## Project Structure

The repository separates experimentation, application code, data and model artifacts.

Main areas include:

- assets for documentation images and screenshots
- raw and processed data directories
- a models directory for the serialized pipeline
- notebooks for EDA, cleaning, evaluation and pipeline creation
- backend code under the source package
- frontend code under the source package
- shared utilities and constants
- dependency configuration through pyproject.toml and uv.lock

The backend, frontend and shared logic are separated into distinct modules.

## Data Structure

The project keeps raw and processed data in separate directories.

Raw data is treated as immutable.

Cleaning and transformation produce a separate processed dataset rather than modifying the original source data.

This makes the workflow easier to reproduce and reduces the risk of losing or unintentionally changing the original data.

## Exploratory Data Analysis

Exploratory work was carried out in a dedicated notebook.

The analysis included:

- inspecting the dataset structure
- checking feature types
- identifying missing or invalid values
- examining distributions
- checking for unrealistic observations
- understanding relationships between input features and taxi prices

The purpose of the notebook was exploration and decision-making.

Production application logic was kept outside the notebooks.

## Data Cleaning

Data cleaning was handled in a separate stage.

The workflow transformed the raw input into a processed dataset suitable for model training.

The separation between raw and processed data helped ensure that:

- the original source remained unchanged
- cleaning steps could be repeated
- training data could be inspected independently
- experimentation did not silently alter the source data

## Model Development

Several modeling approaches were tested and evaluated before selecting the final solution.

The project used scikit-learn for model development.

The emphasis was not solely on finding the highest possible score. The final solution also needed to be:

- understandable
- reproducible
- compatible with a complete preprocessing pipeline
- possible to serialize
- easy to use during inference

## Preprocessing Pipeline

The final model was stored as a complete scikit-learn pipeline.

The pipeline combined preprocessing and prediction logic into one reusable artifact.

This was an important design decision because the same preprocessing steps must be applied during both training and inference.

Keeping preprocessing inside the pipeline reduces the risk that:

- the frontend sends data in a different format
- the API applies different transformations
- training and inference use inconsistent logic
- feature ordering changes
- data leakage is introduced through manual processing

## Avoiding Data Leakage

Avoiding data leakage was one of the explicit goals of the project.

The project kept clear boundaries between:

- raw data
- processed data
- training
- evaluation
- saved model artifacts
- inference

Preprocessing was fitted only as part of the training workflow and later reused through the serialized pipeline.

This helped prevent information from the evaluation data from influencing model training.

## Model Artifact

The trained pipeline is stored in the models directory as taxi_price_predictor.joblib.

The artifact contains the preprocessing and prediction logic required during inference.

The backend loads this artifact and uses it to generate fare predictions.

## Backend

The backend was built with FastAPI.

Its main responsibilities were to:

- validate incoming prediction requests
- transform request data into the expected model input
- load the serialized model pipeline
- generate predictions
- return structured responses
- expose interactive API documentation through Swagger UI

The backend was divided into:

- API routes
- service logic
- request and response schemas

This helped keep the API entrypoint small and separated transport logic from prediction logic.

## Frontend

The frontend was built with Streamlit.

It allowed a user to enter trip information and request a predicted taxi price through a simple interface.

The frontend communicated with the FastAPI backend rather than loading the model directly.

This separation meant that:

- the frontend handled presentation and user input
- the backend handled validation and prediction
- the model remained isolated from the user interface
- the two components could be developed and changed independently

## Separation of Concerns

Separation of concerns was one of the main architectural goals.

The project separates:

- notebooks from production code
- raw data from processed data
- model training from model serving
- frontend logic from backend logic
- API routes from business logic
- schemas from service implementation
- shared utilities from application-specific code

The backend and frontend both use thin entrypoints with logic delegated to service modules.

This follows the single responsibility principle and makes the project easier to understand and maintain.

## Reproducibility

The project was structured to make results and application behaviour reproducible.

Reproducibility was supported by:

- immutable raw data
- separate processed data
- a serialized preprocessing and model pipeline
- versioned model artifacts
- pinned dependencies
- pyproject.toml
- uv.lock
- a clear project structure
- shared preprocessing between training and inference

The project can be installed using uv or pip and run locally through separate commands for the API and frontend.

## Dependency Management

The project uses pyproject.toml and uv.lock for dependency management.

This ensures that the development environment can be recreated with consistent dependency versions.

The package can also be installed in editable mode during development.

## Technologies

- Python 3.12
- scikit-learn
- pandas
- NumPy
- FastAPI
- Pydantic
- Streamlit
- joblib
- Jupyter
- uv
- Git
- GitHub

## Notebooks

The project contains four main notebooks.

### Exploratory Data Analysis

The first notebook is used for dataset exploration and sanity checks.

### Data Cleaning

The second notebook handles cleaning and exports the processed dataset.

### Model Testing and Evaluation

The third notebook compares models and evaluates their performance.

### Pipeline Creation

The fourth notebook builds and serializes the final preprocessing and prediction pipeline.

The notebooks are used for experimentation and model development only.

Application logic is kept in the source package.

## Key Design Decisions

### Keep Notebooks Out of Production Logic

Notebooks were used to investigate data and compare models, but the final application does not depend on notebook execution.

This prevents the production workflow from becoming tied to hidden notebook state or manually executed cells.

### Serialize the Complete Pipeline

The saved artifact contains both preprocessing and prediction logic.

This ensures that the same transformations are applied when the model is used through the API.

### Keep the Frontend Separate from the Model

The Streamlit application communicates with the FastAPI backend.

It does not load or run the trained model directly.

This makes the architecture closer to a real service-based application.

### Use Thin Entrypoints

The FastAPI and Streamlit entrypoints contain limited logic.

Most behaviour is moved into service modules and shared utilities.

This makes each component easier to test, replace and extend.

## Results

The completed project provides a functioning local application where:

- a user enters structured taxi-trip information
- the frontend sends the data to the API
- the backend validates the request
- the trained pipeline processes the input
- the model predicts a taxi price
- the result is returned and displayed to the user

The project also demonstrates a complete and reproducible ML workflow from data exploration to model serving.

## What Daniela Learned

The project strengthened Daniela's understanding of how machine learning work moves beyond experimentation.

Her main learning included:

- structuring an end-to-end ML repository
- separating training from inference
- keeping raw data immutable
- avoiding data leakage
- building reusable preprocessing pipelines
- serializing trained models
- loading model artifacts during inference
- exposing models through FastAPI
- connecting a Streamlit frontend to an API
- separating frontend, backend and shared logic
- managing dependencies with uv
- designing code around clear responsibilities

The project also reinforced the importance of consistency between training and production.

A model can perform well during experimentation but still fail in an application if preprocessing, feature order or input validation differs during inference.

## Challenges

One of the main challenges was deciding where different responsibilities should live.

A small ML project can easily become tangled if data processing, model logic, API routes and user-interface code are mixed together.

The project therefore required deliberate decisions about:

- which work belonged in notebooks
- which logic belonged in the source package
- how the backend should be divided
- how the frontend should communicate with the backend
- how preprocessing should be reused
- how the model artifact should be loaded

Another challenge was avoiding data leakage while still keeping the workflow practical and understandable.

## Limitations

The project is educational and is not intended to be production-ready.

Current limitations include:

- no automated monitoring
- no CI/CD pipeline
- no automated model retraining
- no production database
- no user authentication
- no rate limiting
- no production deployment configuration
- limited automated testing
- no drift detection
- no feature store
- no model registry
- no detailed error tracking

The model must also be retrained if the feature structure changes.

## What Could Be Improved

With more time, the project could be extended with:

- automated tests
- CI/CD through GitHub Actions
- Docker support
- cloud deployment
- model performance monitoring
- data-drift detection
- structured logging
- a model registry
- experiment tracking with MLflow
- automated retraining
- stronger API error handling
- input-range validation
- frontend usability improvements
- production security controls

A future version could also compare predictions over time and detect whether changes in trip data reduce model reliability.

## Use of LLMs

Large language models were used as supporting tools during development.

They were used for:

- documentation support
- image generation
- implementation guidance for routing

The machine learning workflow, project architecture and application structure remained the central educational work.

## Relevance to MLOps

The project demonstrates several core MLOps principles:

- reproducible environments
- versioned artifacts
- separation of experimentation and production code
- consistent preprocessing
- clear training and inference boundaries
- model serialization
- API-based model serving
- modular application architecture
- explicit limitations and future operational needs

Although it does not include monitoring, CI/CD or automated retraining, it provides a foundation for adding those capabilities later.

## Repository

Repository name: taxi-prediction-fullstack-daniela