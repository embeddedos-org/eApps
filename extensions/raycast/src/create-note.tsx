import { Action, ActionPanel, Form, showToast, Toast, useNavigation } from "@raycast/api";
import { useState } from "react";
import { createNote } from "./api";

export default function CreateNote() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { pop } = useNavigation();

  async function handleSubmit() {
    if (!title.trim()) {
      showToast({ style: Toast.Style.Failure, title: "Title is required" });
      return;
    }

    setIsSubmitting(true);

    try {
      const note = await createNote(title.trim(), content);
      showToast({
        style: Toast.Style.Success,
        title: "Note created",
        message: `"${note.title}" saved to eNotes`,
      });
      pop();
    } catch (err) {
      showToast({
        style: Toast.Style.Failure,
        title: "Failed to create note",
        message: err instanceof Error ? err.message : "Could not connect to eOffice",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Form
      isLoading={isSubmitting}
      actions={
        <ActionPanel>
          <Action.SubmitForm title="Create Note" onSubmit={handleSubmit} />
        </ActionPanel>
      }
    >
      <Form.TextField
        id="title"
        title="Title"
        placeholder="Note title..."
        value={title}
        onChange={setTitle}
      />
      <Form.TextArea
        id="content"
        title="Content"
        placeholder="Write your note here..."
        value={content}
        onChange={setContent}
        enableMarkdown
      />
      <Form.Separator />
      <Form.Description text="Notes are saved to eNotes and synced across eOffice." />
    </Form>
  );
}
