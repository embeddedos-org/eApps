import { useState, useCallback } from 'react';

export type TaskStatus = 'todo' | 'in-progress' | 'done';
export type TaskPriority = 'high' | 'medium' | 'low';

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate: string;
  tags: string[];
}

let nextId = 1;
const uid = () => `task-${nextId++}`;

const SAMPLE_TASKS: Task[] = [
  { id: uid(), title: 'Design landing page', description: 'Create wireframes for the new landing page', status: 'todo', priority: 'high', dueDate: '2026-04-10', tags: ['design'] },
  { id: uid(), title: 'Set up CI/CD pipeline', description: 'Configure GitHub Actions for automated deployment', status: 'in-progress', priority: 'medium', dueDate: '2026-04-08', tags: ['devops'] },
  { id: uid(), title: 'Write API documentation', description: 'Document all REST endpoints', status: 'done', priority: 'low', dueDate: '2026-04-05', tags: ['docs'] },
];

export function usePlanner() {
  const [tasks, setTasks] = useState<Task[]>(SAMPLE_TASKS);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  const selectedTask = tasks.find((t) => t.id === selectedTaskId) || null;

  const addTask = useCallback((task: Omit<Task, 'id'>) => {
    const newTask = { ...task, id: uid() };
    setTasks((prev) => [...prev, newTask]);
    return newTask;
  }, []);

  const updateTask = useCallback((id: string, updates: Partial<Task>) => {
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, ...updates } : t)));
  }, []);

  const removeTask = useCallback((id: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
    setSelectedTaskId((prev) => (prev === id ? null : prev));
  }, []);

  const moveTask = useCallback((id: string, newStatus: TaskStatus) => {
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t)));
  }, []);

  const filterByStatus = useCallback(
    (status: TaskStatus) => tasks.filter((t) => t.status === status),
    [tasks],
  );

  const counts = {
    total: tasks.length,
    todo: tasks.filter((t) => t.status === 'todo').length,
    inProgress: tasks.filter((t) => t.status === 'in-progress').length,
    done: tasks.filter((t) => t.status === 'done').length,
  };

  return {
    tasks,
    selectedTask,
    selectedTaskId,
    setSelectedTaskId,
    addTask,
    updateTask,
    removeTask,
    moveTask,
    filterByStatus,
    counts,
  };
}
