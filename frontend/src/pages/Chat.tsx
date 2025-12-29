import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  newChat,
  sendMessage,
  getHint,
  getAnswer,
  finishChat,
  listChats,
  loadChat,
} from "../api/chat"
import "../chat.css"

type Message = {
  role: "user" | "assistant"
  content: string
}

type ChatItem = {
  id: string
  vacancy_title: string | null
  created_at: string
  finished: boolean
}

// ───────── helpers ─────────

function typeMessage(
  text: string,
  onUpdate: (value: string) => void,
  speed = 20
) {
  let i = 0
  const interval = setInterval(() => {
    i++
    onUpdate(text.slice(0, i))
    if (i >= text.length) clearInterval(interval)
  }, speed)
}

// ───────── component ─────────

export default function Chat() {
  const navigate = useNavigate()

  const [chatId, setChatId] = useState<string | null>(null)
  const [chatList, setChatList] = useState<ChatItem[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const startedRef = useRef(false)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  // ───────── effects ─────────

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    init()
  }, [])

  async function init() {
    try {
      const list = await listChats()
      setChatList(list)

      if (list.length > 0) {
        await openChat(list[0].id)
      } else {
        await startNewChat() 
      }
    } catch (e) {
      console.error("Ошибка инициализации чатов")
    }
  }

  // ───────── auth ─────────

  function logout() {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    navigate("/login")
  }

  // ───────── chat list ─────────

  async function refreshChatList() {
    try {
      const list = await listChats()
      setChatList(list)
    } catch {
      console.error("Не удалось загрузить список чатов")
    }
  }

  async function openChat(id: string) {
    setLoading(true)
    try {
      const chat = await loadChat(id)
      setChatId(id)
      setMessages(
        (chat.messages || []).map((m: any) => ({
          role: m.role,
          content: m.content,
        }))
      )
    } finally {
      setLoading(false)
    }
  }

  // ───────── new chat ─────────

  async function startNewChat() {
    setError("")
    setLoading(true)
    try {
      const res = await newChat()
      setChatId(res.chat_id)
      setMessages([])
      await refreshChatList()
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? "Не удалось создать чат")
    } finally {
      setLoading(false)
    }
  }

  // ───────── message helpers ─────────

  function pushUser(text: string) {
    setMessages((prev) => [...prev, { role: "user", content: text }])
  }

  function pushAssistantTyping(text: string) {
    setMessages((prev) => [...prev, { role: "assistant", content: "" }])

    typeMessage(text, (partial) => {
      setMessages((prev) => {
        const copy = [...prev]
        copy[copy.length - 1] = { role: "assistant", content: partial }
        return copy
      })
    })
  }

  // ───────── send message ─────────

  async function send() {
    if (!chatId || !input || loading) return

    const text = input
    setInput("")
    pushUser(text)

    setLoading(true)
    try {
      const reply = await sendMessage(chatId, text)
      pushAssistantTyping(reply || "(пустой ответ модели)")
    } catch {
      setError("Ошибка отправки сообщения")
    } finally {
      setLoading(false)
    }
  }

  // ───────── actions ─────────

  async function hint() {
    if (!chatId || loading) return
    pushUser("Дай подсказку")
    setLoading(true)
    try {
      const reply = await getHint(chatId)
      pushAssistantTyping(String(reply))
    } finally {
      setLoading(false)
    }
  }

  async function answer() {
    if (!chatId || loading) return
    pushUser("Покажи идеальный ответ")
    setLoading(true)
    try {
      const reply = await getAnswer(chatId)
      pushAssistantTyping(String(reply))
    } finally {
      setLoading(false)
    }
  }

  async function finish() {
    if (!chatId || loading) return
    pushUser("Подведи итоги интервью")
    setLoading(true)
    try {
      const reply = await finishChat(chatId)
      pushAssistantTyping(JSON.stringify(reply, null, 2))
      await refreshChatList()
    } finally {
      setLoading(false)
    }
  }

  // ───────── render ─────────

  return (
    <div className="chat-layout">
      {/* sidebar */}
      <div className="sidebar">
        

        <div className="chat-history">
          {chatList.map((c) => (
            <div
              key={c.id}
              className={`chat-item ${c.id === chatId ? "active" : ""}`}
              onClick={() => openChat(c.id)}
            >
              <div className="chat-title">
                {c.vacancy_title || "Новое интервью"}
              </div>
              <div className="chat-meta">
                {c.finished ? "✓ Завершено" : "● В процессе"}
              </div>
            </div>
          ))}
        </div>

        <hr />
        <button onClick={logout}>Logout</button>
      </div>

      {/* chat */}
      <div className="chat">
        <div className="messages">
          {error && <div className="message assistant error">{error}</div>}

          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.content}
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <em>Печатает…</em>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="input-panel">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Первое сообщение — название вакансии"
            onKeyDown={(e) => e.key === "Enter" && send()}
            disabled={loading}
          />

          <button onClick={send} disabled={loading}>Send</button>
          <button onClick={hint} disabled={loading}>Hint</button>
          <button onClick={answer} disabled={loading}>Answer</button>
          <button onClick={finish} disabled={loading}>Finish</button>
        </div>
      </div>
    </div>
  )
}