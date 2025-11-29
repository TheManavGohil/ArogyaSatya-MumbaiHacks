'use client'

import { useState } from "react"
import { analyzeTextApi, type AnalyzeTextResult } from "@/lib/api"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/card"

export function AnalyzeTextPanel() {
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalyzeTextResult | null>(null)

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await analyzeTextApi(text.trim())
      // Basic client-side logging to verify shape while debugging
      console.log("analyze-text result", data)
      setResult(data)
    } catch (e) {
      setError((e as Error).message || "Failed to analyze text")
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="w-full flex justify-center bg-black py-12 px-4">
      <Card className="w-full max-w-3xl bg-zinc-950/80 border-zinc-800">
        <div className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-white">
            Try TrueLens on your own text
          </h2>
          <p className="text-sm text-zinc-400">
            Paste a tweet, headline, or short paragraph to see how the backend
            analysis responds.
          </p>
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste healthcare-related text here..."
            className="min-h-[120px] bg-black/40 border-zinc-800 text-sm text-zinc-100"
          />
          <div className="flex items-center gap-3">
            <Button
              onClick={handleSubmit}
              disabled={loading || !text.trim()}
              className="bg-blue-600 hover:bg-blue-500"
            >
              {loading ? "Analyzing..." : "Analyze text"}
            </Button>
            {error && (
              <p className="text-sm text-red-400 line-clamp-2">{error}</p>
            )}
          </div>

          {result && (
            <div className="mt-6 space-y-3 border-t border-zinc-800 pt-4">
              <h3 className="text-lg font-medium text-white">
                Analysis report
              </h3>
              {result.report ? (
                <p className="text-sm text-zinc-300 whitespace-pre-wrap">
                  {result.report}
                </p>
              ) : (
                <p className="text-sm text-zinc-400">
                  Analysis completed (status: {result.status}). No long-form
                  report was returned by the backend.
                </p>
              )}

              {result.verification_results?.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="text-sm font-semibold text-zinc-200">
                    Detected claims
                  </h4>
                  <ul className="space-y-2 text-sm text-zinc-300">
                    {result.verification_results.map((vr, idx) => (
                      <li
                        key={idx}
                        className="rounded-md border border-zinc-800 bg-black/40 p-3"
                      >
                        {vr.claim && (
                          <p className="font-medium text-zinc-100">
                            Claim: {vr.claim}
                          </p>
                        )}
                        {vr.status && (
                          <p className="text-xs text-zinc-400">
                            Status: {vr.status}
                          </p>
                        )}
                        {vr.explanation && (
                          <p className="mt-1 text-xs text-zinc-300 whitespace-pre-wrap">
                            {vr.explanation}
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {/* Small raw JSON for debugging when needed */}
              <details className="mt-3 text-xs text-zinc-500">
                <summary className="cursor-pointer">
                  Raw response (debug – can be removed later)
                </summary>
                <pre className="mt-1 max-h-64 overflow-auto rounded bg-black/60 p-2 text-[10px]">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
      </Card>
    </section>
  )
}



