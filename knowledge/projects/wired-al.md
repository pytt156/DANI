# Wired-AI

## Summary

Wired-AI is an AI-powered onboarding assistant designed to help new employees and internal staff find reliable information without depending entirely on senior colleagues.

The system uses retrieval-augmented generation to answer questions from a company knowledge base. Each response includes the generated answer, relevant sources and documents, and an escalation recommendation indicating whether the user should proceed independently, ask a teammate or escalate the issue to a supervisor.

Wired-AI was developed as the final project in an LLMOps course by Daniela and two other students.

## Problem

Employee onboarding is often inconsistent and difficult to manage.

Important information may be spread across documents, internal systems and the knowledge of experienced employees. New employees may not know where to look, while senior colleagues repeatedly spend time answering the same questions.

The group wanted to create a system that could:

- give new employees faster access to internal knowledge
- provide more consistent onboarding support
- reduce repetitive questions directed at senior staff
- help users understand when they could act independently
- identify when a question required support from a colleague or supervisor
- improve the conditions for a new employee to succeed

The goal was not to remove human support, but to use it more effectively.

## Project Context

Wired-AI was created as the concluding group project in an LLMOps course.

The project team consisted of three students.

The team organised the work through GitHub issues and divided responsibilities across:

- project setup
- backend development
- API endpoints
- frontend development
- RAG and retrieval
- company knowledge base
- agent logic
- evaluation
- MLflow
- Docker
- deployment preparation
- documentation
- fallback behaviour
- demonstration and presentation

## Daniela's Role

Daniela's main responsibilities were:

- building the RAG pipeline
- implementing retrieval logic
- creating the company knowledge base
- developing the model and agent logic
- implementing schemas and fallback behaviour
- contributing to the Streamlit frontend
- contributing to documentation
- contributing to MLflow integration and evaluation

Her work covered much of the flow between the company documents, retrieval system and generated answer.

She was also involved in the escalation logic, which became one of the project's defining features.

## User Experience

The user entered a work-related question through the application.

The system returned:

- a direct answer
- relevant sources
- retrieved documents
- an escalation recommendation
- an explanation for the recommendation

The escalation recommendation used one of three levels:

1. **Proceed**
2. **Ask a teammate**
3. **Escalate to a supervisor**

This gave the user more than a generated answer. It also provided guidance about how much confidence and authority the user should place in that answer.

## Escalation Guidance

The escalation guidance was designed to help users decide what to do next.

### Proceed

The user could continue independently when the retrieved information was sufficiently clear and the question involved a low-risk or routine decision.

### Ask a Teammate

The user was advised to ask a colleague when the available information was useful but potentially incomplete, ambiguous or dependent on local context.

### Escalate to a Supervisor

The system recommended escalation when the question involved greater uncertainty, risk, responsibility or a decision that should not be made independently.

Each recommendation was accompanied by reasoning rather than only a label.

This made the system more cautious and practically useful than a chatbot that simply returned an answer without considering what the user should do with it.

## Architecture

The application followed a retrieval-augmented generation workflow:

1. Company documents were processed into searchable text.
2. The text was divided into smaller chunks.
3. Embeddings were created for the chunks.
4. The embeddings and document metadata were stored in a vector database.
5. The user's question was embedded.
6. Relevant chunks were retrieved using semantic search.
7. The retrieved context was provided to the language model.
8. The model generated a grounded answer.
9. The system generated an escalation recommendation and explanation.
10. The application displayed the answer, sources, documents and guidance to the user.

## Knowledge Base

Daniela created the initial company knowledge base used by the system.

The knowledge base was designed to represent internal documentation that a new employee might need during onboarding.

The work included:

- selecting and structuring the documents
- preparing text for ingestion
- dividing documents into chunks
- preserving source information
- creating embeddings
- storing document chunks in LanceDB
- retrieving relevant information for user questions

The knowledge base was static in the final version of the project.

The system did not yet include a user-facing workflow for uploading and ingesting new documents after deployment.

## Retrieval-Augmented Generation

The RAG pipeline used semantic retrieval to find relevant information from the company knowledge base.

Daniela worked with the complete RAG process, including:

- document ingestion
- text preparation
- chunking
- embeddings
- vector storage
- semantic search
- retrieved context
- grounded response generation
- source attribution

The project gave her practical experience of how decisions about chunk size, document structure and retrieval affect the final answer.

## Model and Agent Logic

The model logic was responsible for generating both the onboarding answer and the escalation guidance.

Structured schemas were used to make the model output predictable and easier for the application to handle.

Fallback behaviour was also implemented so that the system could respond more safely when:

- relevant information could not be found
- the retrieved context was insufficient
- the response did not match the expected schema
- the question required human judgement

This was important because the application was intended to guide new employees, not simply generate plausible-sounding text.

## MLflow and LLMOps

MLflow was used as part of the project's LLMOps workflow.

The team used it for:

