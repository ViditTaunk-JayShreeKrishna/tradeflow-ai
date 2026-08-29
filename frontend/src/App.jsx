import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import HSClassifier from './pages/HSClassifier'
import LandedCost from './pages/LandedCost'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/hs-classifier" element={<HSClassifier />} />
        <Route path="/landed-cost" element={<LandedCost />} />
      </Routes>
    </BrowserRouter>
  )
}