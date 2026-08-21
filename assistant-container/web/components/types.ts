export type SourceChunk = { chunk: number; text: string; distance?: number };
export type Source = { source: string; chunks: SourceChunk[] };
export type RelatedTopic = { source: string; source_name: string; chunks: number; snippet: string };

export type ChatMode = "strict" | "combined";
export type AnswerSource = "rag" | "llm_knowledge" | "no_info";

export type SkillHit = { name: string; title: string; download_url: string };

export type Turn = {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  related_topics: RelatedTopic[];
  answer_source: AnswerSource;
  normalized_query?: string | null;
  skills: SkillHit[];
  loading: boolean;
  error?: string;
};

export type SkillSummary = {
  name: string;
  title: string;
  description: string;
  version: string;
  files_count: number;
  size_bytes: number;
  download_url: string;
};

export type SkillDetail = SkillSummary & {
  files: string[];
  sha256: string;
  install_hint: string;
};

export function topicLabel(source: string): string {
  const parts = source.replace(/\\/g, "/").split("/");
  return (parts[parts.length - 1] || source).replace(/\.md$/, "");
}
