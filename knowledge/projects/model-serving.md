# CIFAR-10 Training and Model Serving

## Summary

This project follows a CIFAR-10 image-classification model from training and experimentation to a containerized inference service.

Daniela first built a modular PyTorch training pipeline for a convolutional neural network and used validation-based experiments to select the final model.

The trained model was then reused in a collaborative model-serving project with Ömer Aytug. In that project, the model was exported to TorchScript, served through a FastAPI API and accessed through a separate Streamlit frontend.

Together, the two stages demonstrate the transition from model development to a usable machine-learning service.

## Project Context

The work was completed in two connected stages.

The first stage focused on model training:

* PyTorch model development
* dataset handling
* reproducible training
* hyperparameter experiments
* validation-based model selection
* checkpointing
* final test evaluation

The second stage focused on model serving:

* model artifact integration
* TorchScript export
* inference preprocessing
* FastAPI
* Streamlit
* Docker
* Docker Compose networking
* stateless API design
* collaborative Git development

The model produced during the training work became the starting point for the serving project rather than being treated as an unrelated model artifact.

## Dataset

The model was trained on CIFAR-10.

The dataset contains:

* 50,000 training images
* 10,000 test images
* 10 image classes
* 32 × 32 RGB images

The training data was further divided into training and validation sets.

The final configuration used 10% of the training data for validation.

## PyTorch Training Pipeline

Daniela structured the training work as a modular pipeline rather than keeping the full workflow in a single notebook or script.

The project separated responsibilities into components for:

* configuration
* dataset handling
* model architecture
* training
* evaluation
* utility functions

A main entrypoint ran the complete training pipeline, while a separate notebook was used for experiments.

The goal was to make training easier to reproduce, inspect and modify.

## Training Procedure

The model-selection process kept training, validation and final testing separate.

The workflow was:

1. Train the model on the training split.
2. Evaluate it against the validation split after each epoch.
3. Save a checkpoint when validation accuracy improves.
4. Load the best checkpoint after training.
5. Evaluate that model once against the test set.

The test set was not used to choose the model.

Model selection was based on validation performance.

This distinction was an important part of the project because repeatedly tuning against test results would make the final test score less meaningful.

## Experiments

Daniela experimented with several training parameters before choosing the final configuration.

The experiments included changes to:

* learning rate, from 0.1 down to 0.0001
* batch sizes of 16, 64 and 128
* training lengths between 5 and 25 epochs

The experiments showed several clear behaviours.

A learning rate of 0.1 was too high and the network remained close to random classification performance.

Very low learning rates produced much slower learning.

A batch size of 128 performed better in the experiments than the smaller alternatives.

Validation accuracy generally peaked around epochs 10–13 and could decline afterward, showing signs of overfitting and reinforcing the decision to save the best validation checkpoint rather than simply use the final epoch.

## Final Training Configuration

The selected configuration was:

* batch size: 128
* learning rate: 0.0005
* epochs: 15
* validation fraction: 0.1
* optimizer: Adam
* loss function: CrossEntropyLoss

The best model checkpoint was selected using validation accuracy.

The final test accuracy was:

`0.7140`

or approximately 71.4%.

The test accuracy was slightly below the best validation accuracy.

## Reproducibility

Reproducibility was a deliberate part of the training pipeline.

The project included:

* fixed Python random seeds
* fixed NumPy random seeds
* fixed PyTorch random seeds
* deterministic CUDA configuration
* reproducible train/validation splitting
* automatic device detection

The training code could detect and use CUDA, MPS or CPU depending on the available environment.

One practical challenge was ensuring that the training/validation split remained deterministic, which required explicitly controlling the random generator used during splitting.

Daniela also verified GPU execution during development rather than assuming that PyTorch was actually using the GPU.

## From Training to Serving

After completing the training pipeline, the next project focused on what happens after a model has been trained.

A model checkpoint by itself is not yet an application.

To make the classifier usable by another service or user, the project needed to handle:

* model serialization
* loading the model for inference
* consistent preprocessing
* input validation
* an API interface
* a user-facing client
* service networking
* reproducible runtime environments

