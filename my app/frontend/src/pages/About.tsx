import { useState, useEffect } from 'react'

interface Task {
  id: number
  title: string
  assigned_to: string
  completed: boolean
  due_date: string
}

const API_URL = 'http://localhost:8000/api/chores'

export default function About() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [newTask, setNewTask] = useState('')
  const [newAssignee, setNewAssignee] = useState('')
  const [newDueDate, setNewDueDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Fetch chores from backend on component mount
  useEffect(() => {
    fetchChores()
  }, [])

  const fetchChores = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await fetch(API_URL)
      if (!response.ok) throw new Error('Failed to fetch chores')
      const data = await response.json()
      // Convert snake_case to match our interface
      const formattedTasks = data.chores.map((chore: any) => ({
        id: chore.id,
        title: chore.title,
        assigned_to: chore.assigned_to,
        completed: Boolean(chore.completed),
        due_date: chore.due_date,
      }))
      setTasks(formattedTasks)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chores')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const addTask = async () => {
    if (!newTask || !newAssignee) {
      setError('Please fill in task name and assignee')
      return
    }

    try {
      setError('')
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTask,
          assignedTo: newAssignee,
          dueDate: newDueDate || new Date().toISOString().split('T')[0],
        }),
      })

      if (!response.ok) throw new Error('Failed to add chore')
      const data = await response.json()
      const newChore = {
        id: data.chore.id,
        title: data.chore.title,
        assigned_to: data.chore.assigned_to,
        completed: Boolean(data.chore.completed),
        due_date: data.chore.due_date,
      }
      setTasks([newChore, ...tasks])
      setNewTask('')
      setNewAssignee('')
      setNewDueDate('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add chore')
      console.error(err)
    }
  }

  const toggleComplete = async (id: number) => {
    try {
      setError('')
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}), // Send empty object to toggle
      })

      if (!response.ok) throw new Error('Failed to update chore')
      const data = await response.json()
      const updatedChore = {
        id: data.chore.id,
        title: data.chore.title,
        assigned_to: data.chore.assigned_to,
        completed: Boolean(data.chore.completed),
        due_date: data.chore.due_date,
      }
      setTasks(tasks.map(t => t.id === id ? updatedChore : t))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update chore')
      console.error(err)
    }
  }

  const deleteTask = async (id: number) => {
    try {
      setError('')
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) throw new Error('Failed to delete chore')
      setTasks(tasks.filter(t => t.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete chore')
      console.error(err)
    }
  }

  const completedCount = tasks.filter(t => t.completed).length
  const totalCount = tasks.length

  return (
    <div className="todo-container">
      <h1>Family Chore List</h1>
      <p className="todo-stats">Progress: {completedCount} of {totalCount} tasks completed</p>
      
      {error && <div className="error-message">{error}</div>}

      <div className="add-task-section">
        <h2>Add New Chore</h2>
        <div className="add-task-form">
          <input
            type="text"
            placeholder="Task name (e.g., Wash dishes)"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTask()}
          />
          <input
            type="text"
            placeholder="Assigned to (e.g., John)"
            value={newAssignee}
            onChange={(e) => setNewAssignee(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTask()}
          />
          <input
            type="date"
            value={newDueDate}
            onChange={(e) => setNewDueDate(e.target.value)}
          />
          <button onClick={addTask}>Add Chore</button>
        </div>
      </div>

      <div className="tasks-section">
        <h2>Chores</h2>
        {loading ? (
          <p className="no-tasks">Loading chores...</p>
        ) : tasks.length === 0 ? (
          <p className="no-tasks">No chores yet! Great job! 🎉</p>
        ) : (
          <ul className="task-list">
            {tasks.map(task => (
              <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
                <div className="task-content">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleComplete(task.id)}
                    className="task-checkbox"
                  />
                  <div className="task-details">
                    <span className="task-title">{task.title}</span>
                    <span className="task-meta">
                      {task.assigned_to} • {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => deleteTask(task.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
