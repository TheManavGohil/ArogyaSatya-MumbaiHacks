'use client'

import { useEffect, useState, useRef } from "react"
import {
  analyzeArticleApi,
  analyzeTextApi,
  getArticlesApi,
  getTrendsApi,
  triggerScanApi,
  type AnalyzeTextResult,
  type RawArticle,
  type TrendCluster,
} from "@/lib/api"
import { Card } from "@/components/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { RefreshCw } from "lucide-react"

function renderReportContent(report: string) {
  if (!report) return null

  const lines = report.split("\n")
  const firstNonEmptyIndex = lines.findIndex((l) => l.trim().length > 0)

  let heading: string | null = null
  if (firstNonEmptyIndex !== -1) {
    const firstLine = lines[firstNonEmptyIndex].trim()
    const match = firstLine.match(/^\*\*(.+)\*\*$/)
    if (match) {
      heading = match[1].trim()
      lines[firstNonEmptyIndex] = ""
    }
  }

  const remaining = lines.join("\n").trim()
  const paragraphs = remaining
    ? remaining.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean)
    : []

  return (
    <div className="space-y-3">
      {heading && (
        <h3 className="text-sm font-semibold text-zinc-100">
          {heading}
        </h3>
      )}
      {paragraphs.map((p, idx) => (
        <p key={idx} className="text-sm text-zinc-200 whitespace-pre-wrap">
          {p}
        </p>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const [scanLoading, setScanLoading] = useState(false)
  const [scanMessage, setScanMessage] = useState<string | null>(null)

  const [trends, setTrends] = useState<TrendCluster[]>([])
  const [trendsLoading, setTrendsLoading] = useState(false)

  const [articles, setArticles] = useState<RawArticle[]>([])
  const [articlesLoading, setArticlesLoading] = useState(false)

  const [text, setText] = useState("")
  const [textLoading, setTextLoading] = useState(false)

  const [analyzingArticleId, setAnalyzingArticleId] = useState<number | null>(
    null,
  )

  const [activeAnalysis, setActiveAnalysis] = useState<AnalyzeTextResult | null>(
    null,
  )
  const [analysisSource, setAnalysisSource] = useState<
    { type: "text"; label: string } | { type: "article"; label: string } | null
  >(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  const analyzeSectionRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        setTrendsLoading(true)
        setArticlesLoading(true)
        const [t, a] = await Promise.all([getTrendsApi(), getArticlesApi()])
        setTrends(t)
        setArticles(a)
      } catch (e) {
        // Ignore for now; sections will just appear empty
        console.error(e)
      } finally {
        setTrendsLoading(false)
        setArticlesLoading(false)
      }
    }
    load()
  }, [])

  const refreshTrends = async () => {
    try {
      setTrendsLoading(true)
      const updated = await getTrendsApi()
      setTrends(updated)
    } catch (e) {
      console.error("Failed to refresh trends:", e)
    } finally {
      setTrendsLoading(false)
    }
  }

  const handleTriggerScan = async () => {
    setScanLoading(true)
    setScanMessage(null)
    try {
      const res = await triggerScanApi()
      setScanMessage(res.status ?? "Scan completed")
      // Refresh articles and trends after scan
      const [updatedArticles, updatedTrends] = await Promise.all([
        getArticlesApi(),
        getTrendsApi(),
      ])
      setArticles(updatedArticles)
      setTrends(updatedTrends)
    } catch (e) {
      setScanMessage((e as Error).message || "Failed to trigger scan")
    } finally {
      setScanLoading(false)
    }
  }

  const handleAnalyzeText = async (
    overrideText?: string,
    sourceLabel?: string,
  ) => {
    const value = (overrideText ?? text).trim()
    if (!value) return
    setText(value)
    setTextLoading(true)
    setAnalysisError(null)
    try {
      const res = await analyzeTextApi(value)
      console.log("dashboard analyze-text result", res)
      setActiveAnalysis(res)
      setAnalysisSource({
        type: "text",
        label: sourceLabel ?? "Manual text input",
      })
      // Refresh trends after analysis (new claims might create new trends)
      refreshTrends()
    } catch (e) {
      setAnalysisError((e as Error).message || "Failed to analyze text")
    } finally {
      setTextLoading(false)
    }
  }

  const handleAnalyzeArticle = async (article: RawArticle) => {
    setAnalysisError(null)
    setActiveAnalysis(null)
    setAnalyzingArticleId(article.id)
    try {
      const res = await analyzeArticleApi(article.id)
      setActiveAnalysis(res)
      setAnalysisSource({
        type: "article",
        label: article.title || article.source_id || `Article #${article.id}`,
      })
      // Refresh trends after analysis (new claims might create new trends)
      refreshTrends()
      // Scroll to analysis results in Analyze Content section
      setTimeout(() => {
        if (analyzeSectionRef.current) {
          const rect = analyzeSectionRef.current.getBoundingClientRect()
          const offset = window.scrollY + rect.top - 80
          window.scrollTo({
            top: offset,
            behavior: "smooth",
          })
        }
      }, 100)
    } catch (e) {
      setAnalysisError((e as Error).message || "Failed to analyze article")
    } finally {
      setAnalyzingArticleId(null)
    }
  }

  return (
    <main className="min-h-screen bg-black px-4 py-8 text-zinc-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 mt-20">
        {/* Header / Dashboard card */}
        <Card className="flex items-center justify-between border-zinc-800 bg-zinc-950 px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-sm text-zinc-400">
              AI-Powered Healthcare Misinformation Detector
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Button
              onClick={handleTriggerScan}
              disabled={scanLoading}
              className="bg-blue-600 hover:bg-blue-500"
            >
              {scanLoading ? "Scanning..." : "Trigger New Scan"}
            </Button>
            {scanMessage && (
              <p className="text-xs text-zinc-400 max-w-xs text-right">
                {scanMessage}
              </p>
            )}
          </div>
        </Card>

        {/* Analyze Content */}
        <Card
          ref={analyzeSectionRef}
          className="border-zinc-800 bg-zinc-950 px-6 py-5"
        >
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold text-white">
                Analyze Content
              </h2>
              <p className="text-sm text-zinc-400">
                Paste a news article, tweet, or YouTube URL.
              </p>
            </div>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Regular physical activity lowers the risk of chronic disease"
              className="min-h-[120px] bg-black/40 border-zinc-800 text-sm"
            />
            <Button
              onClick={() => handleAnalyzeText()}
              disabled={textLoading || !text.trim()}
              className="bg-blue-600 hover:bg-blue-500"
            >
              {textLoading ? "Analyzing..." : "Analyze Veracity"}
            </Button>
            {analysisError && (
              <p className="text-sm text-red-400">{analysisError}</p>
            )}

            {activeAnalysis && (
              <div className="mt-5 rounded-xl border border-blue-500/30 bg-gradient-to-b from-blue-500/10 via-zinc-950 to-black/80 p-4 shadow-[0_0_40px_rgba(37,99,235,0.25)]">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium tracking-wide text-zinc-400">
                      Analysis status
                    </span>
                    <span className="inline-flex items-center rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-300">
                      {activeAnalysis.status}
                    </span>
                  </div>
                  <span className="text-[11px] text-zinc-500">
                    Powered by TrueLens agent graph
                  </span>
                </div>

                <div className="mt-3 space-y-3">
                  {analysisSource?.label && (
                    <p className="text-xs font-semibold uppercase tracking-wide text-blue-300">
                      Narrative:&nbsp;
                      <span className="normal-case text-zinc-100">
                        {analysisSource.label}
                      </span>
                    </p>
                  )}
                  <h3 className="text-sm font-semibold text-zinc-100">
                    Executive Summary
                  </h3>
                  <div className="rounded-lg bg-black/40 p-3">
                    {renderReportContent(activeAnalysis.report)}
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Trending + Articles */}
        <div className="grid gap-6 lg:grid-cols-[2fr,3fr]">
          <Card className="border-zinc-800 bg-zinc-950 px-6 py-5">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">
                Trending Narratives
              </h2>
              <Button
                size="sm"
                variant="outline"
                onClick={refreshTrends}
                disabled={trendsLoading}
                className="border-zinc-700 text-xs h-7"
              >
                <RefreshCw
                  className={`mr-1 h-3 w-3 ${trendsLoading ? "animate-spin" : ""}`}
                />
                {trendsLoading ? "Refreshing..." : "Refresh"}
              </Button>
            </div>
            {trendsLoading ? (
              <p className="text-sm text-zinc-400">Loading trends…</p>
            ) : trends.length === 0 ? (
              <p className="text-sm text-zinc-500">
                No trend data available yet.
              </p>
            ) : (
              <div className="flex flex-wrap gap-3">
                {trends.map((trend, idx) => {
                  const label = trend.topic
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={async () => {
                        // Smooth scroll to Analyze Content section
                        if (analyzeSectionRef.current) {
                          const rect =
                            analyzeSectionRef.current.getBoundingClientRect()
                          const offset = window.scrollY + rect.top - 80
                          window.scrollTo({
                            top: offset,
                            behavior: "smooth",
                          })
                        } else {
                          window.scrollTo({ top: 0, behavior: "smooth" })
                        }
                        // Run analysis for this narrative
                        await handleAnalyzeText(label, label)
                      }}
                      className="rounded-full bg-blue-500/10 px-3 py-2 text-sm text-blue-200 border border-blue-500/30 hover:bg-blue-500/20 hover:border-blue-400/60 transition-colors"
                    >
                      {label}
                      {trend.count > 1 && (
                        <span className="ml-1 text-xs text-blue-300">
                          ({trend.count})
                        </span>
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </Card>

          <Card className="border-zinc-800 bg-zinc-950 px-6 py-5">
            <h2 className="mb-3 text-xl font-semibold text-white">
              Latest Articles
            </h2>
            {articlesLoading ? (
              <p className="text-sm text-zinc-400">Loading articles…</p>
            ) : articles.length === 0 ? (
              <p className="text-sm text-zinc-500">
                No ingested content yet. Trigger a new scan to fetch articles.
              </p>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {articles.map((article) => (
                  <div
                    key={article.id}
                    className="flex flex-col justify-between rounded-lg border border-zinc-800 bg-black/40 p-3"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-semibold text-zinc-100 line-clamp-2">
                        {article.title || `Item from ${article.source_id}`}
                      </p>
                      <p className="text-xs text-zinc-500 line-clamp-2">
                        {article.text_content || article.url}
                      </p>
                    </div>
                    <div className="mt-3 flex justify-between items-center">
                      <span className="text-[11px] uppercase tracking-wide text-zinc-500">
                        {article.source_id || "source"}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-zinc-700 text-xs"
                        onClick={() => handleAnalyzeArticle(article)}
                        disabled={analyzingArticleId === article.id}
                      >
                        {analyzingArticleId === article.id
                          ? "Analyzing..."
                          : "Analyze"}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </main>
  )
}



