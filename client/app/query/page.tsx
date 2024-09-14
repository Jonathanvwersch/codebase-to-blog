"use client"

import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

type CodebaseQueryResponse = {
  file_path: string
  start_line: number
  end_line: number
  score: number
}

export default function CodebaseQueryTool() {
  const [repoUrl, setRepoUrl] = useState("")
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [indexingMessage, setIndexingMessage] = useState("")
  const [queryResults, setQueryResults] = useState<CodebaseQueryResponse[]>([])

  const handleIndexing = async () => {
    setLoading(true)
    setError("")
    setIndexingMessage("")
    try {
      const response = await fetch("http://localhost:8000/api/v1/index", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      })
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }
      const data = await response.json()
      setIndexingMessage(data.message)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleQuery = async () => {
    setLoading(true)
    setError("")
    setQueryResults([])
    try {
      const response = await fetch("http://localhost:8000/api/v1/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
        }),
      })
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }
      const data = await response.json()
      setQueryResults(data)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Codebase Query Tool</h1>
      <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Public Repository URL
          </label>
          <Input
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repo"
          />
        </div>
        <Button
          type="button"
          onClick={handleIndexing}
          className="w-full mt-4"
          disabled={loading || !repoUrl}
        >
          {loading ? "Indexing..." : "Index Codebase"}
        </Button>
        {indexingMessage && (
          <div className="mt-4 p-2 bg-green-100 text-green-700 rounded">
            {indexingMessage}
          </div>
        )}
        <div className="mt-8">
          <label className="block text-sm font-medium text-gray-700">
            Query
          </label>
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about the indexed codebase..."
            rows={4}
          />
        </div>
        <Button
          type="button"
          onClick={handleQuery}
          className="w-full mt-4"
          disabled={loading || !query}
        >
          {loading ? "Querying..." : "Submit Query"}
        </Button>
        {error && <div className="text-red-500 mt-4">{error}</div>}
        {queryResults.length > 0 && (
          <div className="mt-4">
            <h2 className="text-xl font-bold">Query Results</h2>
            {queryResults.map((result, index) => (
              <div key={index} className="mt-4 p-4 bg-gray-100 rounded">
                <p className="font-semibold">Result {index + 1}</p>
                <p>File: {result.file_path}</p>
                <p>
                  Lines: {result.start_line} - {result.end_line}
                </p>
                <p>Relevance Score: {result.score.toFixed(4)}</p>
              </div>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}
