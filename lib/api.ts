const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      text || `Request failed with status ${res.status} ${res.statusText}`,
    );
  }
  return (await res.json()) as T;
}

export type AnalyzeTextResult = {
  status: string;
  report: string;
  verification_results: Array<{
    claim?: string;
    status?: string;
    explanation?: string;
    correction?: string;
    evidence?: Array<{
      source?: string;
      title?: string;
      snippet?: string;
      url?: string;
      trusted?: boolean;
    }>;
  }>;
};

export async function analyzeTextApi(text: string): Promise<AnalyzeTextResult> {
  const res = await fetch(`${API_BASE_URL}/api/analyze-text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  return handleResponse<AnalyzeTextResult>(res);
}

export type TrendCluster = {
  topic: string;
  count: number;
  examples?: string[];
};

export async function getTrendsApi(): Promise<TrendCluster[]> {
  const res = await fetch(`${API_BASE_URL}/api/trends`, {
    method: "GET",
  });

  return handleResponse<TrendCluster[]>(res);
}

export type RawArticle = {
  id: number;
  source_id?: string | null;
  external_id?: string | null;
  url?: string | null;
  content_type?: string | null;
  title?: string | null;
  text_content?: string | null;
  published_at?: string | null;
};

export async function getArticlesApi(): Promise<RawArticle[]> {
  const res = await fetch(`${API_BASE_URL}/api/articles`, {
    method: "GET",
  });
  return handleResponse<RawArticle[]>(res);
}

export async function triggerScanApi(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/api/trigger-scan`, {
    method: "POST",
  });
  return handleResponse<{ status: string }>(res);
}

export async function analyzeArticleApi(
  contentId: number,
): Promise<AnalyzeTextResult> {
  const res = await fetch(`${API_BASE_URL}/api/analyze/${contentId}`, {
    method: "POST",
  });
  return handleResponse<AnalyzeTextResult>(res);
}



