"use client"

import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"
import { Textarea } from "@/components/ui/textarea"

export default function BlogGenerator() {
  const [topic, setTopic] = useState("")
  const [repoUrl, setRepoUrl] = useState("")
  const [background, setBackground] = useState("")
  const [wordCount, setWordCount] = useState(3000)
  const [writingStyle, setWritingStyle] = useState(
    "Confident yet humble, emphasizing authenticity and transparency."
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [blogContent, setBlogContent] = useState("")

  const handleSubmit = async () => {
    setLoading(true)
    setError("")
    setBlogContent("")

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/generate_blog",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repo_url: repoUrl, // Replace with actual repo URL or make this a dynamic input
            topic,
            background,
            word_count: wordCount,
            writing_style: writingStyle,
          }),
        }
      )

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      setBlogContent(data.blog_content)
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
      <h1 className="text-2xl font-bold mb-4">Blog Post Generator</h1>
      <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Repo URL{" "}
          </label>
          <Input value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Topic
          </label>
          <Input
            placeholder="Eg: Best AI Tools For Blogging"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Background
          </label>
          <Textarea
            placeholder="Any facts, statistics such as pricing, features that you want to incorporate into the article."
            value={background}
            onChange={(e) => setBackground(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Writing Style
          </label>
          <Input
            value={writingStyle}
            onChange={(e) => setWritingStyle(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Word Count
          </label>
          <Slider
            min={500}
            max={5000}
            value={[wordCount]}
            onValueChange={(value) => setWordCount(value[0])}
          />
          <div className="text-gray-700 mt-2">
            Selected Word Count: {wordCount}
          </div>
        </div>

        <Button
          type="button"
          onClick={handleSubmit}
          className="w-full mt-4"
          disabled={loading}
        >
          {loading ? "Generating..." : "Login to Generate Blogs For Free"}
        </Button>

        {error && <div className="text-red-500 mt-4">{error}</div>}
        {blogContent && (
          <div className="mt-4">
            <h2 className="text-xl font-bold">Generated Blog Content</h2>
            <p className="mt-2 whitespace-pre-wrap">{blogContent}</p>
          </div>
        )}
      </form>
    </div>
  )
}
