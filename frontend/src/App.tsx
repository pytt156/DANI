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

const suggestions = [
  'What has Daniela built?',
  'Why should we hire Daniela?',
  'What does Daniela know about MLOps?',
]

function App() {
  const [message, setMessage] = useState('')
  const [submittedMessage, setSubmittedMessage] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<Source[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  async function sendMessage(question: string) {
    const trimmedMessage = question.trim()

    if (!trimmedMessage || isLoading) return

    setSubmittedMessage(trimmedMessage)
    setAnswer('')
    setSources([])
    setError('')
    setIsLoading(true)

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
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = (await response.json()) as ChatResponse

      setAnswer(data.answer)
      setSources(data.sources)
      setMessage('')
    } catch (requestError) {
      console.error(requestError)
      setError('DANI is unavailable right now.')
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    await sendMessage(message)
  }

  return (
    <div className="site">
      <header className="site-header">
        <div className="header-top">
          <a href="/" className="name">
            Daniela Algerydh
          </a>

          <span className="page-name">DANI</span>
        </div>
      </header>

      <section className="hero-collage" aria-label="Daniela and photography">
        <div className="hero-main">
          <img
            src="/images/daniela-1.jpg"
            alt=""
          />
        </div>
        <div className="hero-side">

          <img
            src="/images/nature-3.jpg"
            alt=""
          />

          <img
            src="/images/nature-2.jpg"
            alt=""
          />

        </div>

      </section>
      <nav className="nav">
        <a href="#">About</a>
        <a href="#">Projects</a>
        <a href="#">Blog</a>
        <a href="#">CV</a>
      </nav>

      <main className="content-layout">
        <div className="main">
          <section className="intro">
            <h1>Ask DANI.</h1>

            <p>
              A conversation about Daniela&apos;s work, projects and experience.
            </p>

            {!submittedMessage && (
              <div className="prompts">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => void sendMessage(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </section>

          {(submittedMessage || isLoading || answer) && (
            <section className="conversation">
              {submittedMessage && (
                <div className="message">
                  <span className="speaker">You</span>
                  <p>{submittedMessage}</p>
                </div>
              )}

              {isLoading && (
                <div className="message">
                  <span className="speaker">DANI</span>
                  <p className="thinking">Thinking…</p>
                </div>
              )}

              {answer && !isLoading && (
                <div className="message">
                  <span className="speaker">DANI</span>

                  <p className="answer">{answer}</p>

                  {sources.length > 0 && (
                    <p className="sources">
                      Sources:{' '}
                      {sources.map((source, index) => (
                        <span key={`${source.source}-${source.chunk_index}`}>
                          {source.title}
                          {index < sources.length - 1 ? ' · ' : ''}
                        </span>
                      ))}
                    </p>
                  )}
                </div>
              )}

              {error && <p className="error">{error}</p>}
            </section>
          )}

          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask something about Daniela..."
              rows={1}
              disabled={isLoading}
              aria-label="Ask DANI"
            />

            <button
              type="submit"
              disabled={!message.trim() || isLoading}
            >
              Send
            </button>
          </form>
        </div>

        <aside className="sidebar">
          <section className="sidebar-section">
            <p className="sidebar-label">Latest writing</p>

            <a className="sidebar-title" href="#">
              Building DANI
            </a>

            <p className="sidebar-meta">August 2026</p>

            <a className="sidebar-link" href="#">
              Read ↗
            </a>
          </section>

          <section className="sidebar-section">
            <p className="sidebar-label">CV</p>

            <p className="sidebar-copy">
              Education, projects, technical skills and experience.
            </p>

            <a className="sidebar-link" href="#">
              View résumé ↗
            </a>
          </section>

          <section className="sidebar-section sidebar-photo">
            <p className="sidebar-label">Photography</p>

            <img
              src="/images/nature-1.jpg"
              alt="Frost-covered plant photographed by Daniela"
            />

            <p className="sidebar-meta">Shot by Daniela</p>
          </section>
        </aside>
      </main>
    </div>
  )
}

export default App