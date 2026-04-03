import type { Channel } from '../hooks/useConnect';

interface ChannelListProps {
  channels: Channel[];
  selectedChannelId: string;
  onSelect: (id: string) => void;
  onCreate: () => void;
}

export default function ChannelList({ channels, selectedChannelId, onSelect, onCreate }: ChannelListProps) {
  return (
    <div className="channel-list">
      <div className="channel-list-header">
        <span>Channels</span>
        <button className="channel-list-add" onClick={onCreate} title="New channel">+</button>
      </div>
      <div className="channel-list-items">
        {channels.map((ch) => (
          <div
            key={ch.id}
            className={`channel-item ${ch.id === selectedChannelId ? 'active' : ''}`}
            onClick={() => onSelect(ch.id)}
          >
            <span className="channel-item-name">
              <span>#</span>
              <span>{ch.name}</span>
            </span>
            <span className="channel-badge">{ch.members}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
