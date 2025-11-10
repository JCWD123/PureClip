import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Task {
  task_id: string
  status: string
  progress: number
  result_url?: string
  error_message?: string
  created_at: string
  updated_at: string
}

interface TaskState {
  currentTask: Task | null
  taskList: Task[]
  history: any[]
}

const initialState: TaskState = {
  currentTask: null,
  taskList: [],
  history: []
}

const taskSlice = createSlice({
  name: 'task',
  initialState,
  reducers: {
    setCurrentTask: (state, action: PayloadAction<Task | null>) => {
      state.currentTask = action.payload
    },
    updateCurrentTask: (state, action: PayloadAction<Partial<Task>>) => {
      if (state.currentTask) {
        state.currentTask = { ...state.currentTask, ...action.payload }
      }
    },
    setTaskList: (state, action: PayloadAction<Task[]>) => {
      state.taskList = action.payload
    },
    setHistory: (state, action: PayloadAction<any[]>) => {
      state.history = action.payload
    }
  }
})

export const {
  setCurrentTask,
  updateCurrentTask,
  setTaskList,
  setHistory
} = taskSlice.actions

export default taskSlice.reducer






