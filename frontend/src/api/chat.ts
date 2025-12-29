import api from "./client"

/**
 * Создать новый чат
 */
export async function newChat() {
  const res = await api.post("/chat/new")
  return res.data
}

/**
 * Отправить сообщение в чат
 */
export async function sendMessage(chatId: string, content: string) {
  const res = await api.post(`/chat/${chatId}/message`, { content })
  return res.data.reply   // 👈 ВАЖНО
}

/**
 * Подсказка (через обычный message)
 */
export async function getHint(chatId: string) {
  return sendMessage(chatId, "Дай подсказку")
}

/**
 * Идеальный ответ
 */
export async function getAnswer(chatId: string) {
  return sendMessage(chatId, "Дай идеальный ответ")
}

/**
 * Завершить интервью и получить оценку
 */
export async function finishChat(chatId: string) {
  return sendMessage(chatId, "Заверши интервью и дай оценку")
}

export async function listChats() {
  const res = await api.get("/chat")
  return res.data
}

export async function loadChat(chatId: string) {
  const res = await api.get(`/chat/${chatId}`)
  return res.data
}

export async function getChats() {
  const res = await api.get("/chat")
  return res.data
}

export async function getChat(chatId: string) {
  const res = await api.get(`/chat/${chatId}`)
  return res.data
}