The saved PyTorch model therefore became the input to the model-serving stage.

## Model Artifacts

The original trained weights are stored as:

`best_model.pt`

For serving, the model was exported to a separate TorchScript artifact:

`model.torchscript.pt`

The export process is handled separately from normal application startup.

The model architecture and original checkpoint are needed when generating the TorchScript artifact, but the running inference API loads the exported model directly using `torch.jit.load`.

This creates a clearer separation between the training artifact and the artifact used by the serving application.

## TorchScript

TorchScript was used to serialize the trained PyTorch model for inference.

The export step separates:

* model training
* saved PyTorch weights
* model architecture
* artifact export
* runtime inference

The serving API does not retrain the model or reconstruct the training process when it starts.

It loads the prepared inference artifact.

## Inference Preprocessing

The serving application applies the image transformations required by the trained model.

Images are:

1. resized to 32 × 32 pixels
2. converted to tensors
3. normalized using the CIFAR-10 mean and standard-deviation values

The normalization mean is:

* 0.4914
* 0.4822
* 0.4465

The standard deviation is:

* 0.2470
* 0.2435
* 0.2616

Keeping preprocessing consistent between training and inference is important because changing the input transformation can change how the model interprets incoming images.

## Model Serving Architecture

The serving application has three main layers:

1. Streamlit frontend
2. FastAPI inference service
3. PyTorch model loaded through TorchScript

The frontend and API run as separate services.

Streamlit handles user interaction while FastAPI owns the inference workflow.

The frontend does not load or execute the model directly.

## Prediction Flow

A prediction follows this sequence:

1. A user uploads an image through Streamlit.
2. Streamlit sends the image to the FastAPI service.
3. FastAPI receives and validates the uploaded file.
4. The image is resized and normalized.
5. The TorchScript model generates logits.
6. Softmax converts those logits into class probabilities.
7. The service selects the class with the highest probability.
8. FastAPI returns the class index, class label and confidence score.
9. Streamlit displays the result.

The complete prediction flow was tested from image upload through returned model response.

## FastAPI Service

The inference backend is implemented with FastAPI.

It exposes two main endpoints.

### Health

`GET /health`

This returns a simple status response:

`{"status": "ok"}`

The endpoint can be used to verify that the API is available.

### Prediction

`POST /predict`

The endpoint accepts an uploaded image as multipart form data.

Supported input formats include:

* JPG
* JPEG
* PNG

A successful response includes:

* predicted class index
* predicted class label
* confidence score

The API is stateless.

Uploaded images, predictions and user sessions are not persisted between requests.

Each inference request is handled independently.

## Streamlit Frontend

Streamlit provides a simple interface for interacting with the model.

A user can:

* upload an image
* preview it
* submit it for prediction
* see the predicted CIFAR-10 class
* see the confidence score
* inspect the raw API response

The frontend communicates with the FastAPI service over HTTP rather than accessing the PyTorch model itself.

## Docker and Service Separation

The serving application is containerized with Docker.

FastAPI and Streamlit run in separate containers.

Docker Compose is used to:

* build the services
* start the containers
* connect them through an internal network
* provide consistent runtime environments

Within the Docker Compose network, the Streamlit service communicates with FastAPI using the backend service rather than a locally loaded model.

This keeps responsibilities separated:

* Streamlit handles presentation
* FastAPI handles inference
* PyTorch handles prediction

The application was designed to run on CPU, so no GPU infrastructure is required for serving the model.

## Collaboration

The model-serving stage was completed collaboratively by Daniela Algerydh and Ömer Aytug.

Development used feature branches and pull requests rather than direct development on the main branch.

The main branch was protected and pull requests required review before merging.

The workflow included:

* creating focused feature branches
* implementing and verifying changes
* opening pull requests
* reviewing each other's work
* updating branches when required
* resolving merge conflicts
* merging after approval

Working on related features in parallel also created practical experience with branch synchronization and merge conflicts.

## Daniela's Work

Daniela developed the original PyTorch training pipeline and trained the CIFAR-10 model used as the basis for the later serving work.