- experiment tracking
- prompt registration
- evaluation
- logging
- comparing results
- LLM-as-a-judge evaluation

The team also worked with a shared deployed MLflow database so that the members could log and inspect live experiment results from their own environments.

This was one of the more difficult technical parts of the project.

It required the team to think beyond a local prototype and create a shared workflow where experiments, prompts and evaluation results could be accessed consistently.

## Evaluation

The project included evaluation of the generated answers and model behaviour.

An LLM-as-a-judge approach was used as one part of the evaluation process.

The evaluation workflow was intended to assess areas such as:

- answer relevance
- answer quality
- use of retrieved context
- grounding
- escalation behaviour
- prompt performance

Evaluation results and experiments were logged through MLflow.

This allowed the team to compare changes rather than relying only on subjective manual testing.

## Backend

The backend was built using FastAPI.

It handled:

- API endpoints
- request and response schemas
- model interaction
- retrieval
- escalation logic
- communication with the frontend
- fallback behaviour

Pydantic and PydanticAI were used for validation and structured model output.

## Frontend

The user interface was built with Streamlit.

Daniela contributed to the frontend alongside her work on the RAG and model logic.

The frontend allowed users to:

- enter onboarding questions
- view generated answers
- inspect source material
- see retrieved documents
- receive escalation guidance
- read the reasoning behind the recommendation

## Technologies

- Python
- FastAPI
- Streamlit
- Pydantic
- PydanticAI
- LanceDB
- Cohere multilingual embeddings
- MLflow
- Docker
- Docker Compose
- Git
- GitHub

## Most Challenging Parts

### Shared MLflow Environment

One of the most difficult parts was setting up MLflow in a way that allowed all team members to log experiments and push results to the same live environment.

This introduced challenges involving:

- remote services
- shared configuration
- database deployment
- environment variables
- team access
- consistent experiment logging

### RAG Quality

The RAG workflow also required decisions about:

- document structure
- chunk size
- chunk boundaries
- metadata
- embedding quality
- retrieval relevance
- how much context to include

Small changes to these parts could affect whether the final answer was accurate and useful.

## Key Design Decision

The escalation guidance was the solution Daniela was most satisfied with.

A standard RAG application can answer a question and show its sources, but that does not necessarily tell a new employee whether acting on the answer is appropriate.

By adding the three escalation levels, the project connected information retrieval to a practical workplace decision:

- Can I proceed?
- Should I confirm this with someone?
- Does this require a supervisor?

This made the system more aligned with the real onboarding problem.

## Result

The core system was functional when the project was completed.

The final application could:

- receive onboarding questions
- retrieve relevant company information
- generate grounded answers
- display sources and documents
- generate escalation guidance
- explain the escalation recommendation
- log experiments and evaluations through MLflow
- run as a multi-service application

The main planned features that were not completed were:

- uploading new documents through the application
- automatically ingesting newly uploaded documents
- generating schedules or similar structured onboarding plans
- a more advanced custom frontend

These were considered possible extensions rather than requirements for the core system.

## What Daniela Learned

The project gave Daniela practical experience with the full RAG process.

Her main technical learning included:

- document ingestion
- chunking
- embeddings
- vector databases
- semantic retrieval
- grounding model answers in retrieved context
- source attribution
- structured model output
- fallback behaviour
- evaluation of LLM applications
- shared MLflow workflows

She also learned that RAG quality depends on much more than choosing a language model.

Document structure, chunking, retrieval, metadata, prompts, schemas and evaluation all affect whether the application produces reliable answers.

## Teamwork and Project Management

The group used GitHub issues to divide, track and complete work.

Most planned issues were completed by the end of the project, including:

- project setup
- backend
- API endpoints
- RAG
- knowledge base
- agent logic
- frontend
- Docker
- MLflow and evaluation
- schemas and fallbacks
- deployment preparation
- documentation
- presentation

The project gave Daniela experience working across several connected parts of an AI application while coordinating changes with two other developers.

## What Could Be Improved

With more development time, Daniela would improve the project by adding:

- document upload and automatic ingestion
- knowledge-base administration
- improved access control
- user-specific onboarding contexts
- more systematic retrieval evaluation
- manually labelled evaluation datasets
- better monitoring of response quality
- more detailed escalation rules
- onboarding-plan or schedule generation
- a more polished frontend
- fuller production deployment and security

The escalation logic could also be strengthened by combining model judgement with explicit rules for high-risk categories.

## Relevance to MLOps and LLMOps

Wired-AI demonstrates several parts of the AI application lifecycle:

- data and document preparation
- retrieval architecture
- model integration
- API development
- structured outputs
- application packaging
- shared experiment tracking
- prompt management
- evaluation
- logging
- deployment preparation
- user-facing delivery

The project reinforced Daniela's interest in the systems around AI models rather than only the model itself.

It showed how retrieval, evaluation, infrastructure, application logic and user needs must work together for an AI solution to become useful in practice.