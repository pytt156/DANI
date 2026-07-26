# Morpheus

## Summary

Morpheus is an ongoing private AI-assistant project built as a personal and family-facing web application.

The system combines a FastAPI backend, a Node.js-based frontend, Google OAuth authentication, an OpenAI-powered assistant and a prepared retrieval-augmented generation architecture.

The assistant is designed with a personal and sarcastic tone rather than a neutral corporate personality.

The core application works, the database and RAG infrastructure are prepared and retrieval functions correctly. The main remaining task is to ingest the complete document collection into the knowledge base.

## Purpose

The purpose of Morpheus is to create a private AI assistant that Daniela and Andreas can access through a protected web interface.

The system is intended to provide a more personal experience than a standard chatbot.

Its goals include:

- providing a private authenticated AI assistant
- giving the assistant a distinct personality
- allowing Daniela and Andreas to access it through their own accounts
- creating a foundation for personal and household knowledge
- preparing a complete RAG pipeline
- keeping backend, frontend, authentication and AI logic separated
- deploying the system in a real cloud environment

## Project Status

Morpheus is an ongoing project.

The following parts are working or prepared:

- FastAPI backend
- Node.js-based frontend
- Google OAuth login
- authenticated access
- OpenAI assistant integration
- defined assistant personality
- AWS EC2 deployment
- database setup
- RAG architecture
- retrieval functionality
- prepared knowledge-base ingestion flow

The main unfinished part is the full ingestion of the personal document collection.

## Project Context

Morpheus is an individual project created by Daniela.

It was built as a more ambitious personal application rather than as a small isolated school exercise.

The project combines several areas:

- backend development
- frontend development
- authentication
- cloud deployment
- AI integration
- database design
- retrieval-augmented generation
- application security
- user experience

## User Experience

The application begins with a website-style interface.

The outer interface was designed more like a personal website or blog than a direct chatbot landing page.

From the main website, a user can navigate to Morpheus.

Before accessing the assistant, the user must log in through Google OAuth.

The login acts as an access-control layer.

Approved users, primarily Daniela and Andreas, can then enter the private assistant interface and begin asking questions.

## Authentication

Morpheus uses Google OAuth for login.

Authentication is primarily used as access protection.

The purpose is to prevent the private assistant and future personal knowledge base from being publicly accessible.

The system distinguishes between authenticated and unauthenticated users.

Only authenticated users are allowed to access the assistant.

## Users

The intended users are Daniela and Andreas.

The login system provides protected access for both users.

The authentication layer is currently primarily about controlling access rather than creating completely separate personal data environments.

## Assistant Personality

Morpheus was intentionally designed with a distinct personality.

The tone is:

- personal
- direct
- sarcastic
- conversational
- less formal than a standard assistant

The goal was to make the assistant feel like a consistent character rather than a generic interface to a language model.

The personality is defined through instructions that guide how the assistant responds.

## OpenAI Integration

The assistant uses OpenAI for language-model responses.

The model receives instructions that define the Morpheus personality and response style.

The integration allows the assistant to:

- receive user questions
- respond conversationally
- maintain the intended tone
- use retrieved context when relevant
- operate as part of the authenticated web application

## Backend

The backend is built with FastAPI.

The backend is responsible for:

- receiving requests from the frontend
- validating requests
- handling authenticated access
- communicating with OpenAI
- connecting to the database
- executing retrieval logic
- returning responses to the frontend

FastAPI provides the central application layer between the user interface, authentication, model integration and data systems.

## Frontend

The frontend is built in a Node.js-based environment.

The exact frontend framework is not documented with certainty in the current project summary.

The frontend provides:

- the main website or blog-style interface
- navigation to Morpheus
- Google login
- access control
- the assistant chat interface
- user input
- assistant responses

The frontend communicates with the FastAPI backend rather than accessing the model or database directly.

## Cloud Deployment

Morpheus has been deployed to AWS EC2.

The deployment allowed Daniela to run the assistant in a real remote environment instead of only locally.

The EC2 deployment included:

- running the backend service
- hosting the AI integration
- accessing the application remotely
- working with Linux through the terminal
- inspecting and managing the running environment

The deployed OpenAI assistant responded correctly and followed the defined personality instructions.

## Database

The database infrastructure is complete and prepared.

It is designed to support:

- stored application data
- retrieval documents
- chunk metadata
- vector data
- future knowledge-base growth

The database side of the project is not only conceptual.

It has been configured and connected to the application architecture.

## Retrieval-Augmented Generation

Morpheus includes a functioning RAG pipeline.

The retrieval process is prepared to:

- ingest documents
- divide content into chunks
- create vector representations
- store document data
- retrieve relevant context
- pass retrieved information to the assistant
- generate grounded responses

The RAG system itself works.

The incomplete part is the ingestion of the full intended document collection.

## Knowledge Base

The knowledge-base architecture is prepared.

The database, retrieval logic and ingestion flow are in place.

However, the complete set of personal and household documents has not yet been ingested.

This means the system has a functioning foundation for knowledge retrieval but does not yet contain the final intended breadth of personal information.

## Current End-to-End Flow

The functioning application flow is:

