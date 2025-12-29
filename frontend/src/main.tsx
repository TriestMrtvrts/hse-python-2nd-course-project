import ReactDOM from "react-dom/client"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"

import Chat from "./pages/Chat"
import Login from "./pages/Login"
import Register from "./pages/Register"
import "./index.css"

function RootRedirect() {
  const token = localStorage.getItem("access_token")
  return token ? <Navigate to="/chat" /> : <Navigate to="/login" />
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/chat" element={<Chat />} />
    </Routes>
  </BrowserRouter>
)