Her training work included:

* modular training code
* data handling
* validation-based model selection
* checkpointing
* hyperparameter experiments
* reproducibility
* final evaluation

In the collaborative serving stage, her work included project integration, application development, containerized service design, pull-request collaboration, verification and documentation.

The combined work gave her experience across both model development and model serving rather than only one side of the workflow.

## Verification

The serving system was verified through:

* the health endpoint
* manual image uploads
* direct API requests
* Swagger UI
* Streamlit
* command-line requests
* container startup checks

The prediction endpoint verified the full path from uploaded image to returned prediction.

## Challenges and Learning

### Model Selection

The training experiments demonstrated why model selection should use validation data rather than the final test set.

They also showed how learning rate, batch size and training duration can materially affect model behaviour.

### Reproducibility

Producing a deterministic train/validation split required more than setting a single global seed.

The project reinforced the need to control randomness throughout the training pipeline.

### Overfitting

Longer training showed validation performance peaking and then declining.

This made validation-based checkpointing more useful than simply saving the model from the final epoch.

### Training versus Inference

Moving the same model into a serving project made the distinction between training and inference concrete.

The serving system does not need the complete experiment environment.

Instead it needs a stable model artifact, deterministic preprocessing and a predictable inference interface.

### TorchScript Export

The original architecture and weights needed to be loaded correctly before generating the TorchScript model.

The exported artifact then had to be verified to ensure it produced valid predictions.

### Container Networking

Separating Streamlit and FastAPI meant the services had to communicate correctly through Docker networking.

This required working with:

* internal service names
* container addresses
* exposed ports
* startup behaviour

### Collaborative Development

Feature-branch development and pull requests introduced practical issues such as branches falling behind main and merge conflicts when several connected features changed simultaneously.

## Technologies

The combined project used:

* Python
* PyTorch
* TorchScript
* FastAPI
* Streamlit
* Docker
* Docker Compose
* Pydantic
* Pillow
* uv
* Git
* GitHub
* NumPy

## Limitations

The project is educational rather than a production deployment.

The serving application does not currently include features such as:

* authentication
* rate limiting
* production monitoring
* metrics collection
* model registry integration
* drift detection
* automated deployment
* autoscaling
* automated performance testing

Input validation is also limited compared with what would be appropriate for an internet-facing production service.

The CIFAR-10 model was primarily used to explore the training and serving workflow rather than maximize state-of-the-art classification accuracy.

## Possible Improvements

The training side could be extended with:

* data augmentation
* dropout or weight decay
* learning-rate scheduling
* deeper architectures such as ResNet
* better experiment logging
* automated training checks

The serving side could be extended with:

* stronger file validation
* upload-size limits
* structured logging
* metrics and tracing
* latency monitoring
* model-version metadata
* automated tests
* CI for linting and container builds
* cloud deployment
* quantization
* batch inference
* automated health and readiness checks

## Use of LLMs

Large language models were used as development support during both stages.

They were used for tasks such as:

* reviewing code and project structure
* debugging environment problems
* discussing reproducibility
* validating experimental approaches
* documentation support

Hyperparameter choices and final model selection were based on the actual experiment results.

Implementation, integration and verification were performed by the project participants.

## Relevance to MLOps

The combined project demonstrates a larger part of the machine-learning lifecycle than either stage does alone.

It includes:

`data -> training -> validation -> model selection -> checkpoint -> inference artifact -> API -> containerized service -> client`

Relevant MLOps concepts include:

* reproducible training
* separation of train, validation and test data
* experiment-driven model selection
* model checkpointing
* separation of training and inference
* serialized model artifacts
* consistent preprocessing
* API-based model serving
* stateless inference
* reproducible runtime environments
* containerized services
* service isolation
* internal networking
* collaborative Git workflows

The project helped Daniela understand not only how to train a model, but how to turn a trained model into a service that another application can actually use.

## Repositories

Training pipeline:

`pytorch-training-pipeline`

Model-serving application:

`mlops-model-serving`

## Collaborators

Model-serving stage:

* Daniela Algerydh
* Ömer Aytug