1. The user opens the website.
2. The user navigates to Morpheus.
3. The user logs in through Google OAuth.
4. The application verifies access.
5. The user submits a question.
6. The frontend sends the request to FastAPI.
7. The backend processes the request.
8. Relevant context can be retrieved through the RAG pipeline.
9. The question and context are sent to the OpenAI assistant.
10. The assistant responds using the defined personality.
11. The response is returned to the frontend.
12. The user sees the answer in the chat interface.

## Architecture

The application is separated into several layers:

- website and frontend
- authentication
- FastAPI backend
- OpenAI integration
- database
- RAG pipeline
- deployment environment

This separation makes the project easier to extend and allows each responsibility to evolve independently.

## Technologies

- Python
- FastAPI
- Node.js
- Google OAuth
- OpenAI
- retrieval-augmented generation
- vector search
- database storage
- AWS EC2
- Linux
- Git
- GitHub

## Key Design Decisions

### Protected Access

The assistant is not publicly available.

Google OAuth is used to restrict access to approved users.

This is important because the system is intended to contain personal and household information.

### Separate Frontend and Backend

The user interface and application logic are separated.

The frontend handles presentation and interaction.

The FastAPI backend handles authentication-aware requests, AI communication, retrieval and data access.

### Defined Personality

The assistant was given a clear personal and sarcastic tone.

This makes the experience more distinctive and gives the system a consistent identity.

### Prepare RAG Before Full Ingestion

Daniela built the complete retrieval architecture before adding the full document collection.

This allowed the technical flow to be verified independently from the final knowledge-base content.

### Real Cloud Deployment

The project was deployed to AWS EC2 rather than remaining only as a local prototype.

This created practical experience with remote application environments and Linux-based service management.

## Challenges

### Combining Several Application Layers

Morpheus required multiple systems to work together:

- frontend
- backend
- authentication
- AI model
- database
- retrieval
- cloud deployment

The challenge was not only implementing each component but ensuring that the full request flow worked.

### Authentication

Google OAuth introduced a need to manage:

- login flow
- authenticated sessions
- protected routes
- frontend and backend coordination
- access control

### Cloud Deployment

Running the application on EC2 required Daniela to work with:

- remote Linux environments
- service startup
- environment variables
- application availability
- logs
- network configuration

### Personality Consistency

The assistant needed to follow the intended personal and sarcastic tone without becoming unhelpful or inconsistent.

This required careful personality instructions and testing.

### RAG Preparation

The retrieval architecture needed to be completed before the knowledge base itself was populated.

This involved separating:

- database setup
- ingestion
- chunking
- vector storage
- retrieval
- answer generation

## Results

The project reached a functioning state where:

- the assistant could run on AWS EC2
- users could access the application remotely
- Google login protected the assistant
- the OpenAI assistant followed the defined personality
- the frontend communicated with the FastAPI backend
- the database was prepared
- the RAG pipeline worked
- document ingestion was technically supported

The main remaining work is to ingest and organise the complete document collection.

## What Daniela Learned

Morpheus gave Daniela practical experience with building a more complete AI product.

Her main learning included:

- designing a private AI assistant
- defining and testing an assistant personality
- building a FastAPI backend
- connecting a frontend to an API
- implementing Google OAuth
- protecting application access
- deploying an AI service to AWS EC2
- working with Linux remotely
- preparing a database for RAG
- building a functioning retrieval pipeline
- separating infrastructure from knowledge content
- thinking about privacy in personal AI systems

## Difference from Wired-AI

Morpheus and Wired-AI both include retrieval and language-model integration, but they solve different problems.

Wired-AI is a workplace onboarding assistant focused on internal company knowledge, sources and escalation guidance.

Morpheus is a private personal assistant focused on authenticated access, personality, personal use and future household knowledge.

Morpheus places greater emphasis on:

- private access
- Google authentication
- personal tone
- cloud deployment
- long-term personal use
- household and personal data

## Limitations

The project is not complete.

Current limitations include:

- the full document collection has not been ingested
- the knowledge base is not yet comprehensive
- user-specific data separation is limited
- monitoring is limited
- automated tests are limited
- production security could be strengthened
- frontend details and framework documentation should be clarified
- deployment automation could be improved
- backup and recovery procedures are not fully documented

## Planned Improvements

The next major step is to ingest the intended personal and household documents.

Further improvements could include:

- automated document ingestion
- document management through the interface
- separate knowledge contexts for Daniela and Andreas
- improved permissions
- conversation history
- source references in responses
- document update and deletion
- structured logging
- monitoring
- automated tests
- CI/CD
- backup routines
- stronger production security
- improved frontend design
- clearer deployment documentation
- containerization
- infrastructure as code

## Relevance to MLOps and LLMOps

Morpheus demonstrates several areas relevant to MLOps and LLMOps:

- AI application architecture
- model integration
- prompt and personality design
- API-based AI access
- authentication
- cloud deployment
- database integration
- RAG infrastructure
- retrieval pipelines
- operational access control
- separation of application components

The project shows Daniela's interest in the entire AI-system lifecycle, not only the model response itself.

## Repository

Project name: Morpheus

Status: Ongoing