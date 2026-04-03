import { Action, ActionPanel, Detail, Form, showToast, Toast } from "@raycast/api";
import { useState } from "react";
import { askEBot } from "./api";

export default function EBotAsk() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    if (!question.trim()) {
      showToast({ style: Toast.Style.Failure, title: "Please enter a question" });
      return;
    }

    setIsLoading(true);
    try {
      const response = await askEBot(question.trim());
      setAnswer(response);
    } catch (err) {
      showToast({
        style: Toast.Style.Failure,
        title: "eBot error",
        message: err instanceof Error ? err.message : "Could not connect to eBot",
      });
    } finally {
      setIsLoading(false);
    }
  }

  if (answer !== null) {
    return (
      <Detail
        markdown={`## 🤖 eBot\n\n**Question:** ${question}\n\n---\n\n${answer}`}
        actions={
          <ActionPanel>
            <Action
              title="Ask Another Question"
              onAction={() => {
                setAnswer(null);
                setQuestion("");
              }}
            />
            <Action.CopyToClipboard
              title="Copy Response"
              content={answer}
              shortcut={{ modifiers: ["cmd"], key: "c" }}
            />
            <Action.CopyToClipboard
              title="Copy All"
              content={`Q: ${question}\n\nA: ${answer}`}
              shortcut={{ modifiers: ["cmd", "shift"], key: "c" }}
            />
          </ActionPanel>
        }
      />
    );
  }

  return (
    <Form
      isLoading={isLoading}
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Ask eBot" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.TextArea
        id="question"
        title="Question"
        placeholder="Ask eBot anything..."
        value={question}
        onChange={setQuestion}
      />
      <Form.Separator />
      <Form.Description text="eBot is your AI assistant. Ask about documents, tasks, or anything else." />
    </Form>
  );
}
