import { Action, ActionPanel, Grid } from "@raycast/api";
import { getPreferenceValues } from "@raycast/api";

interface Preferences {
  backendUrl: string;
}

interface AppItem {
  name: string;
  subtitle: string;
  icon: string;
  path: string;
}

const apps: AppItem[] = [
  { name: "eDocs", subtitle: "Documents", icon: "📄", path: "edocs" },
  { name: "eNotes", subtitle: "Notes", icon: "📝", path: "enotes" },
  { name: "eSheets", subtitle: "Spreadsheets", icon: "📊", path: "esheets" },
  { name: "eSlides", subtitle: "Presentations", icon: "📽️", path: "eslides" },
  { name: "eMail", subtitle: "Email", icon: "✉️", path: "email" },
  { name: "eDrive", subtitle: "File Storage", icon: "☁️", path: "edrive" },
  { name: "eConnect", subtitle: "Chat & Messaging", icon: "💬", path: "econnect" },
  { name: "eForms", subtitle: "Forms & Surveys", icon: "📋", path: "eforms" },
  { name: "ePlanner", subtitle: "Tasks & Projects", icon: "📅", path: "eplanner" },
  { name: "eBot", subtitle: "AI Assistant", icon: "🤖", path: "ebot" },
  { name: "eOffice Home", subtitle: "Dashboard", icon: "🏠", path: "" },
];

export default function OpenApp() {
  const { backendUrl } = getPreferenceValues<Preferences>();
  const baseUrl = backendUrl.replace(/\/+$/, "");

  return (
    <Grid columns={4} searchBarPlaceholder="Search eOffice apps...">
      {apps.map((app) => (
        <Grid.Item
          key={app.path}
          title={app.name}
          subtitle={app.subtitle}
          content={app.icon}
          actions={
            <ActionPanel>
              <Action.OpenInBrowser
                title={`Open ${app.name}`}
                url={app.path ? `${baseUrl}/apps/${app.path}` : baseUrl}
              />
              <Action.CopyToClipboard
                title="Copy URL"
                content={app.path ? `${baseUrl}/apps/${app.path}` : baseUrl}
                shortcut={{ modifiers: ["cmd"], key: "c" }}
              />
            </ActionPanel>
          }
        />
      ))}
    </Grid>
  );
}
