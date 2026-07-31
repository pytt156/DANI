import { useState } from 'react'
import type { SubmitEvent } from 'react'
import './App.css'

type Source = {
  title: string
  source: string
  section: string
  chunk_index: number
  score: number
}

type ChatResponse = {
  answer: string
  sources: Source[]
}

const API_URL =
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

function App() {
  const [message, setMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<Source[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedMessage = message.trim()

    if (!trimmedMessage || isLoading) {
      return
    }

    setIsLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: trimmedMessage,
        }),
      })

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }

      const data = (await response.json()) as ChatResponse

      setAnswer(data.answer)
      setSources(data.sources)
    } catch (requestError) {
      console.error(requestError)
      setError(
        'DANI kunde inte nå servern. Kontrollera att backend körs och försök igen.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="page">
      <section className="intro">
        <p className="eyebrow">Daniela’s AI Navigation Interface</p>
        <h1>Talk with DANI</h1>
        <p className="intro-text">
          Ask about Daniela’s projects, technical skills, experience and what
          she has learned while becoming an AI and MLOps engineer.
        </p>
      </section>

      <section className="chat-panel" aria-labelledby="chat-heading">
        <div className="panel-header">
          <div>
            <p className="status">
              <span className="status-dot" aria-hidden="true" />
              Knowledge base online
            </p>
            <h2 id="chat-heading">What would you like to know?</h2>
          </div>
        </div>

        <form className="chat-form" onSubmit={handleSubmit}>
          <label htmlFor="message">Your question</label>

          <textarea
            id="message"
            name="message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Which projects use FastAPI?"
            rows={4}
            disabled={isLoading}
          />

          <div className="form-footer">
            <span className="hint">
              Try asking about projects, technologies or experience.
            </span>

            <button type="submit" disabled={!message.trim() || isLoading}>
              {isLoading ? 'Thinking…' : 'Ask DANI'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        {answer && (
          <section className="response" aria-live="polite">
            <p className="response-label">DANI</p>
            <p className="answer">{answer}</p>

            {sources.length > 0 && (
              <div className="sources">
                <h3>Sources</h3>

                <ul>
                  {sources.map((source) => (
                    <li
                      key={`${source.source}-${source.chunk_index}`}
                      className="source-card"
                    >
                      <div>
                        <strong>{source.title}</strong>
                        <span>{source.section}</span>
                      </div>

                      <span className="score">
                        {Math.round(source.score * 100)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </section>
    </main>
  )
}

export default App