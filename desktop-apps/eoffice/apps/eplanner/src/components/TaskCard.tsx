import type { DragEvent } from 'react';
import type { Task } from '../hooks/usePlanner';

interface TaskCardProps {
  task: Task;
  onClick: () => void;
}

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const handleDragStart = (e: DragEvent) => {
    e.dataTransfer.setData('text/plain', task.id);
  };

  return (
    <div className="task-card" onClick={onClick} draggable onDragStart={handleDragStart}>
      <div className="task-card-title">{task.title}</div>
      <div className="task-card-meta">
        <span className={`task-card-priority ${task.priority}`}>{task.priority}</span>
        {task.dueDate && <span className="task-card-due">📅 {task.dueDate}</span>}
      </div>
      {task.tags.length > 0 && (
        <div className="task-card-tags">
          {task.tags.map((tag) => (
            <span key={tag} className="task-card-tag">{tag}</span>
          ))}
        </div>
      )}
    </div>
  );
}
