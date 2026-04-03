import { useState, useCallback } from 'react';
import TopBar from './components/TopBar';
import BoardView from './components/BoardView';
import TaskDetail from './components/TaskDetail';
import EBotSidebar from './components/EBotSidebar';
import StatusBar from './components/StatusBar';
import { usePlanner } from './hooks/usePlanner';
import { useEBot } from './hooks/useEBot';

export default function App() {
  const [boardName, setBoardName] = useState('My Project Board');
  const [ebotOpen, setEbotOpen] = useState(false);
  const [ebotResponse, setEbotResponse] = useState('');

  const planner = usePlanner();
  const { connected, loading, extractTasks, suggestPriority } = useEBot();

  const handleAddTask = useCallback(() => {
    planner.addTask({
      title: 'New Task',
      description: '',
      status: 'todo',
      priority: 'medium',
      dueDate: '',
      tags: [],
    });
  }, [planner]);

  const handleEBotAction = useCallback(
    async (action: string, input?: string) => {
      if (!connected) return;
      setEbotResponse('');
      try {
        let response = '';
        switch (action) {
          case 'extract-tasks': {
            if (input) {
              response = await extractTasks(input);
              response = `📝 **Extracted Tasks**\n\n${response}`;
            }
            break;
          }
          case 'prioritize': {
            const todoTasks = planner.tasks
              .filter((t) => t.status !== 'done')
              .map((t) => t.title)
              .join('\n');
            if (!todoTasks) {
              response = '⚠️ No open tasks to prioritize.';
            } else {
              response = await suggestPriority(todoTasks);
              response = `🎯 **Priority Suggestions**\n\n${response}`;
            }
            break;
          }
          case 'summarize': {
            const { total, todo, inProgress, done } = planner.counts;
            response = `📊 **Board Summary**\n\nTotal: ${total} tasks\n📝 To Do: ${todo}\n🔄 In Progress: ${inProgress}\n✅ Done: ${done}\n\nCompletion: ${total > 0 ? Math.round((done / total) * 100) : 0}%`;
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
    [connected, extractTasks, suggestPriority, planner],
  );

  return (
    <div className="eplanner-app">
      <TopBar
        boardName={boardName}
        onBoardNameChange={setBoardName}
        ebotSidebarOpen={ebotOpen}
        onToggleEBot={() => setEbotOpen((p) => !p)}
        connected={connected}
        onAddTask={handleAddTask}
      />
      <div className="eplanner-body">
        <BoardView
          tasks={planner.tasks}
          filterByStatus={planner.filterByStatus}
          onSelectTask={planner.setSelectedTaskId}
          onMoveTask={planner.moveTask}
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
      {planner.selectedTask && (
        <TaskDetail
          task={planner.selectedTask}
          onUpdate={planner.updateTask}
          onRemove={planner.removeTask}
          onClose={() => planner.setSelectedTaskId(null)}
        />
      )}
      <StatusBar
        total={planner.counts.total}
        todo={planner.counts.todo}
        inProgress={planner.counts.inProgress}
        done={planner.counts.done}
        connected={connected}
      />
    </div>
  );
}
