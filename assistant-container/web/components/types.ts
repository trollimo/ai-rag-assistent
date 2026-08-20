export type SourceChunk = { chunk: number; text: string; distance?: number };
export type Source = { source: string; chunks: SourceChunk[] };
export type RelatedTopic = { source: string; source_name: string; chunks: number; snippet: string };

export type ChatMode = "strict" | "combined";
export type AnswerSource = "rag" | "llm_knowledge" | "no_info";

export type Turn = {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  related_topics: RelatedTopic[];
  answer_source: AnswerSource;
  normalized_query?: string | null;
  loading: boolean;
  error?: string;
};

export function topicLabel(source: string): string {
  const parts = source.replace(/\\/g, "/").split("/");
  return (parts[parts.length - 1] || source).replace(/\.md$/, "");
}
