import { useState } from "react"
import { register } from "../api/auth"
import { useNavigate } from "react-router-dom"
import Passmodal from "../passmodal/Passmodal"
import "../background.css"
import "../auth.css"

function isStrongPassword(password: string) {
  return (
    password.length >= 8 &&
    /[a-zA-Z]/.test(password) &&
    /\d/.test(password)
  )
}

export default function Register() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const navigate = useNavigate()

  async function submit() {
    setError("")
    if (!username || !password) {
        setError("Заполните все поля")
        return
    }

    if (!isStrongPassword(password)) {
        setShowPasswordModal(true)
        return
    }


    try {
      const data = await register(username, password, "ru")
      localStorage.setItem("access_token", data.access_token)
      localStorage.setItem("refresh_token", data.refresh_token)
      navigate("/chat")
    } catch (e: any) {
      if (e.response?.status === 409) {
        setError("Пользователь уже существует. Войдите.")
      } else {
        setError("Ошибка регистрации")
      }
    }
  }

  return (
    <div className="auth-page">
        <div className="bg" />

        <div className="auth-card">
        <h1 className="logo">onlyjobless</h1>
        <p className="subtitle">Создай аккаунт и начни тренироваться</p>

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

        <button onClick={submit}>Зарегистрироваться</button>

        <p className="auth-hint">
            Уже есть аккаунт?{" "}
            <span onClick={() => navigate("/login")}>
            Войти
            </span>
        </p>
        </div>

        {/* 👇 ВОТ ЗДЕСЬ */}
        <Passmodal
        open={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
        message="Пароль должен быть ≥8 символов и содержать буквы и цифры"
        />
    </div>
    )
}