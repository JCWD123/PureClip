import { configureStore } from '@reduxjs/toolkit'
import taskReducer from './taskSlice'

const store = configureStore({
  reducer: {
    task: taskReducer
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store


