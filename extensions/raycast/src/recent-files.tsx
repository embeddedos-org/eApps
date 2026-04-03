import { Action, ActionPanel, List, showToast, Toast } from "@raycast/api";
import { useEffect, useState } from "react";
import { getRecentFiles, RecentFile } from "./api";

const appIcons: Record<string, string> = {
  edocs: "📄",
  enotes: "📝",
  esheets: "📊",
  eslides: "📽️",
  email: "✉️",
  edrive: "☁️",
  econnect: "💬",
  eforms: "📋",
  eplanner: "📅",
};

export default function RecentFiles() {
  const [files, setFiles] = useState<RecentFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadFiles() {
      try {
        const recent = await getRecentFiles();
        setFiles(recent);
      } catch (err) {
        showToast({
          style: Toast.Style.Failure,
          title: "Failed to load recent files",
          message: err instanceof Error ? err.message : "Could not connect to eOffice",
        });
      } finally {
        setIsLoading(false);
      }
    }
    loadFiles();
  }, []);

  return (
    <List isLoading={isLoading} searchBarPlaceholder="Filter recent files...">
      {files.length === 0 && !isLoading ? (
        <List.EmptyView
          title="No recent files"
          description="Files you access in eOffice will appear here"
          icon="📂"
        />
      ) : (
        files.map((file) => (
          <List.Item
            key={file.id}
            title={file.name}
            subtitle={file.app}
            icon={appIcons[file.app] || "📁"}
            accessories={[
              { text: file.type },
              { text: new Date(file.updatedAt).toLocaleDateString() },
            ]}
            actions={
              <ActionPanel>
                <Action.OpenInBrowser
                  title="Open in eOffice"
                  url={`http://localhost:3001/apps/${file.app}/${file.id}`}
                />
                <Action.CopyToClipboard
                  title="Copy File Name"
                  content={file.name}
                  shortcut={{ modifiers: ["cmd"], key: "c" }}
                />
                <Action.CopyToClipboard
                  title="Copy Link"
                  content={`http://localhost:3001/apps/${file.app}/${file.id}`}
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
