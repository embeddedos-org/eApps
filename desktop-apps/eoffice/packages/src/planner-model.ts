import type { Board, PlannerTask, TaskStatus, TaskPriority } from './types';
import { generateId } from './utils';

export class PlannerModel {
  public boards: Board[];

  constructor(boards: Board[] = []) {
    this.boards = boards;
  }

  addBoard(name: string, columns: string[] = ['todo', 'in-progress', 'done']): Board {
    const now = new Date();
    const board: Board = { id: generateId(), name, columns, tasks: [], created_at: now, updated_at: now };
    this.boards.push(board);
    return board;
  }

  removeBoard(id: string): boolean {
    const index = this.boards.findIndex((b) => b.id === id);
    if (index === -1) return false;
    this.boards.splice(index, 1);
    return true;
  }

  addTask(boardId: string, title: string, description: string, priority: TaskPriority): PlannerTask | undefined {
    const board = this.boards.find((b) => b.id === boardId);
    if (!board) return undefined;
    const now = new Date();
    const task: PlannerTask = {
      id: generateId(), title, description, status: 'todo', priority,
      tags: [], linkedDocs: [], created_at: now, updated_at: now,
    };
    board.tasks.push(task);
    board.updated_at = now;
    return task;
  }

  updateTask(boardId: string, taskId: string, updates: Partial<Omit<PlannerTask, 'id' | 'created_at'>>): boolean {
    const board = this.boards.find((b) => b.id === boardId);
    if (!board) return false;
    const task = board.tasks.find((t) => t.id === taskId);
    if (!task) return false;
    Object.assign(task, updates, { updated_at: new Date() });
    board.updated_at = new Date();
    return true;
  }

  removeTask(boardId: string, taskId: string): boolean {
    const board = this.boards.find((b) => b.id === boardId);
    if (!board) return false;
    const index = board.tasks.findIndex((t) => t.id === taskId);
    if (index === -1) return false;
    board.tasks.splice(index, 1);
    board.updated_at = new Date();
    return true;
  }

  moveTask(boardId: string, taskId: string, newStatus: TaskStatus): boolean {
    return this.updateTask(boardId, taskId, { status: newStatus });
  }

  getTasksByStatus(boardId: string, status: TaskStatus): PlannerTask[] {
    const board = this.boards.find((b) => b.id === boardId);
    if (!board) return [];
    return board.tasks.filter((t) => t.status === status);
  }

  toJSON(): object {
    return { boards: this.boards };
  }

  static fromJSON(json: { boards: Board[] }): PlannerModel {
    return new PlannerModel(json.boards.map((b) => ({
      ...b,
      created_at: new Date(b.created_at),
      updated_at: new Date(b.updated_at),
      tasks: b.tasks.map((t) => ({
        ...t,
        created_at: new Date(t.created_at),
        updated_at: new Date(t.updated_at),
        dueDate: t.dueDate ? new Date(t.dueDate) : undefined,
      })),
    })));
  }
}
