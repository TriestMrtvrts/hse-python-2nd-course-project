import { useState } from "react"
import { login } from "../api/auth"
import { useNavigate } from "react-router-dom"
import "../background.css"
import "../auth.css"

export default function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  async function submit() {
    setError("")

    if (!username || !password) {
      setError("Введите логин и пароль")
      return
    }

    try {
      const data = await login(username, password)
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      navigate("/chat")
    } catch (e: any) {
      if (e.response?.status === 401) {
        setError("Неверный логин или пароль")
      } else {
        setError("Ошибка входа")
      }
    }
  }

  return (
    <div className="auth-page">
      <div className="bg" />

      <div className="auth-card">
        <h1 className="logo">onlyjobless</h1>
        <p className="subtitle">Подготовка к интервью без стресса</p>

        {error && <div className="auth-error">{error}</div>}

        <input
          placeholder="Username"
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={submit}>Войти</button>

        <p className="auth-hint">
          Нет аккаунта?{" "}
          <span onClick={() => navigate("/register")}>
            Зарегистрироваться
          </span>
        </p>
      </div>
    </div>
  )
}