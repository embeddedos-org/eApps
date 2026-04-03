import { useState } from 'react';
import TopBar from './components/TopBar';
import ChannelList from './components/ChannelList';
import MessageThread from './components/MessageThread';
import MessageComposer from './components/MessageComposer';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { useConnect } from './hooks/useConnect';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [ebotOpen, setEbotOpen] = useState(false);
  const connect = useConnect();
  const ebot = useEBot();

  const handleNewChannel = () => {
    const name = prompt('Channel name:');
    if (name?.trim()) connect.addChannel(name.trim());
  };

  return (
    <div className="econnect-app">
      <TopBar
        onNewChannel={handleNewChannel}
        ebotOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={ebot.connected}
      />
      <div className="econnect-body">
        <ChannelList
          channels={connect.channels}
          selectedChannelId={connect.selectedChannelId}
          onSelect={connect.setSelectedChannelId}
          onCreate={handleNewChannel}
        />
        <div className="econnect-main">
          <MessageThread
            messages={connect.channelMessages}
            channelName={connect.selectedChannel?.name ?? ''}
          />
          <MessageComposer
            onSend={connect.sendMessage}
            channelName={connect.selectedChannel?.name ?? ''}
          />
        </div>
        <EBotSidebar
          open={ebotOpen}
          connected={ebot.connected}
          loading={ebot.loading}
          onClose={() => setEbotOpen(false)}
          onSummarizeThread={ebot.summarizeThread}
          onDraftMessage={ebot.draftMessage}
        />
      </div>
      <StatusBar
        channelCount={connect.channels.length}
        messageCount={connect.messages.length}
        connected={ebot.connected}
      />
    </div>
  );
}
