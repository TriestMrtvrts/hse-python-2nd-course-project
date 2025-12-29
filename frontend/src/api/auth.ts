import api from "./client"

export async function register(
  username: string,
  password: string,
  preferred_language: string
) {
  const res = await api.post("/auth/register", {
    username,
    password,
    preferred_language,
  })
  return res.data
}

export async function login(username: string, password: string) {
  const res = await api.post("/auth/login", {
    username,
    password,
  })
  return res.data
}