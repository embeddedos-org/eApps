import type { DragEvent } from 'react';
import type { Task, TaskStatus } from '../hooks/usePlanner';
import TaskCard from './TaskCard';

interface BoardViewProps {
  tasks: Task[];
  filterByStatus: (status: TaskStatus) => Task[];
  onSelectTask: (id: string) => void;
  onMoveTask: (id: string, status: TaskStatus) => void;
}

const COLUMNS: { status: TaskStatus; label: string; emoji: string }[] = [
  { status: 'todo', label: 'To Do', emoji: '📝' },
  { status: 'in-progress', label: 'In Progress', emoji: '🔄' },
  { status: 'done', label: 'Done', emoji: '✅' },
];

export default function BoardView({ filterByStatus, onSelectTask, onMoveTask }: BoardViewProps) {
  const handleDragOver = (e: DragEvent) => e.preventDefault();

  const handleDrop = (e: DragEvent, status: TaskStatus) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('text/plain');
    if (taskId) onMoveTask(taskId, status);
  };

  return (
    <div className="board">
      {COLUMNS.map(({ status, label, emoji }) => {
        const columnTasks = filterByStatus(status);
        return (
          <div
            key={status}
            className="board-column"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, status)}
          >
            <div className="board-column-header">
              <span>{emoji} {label}</span>
              <span className="board-column-count">{columnTasks.length}</span>
            </div>
            <div className="board-column-body">
              {columnTasks.map((task) => (
                <TaskCard key={task.id} task={task} onClick={() => onSelectTask(task.id)} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
