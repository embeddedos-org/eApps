import { useState, useCallback } from 'react';
import TopBar from './components/TopBar';
import InboxList from './components/InboxList';
import EmailViewer from './components/EmailViewer';
import EmailComposer from './components/EmailComposer';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useMailbox } from './hooks/useMailbox';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [ebotOpen, setEbotOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');
  const [composerOpen, setComposerOpen] = useState(false);
  const [composerDefaults, setComposerDefaults] = useState({ to: '', subject: '', body: '' });

  const mailbox = useMailbox();
  const { connected, loading, draftReply, summarizeThread, smartCompose } = useEBot();

  const folderLabels = { inbox: 'Inbox', sent: 'Sent', drafts: 'Drafts' };

  const handleCompose = useCallback(() => {
    setComposerDefaults({ to: '', subject: '', body: '' });
    setComposerOpen(true);
  }, []);

  const handleReply = useCallback(() => {
    if (!mailbox.selectedEmail) return;
    const email = mailbox.selectedEmail;
    setComposerDefaults({
      to: email.from,
      subject: `Re: ${email.subject}`,
      body: `\n\n--- Original Message ---\nFrom: ${email.from}\n${email.body}`,
    });
    setComposerOpen(true);
  }, [mailbox.selectedEmail]);

  const handleForward = useCallback(() => {
    if (!mailbox.selectedEmail) return;
    const email = mailbox.selectedEmail;
    setComposerDefaults({
      to: '',
      subject: `Fwd: ${email.subject}`,
      body: `\n\n--- Forwarded Message ---\nFrom: ${email.from}\nSubject: ${email.subject}\n\n${email.body}`,
    });
    setComposerOpen(true);
  }, [mailbox.selectedEmail]);

  const handleSend = useCallback(
    (to: string, subject: string, body: string) => {
      mailbox.addMessage({
        from: 'me@eoffice.com',
        to,
        subject,
        body,
        date: new Date().toISOString().split('T')[0],
        read: true,
        starred: false,
        folder: 'sent',
      });
    },
    [mailbox],
  );

  const handleEBotAction = useCallback(
    async (action: string) => {
      if (!connected) return;
      setEbotResponse('');
      try {
        let response = '';
        switch (action) {
          case 'draft-reply': {
            if (!mailbox.selectedEmail) {
              response = '⚠️ Select an email first to draft a reply.';
            } else {
              const { from, subject, body } = mailbox.selectedEmail;
              response = await draftReply(`From: ${from}\nSubject: ${subject}\n\n${body}`);
              response = `↩️ **Draft Reply**\n\n${response}`;
            }
            break;
          }
          case 'summarize': {
            if (!mailbox.selectedEmail) {
              response = '⚠️ Select an email first to summarize.';
            } else {
              response = await summarizeThread(mailbox.selectedEmail.body);
              response = `📋 **Summary**\n\n${response}`;
            }
            break;
          }
          case 'smart-compose': {
            response = await smartCompose('a follow-up on the latest project status');
            response = `✨ **Smart Compose**\n\n${response}`;
            break;
          }
          case 'improve': {
            if (!mailbox.selectedEmail) {
              response = '⚠️ Select an email first.';
            } else {
              response = `💡 **Suggestions**\n\n• Consider a clearer subject line\n• Add a specific call to action\n• Keep paragraphs short for readability`;
            }
            break;
          }
          default:
            response = `eBot processed "${action}".`;
        }
        setEbotResponse(response);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Unknown error';
        setEbotResponse(`❌ **eBot Error**\n\n${msg}`);
      }
    },
    [connected, draftReply, summarizeThread, smartCompose, mailbox.selectedEmail],
  );

  return (
    <div className="email-app">
      <TopBar
        currentFolder={mailbox.currentFolder}
        onFolderChange={mailbox.setCurrentFolder}
        onCompose={handleCompose}
        ebotSidebarOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={connected}
        unreadCount={mailbox.unreadCount}
      />
      <div className="email-body">
        <InboxList
          emails={mailbox.folderMessages}
          selectedId={mailbox.selectedId}
          onSelect={mailbox.selectEmail}
          onToggleStar={mailbox.toggleStar}
          folderLabel={folderLabels[mailbox.currentFolder]}
        />
        <EmailViewer
          email={mailbox.selectedEmail}
          onReply={handleReply}
          onForward={handleForward}
          onDelete={mailbox.deleteMessage}
        />
        <EBotSidebar
          open={ebotOpen}
          connected={connected}
          response={ebotResponse}
          isLoading={loading}
          onAction={handleEBotAction}
          onClose={() => setEbotOpen(false)}
        />
      </div>
      {composerOpen && (
        <EmailComposer
          initialTo={composerDefaults.to}
          initialSubject={composerDefaults.subject}
          initialBody={composerDefaults.body}
          onSend={handleSend}
          onClose={() => setComposerOpen(false)}
        />
      )}
      <StatusBar
        messageCount={mailbox.folderMessages.length}
        unreadCount={mailbox.unreadCount}
        connected={connected}
      />
    </div>
  );
}
