import { Action, ActionPanel, List, showToast, Toast } from "@raycast/api";
import { useState, useEffect } from "react";
import { searchDocs, EDoc } from "./api";

export default function SearchDocs() {
  const [query, setQuery] = useState("");
  const [docs, setDocs] = useState<EDoc[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setDocs([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await searchDocs(query);
        setDocs(results);
      } catch (err) {
        showToast({
          style: Toast.Style.Failure,
          title: "Search failed",
          message: err instanceof Error ? err.message : "Could not connect to eOffice",
        });
        setDocs([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <List
      searchBarPlaceholder="Search eDocs..."
      onSearchTextChange={setQuery}
      isLoading={isLoading}
      throttle
    >
      {docs.length === 0 && !isLoading ? (
        <List.EmptyView
          title={query ? "No documents found" : "Search eDocs"}
          description={query ? "Try a different search term" : "Type to search across all documents"}
          icon="📄"
        />
      ) : (
        docs.map((doc) => (
          <List.Item
            key={doc.id}
            title={doc.title}
            subtitle={doc.content.substring(0, 80) + "..."}
            accessories={[
              { text: new Date(doc.updatedAt).toLocaleDateString() },
              ...(doc.tags ? doc.tags.map((tag) => ({ tag: { value: tag } })) : []),
            ]}
            actions={
              <ActionPanel>
                <Action.OpenInBrowser
                  title="Open in eDocs"
                  url={`http://localhost:3001/apps/edocs/${doc.id}`}
                />
                <Action.CopyToClipboard
                  title="Copy Content"
                  content={doc.content}
                  shortcut={{ modifiers: ["cmd"], key: "c" }}
                />
                <Action.CopyToClipboard
                  title="Copy Link"
                  content={`http://localhost:3001/apps/edocs/${doc.id}`}
                  shortcut={{ modifiers: ["cmd", "shift"], key: "c" }}
                />
              </ActionPanel>
            }
          />
        ))
      )}
    </List>
  );
}
