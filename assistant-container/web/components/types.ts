export type Source = { source: string; chunk: number };
export type RelatedTopic = { source: string; source_name: string; chunks: number; snippet: string };

export type Turn = {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  related_topics: RelatedTopic[];
  loading: boolean;
  error?: string;
};

export function topicLabel(source: string): string {
  const parts = source.replace(/\\/g, "/").split("/");
  return (parts[parts.length - 1] || source).replace(/\.md$/, "");
}
