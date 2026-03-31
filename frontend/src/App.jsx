import { useState } from "react"

export default function App() {
  const [query, setQuery] = useState("")
  const [constraint, setConstraint] = useState("balanced")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit() {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          constraints: constraint === "balanced" ? null : { prefer: constraint }
        })
      })

      const data = await response.json()
      if (!response.ok) throw new Error(data.detail)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>

        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>⚡ Prism</h1>
          <p style={styles.subtitle}>Intelligent LLM Router</p>
        </div>

        {/* Input Section */}
        <div style={styles.inputSection}>
          <textarea
            style={styles.textarea}
            placeholder="Enter your query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
          />

          <div style={styles.controls}>
            <select
              style={styles.select}
              value={constraint}
              onChange={(e) => setConstraint(e.target.value)}
            >
              <option value="balanced">Balanced</option>
              <option value="low_cost">Low Cost</option>
              <option value="low_latency">Low Latency</option>
            </select>

            <button
              style={loading ? styles.buttonDisabled : styles.button}
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Routing..." : "Submit"}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div style={styles.error}>
            ⚠️ {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div style={styles.resultSection}>
            <div style={styles.response}>
              {result.response}
            </div>

            <div style={styles.metadata}>
              <div style={styles.metaItem}>
                <span style={styles.metaLabel}>Model</span>
                <span style={styles.metaValue}>{result.model_used}</span>
              </div>
              <div style={styles.metaItem}>
                <span style={styles.metaLabel}>Latency</span>
                <span style={styles.metaValue}>{result.latency_ms?.toFixed(0)}ms</span>
              </div>
              <div style={styles.metaItem}>
                <span style={styles.metaLabel}>Est. Cost</span>
                <span style={styles.metaValue}>${result.estimated_cost?.toFixed(6)}</span>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#0f0f0f",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'Segoe UI', sans-serif",
    padding: "20px",
  },
  card: {
    backgroundColor: "#1a1a1a",
    borderRadius: "16px",
    padding: "40px",
    width: "100%",
    maxWidth: "700px",
    boxShadow: "0 0 40px rgba(99, 102, 241, 0.15)",
    border: "1px solid #2a2a2a",
  },
  header: {
    textAlign: "center",
    marginBottom: "32px",
  },
  title: {
    color: "#ffffff",
    fontSize: "2.5rem",
    margin: "0 0 8px 0",
    fontWeight: "700",
  },
  subtitle: {
    color: "#888",
    fontSize: "1rem",
    margin: 0,
  },
  inputSection: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  textarea: {
    backgroundColor: "#111",
    border: "1px solid #333",
    borderRadius: "8px",
    color: "#fff",
    padding: "12px",
    fontSize: "0.95rem",
    resize: "vertical",
    outline: "none",
    width: "100%",
    boxSizing: "border-box",
  },
  controls: {
    display: "flex",
    gap: "12px",
  },
  select: {
    backgroundColor: "#111",
    border: "1px solid #333",
    borderRadius: "8px",
    color: "#fff",
    padding: "10px 12px",
    fontSize: "0.9rem",
    flex: 1,
    outline: "none",
  },
  button: {
    backgroundColor: "#6366f1",
    border: "none",
    borderRadius: "8px",
    color: "#fff",
    padding: "10px 24px",
    fontSize: "0.95rem",
    fontWeight: "600",
    cursor: "pointer",
    flex: 1,
  },
  buttonDisabled: {
    backgroundColor: "#3a3a5c",
    border: "none",
    borderRadius: "8px",
    color: "#888",
    padding: "10px 24px",
    fontSize: "0.95rem",
    fontWeight: "600",
    cursor: "not-allowed",
    flex: 1,
  },
  error: {
    marginTop: "16px",
    backgroundColor: "#2a1a1a",
    border: "1px solid #5a2a2a",
    borderRadius: "8px",
    color: "#ff6b6b",
    padding: "12px",
    fontSize: "0.9rem",
  },
  resultSection: {
    marginTop: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  response: {
    backgroundColor: "#111",
    border: "1px solid #333",
    borderRadius: "8px",
    color: "#e0e0e0",
    padding: "16px",
    fontSize: "0.95rem",
    lineHeight: "1.6",
    whiteSpace: "pre-wrap",
  },
  metadata: {
    display: "flex",
    gap: "12px",
    justifyContent: "space-between",
  },
  metaItem: {
    backgroundColor: "#111",
    border: "1px solid #2a2a2a",
    borderRadius: "8px",
    padding: "12px 16px",
    flex: 1,
    textAlign: "center",
  },
  metaLabel: {
    display: "block",
    color: "#666",
    fontSize: "0.75rem",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    marginBottom: "4px",
  },
  metaValue: {
    display: "block",
    color: "#6366f1",
    fontSize: "0.95rem",
    fontWeight: "600",
  },
}