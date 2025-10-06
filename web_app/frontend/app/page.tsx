"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function Home() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [message, setMessage] = useState("")
  const [processing, setProcessing] = useState(false)
  const router = useRouter()

  // If already logged in, go straight to chatbot
  useEffect(() => {
    if (typeof window === "undefined") return
    const token = localStorage.getItem("access_token")
    if (token) {
      router.replace("/chatbot")
    }
  }, [router])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage("")
    setProcessing(true)
    try {
      const res = await fetch(`http://localhost:8000/api/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })

      if (!res.ok) {
        let detail = `HTTP ${res.status}`
        const ct = res.headers.get("content-type") || ""
        try {
          if (ct.includes("application/json")) {
            const json = await res.json()
            if (json?.detail) detail = json.detail
            else detail = JSON.stringify(json)
          } else {
            detail = await res.text()
          }
        } catch {
          /* ignore parsing errors */
        }
        throw new Error(detail || "Login failed")
      }

  const data = await res.json()
  if (data?.access) localStorage.setItem("access_token", data.access)
  if (data?.refresh) localStorage.setItem("refresh_token", data.refresh)
  // record login timestamp (ms) for client-side 7-day countdown
  localStorage.setItem("login_time", String(Date.now()))
      if (username) localStorage.setItem("username", username)

      setMessage("✅ Logged in successfully! Redirecting…")
      setTimeout(() => router.push("/chatbot"), 400)
    } catch (err: any) {
      setMessage(err.message || "Login error")
      setProcessing(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-900 text-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-gray-800 text-gray-100 border-gray-700 shadow-xl shadow-black/30 p-8 rounded-xl w-96 border"
      >
        <div className="mb-4 text-center">
          <div className="text-sm font-medium tracking-wide text-violet-600">NL to SQL chatbot</div>
        </div>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-center w-full text-gray-100">Login</h1>
        </div>

        <label className="block text-sm mb-1">Username</label>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={processing}
          className="w-full p-3 mb-4 border rounded-lg focus:outline-none focus:ring-2 bg-gray-900 border-gray-700 placeholder-gray-400 focus:ring-violet-500"
        />

        <label className="block text-sm mb-1">Password</label>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={processing}
          className="w-full p-3 mb-6 border rounded-lg focus:outline-none focus:ring-2 bg-gray-900 border-gray-700 placeholder-gray-400 focus:ring-violet-500"
        />

        <button
          type="submit"
          disabled={processing}
          className={`w-full py-3 rounded-lg transition flex items-center justify-center gap-2 ${
            processing ? "bg-violet-400 cursor-not-allowed" : "bg-violet-600 hover:bg-violet-700"
          } text-white`}
        >
          {processing ? (
            <>
              <span role="img" aria-label="cat" className="animate-bounce">
                🐱
              </span>
              Processing…
            </>
          ) : (
            "Sign In"
          )}
        </button>

        {/* Admin page link */}
        <div className="mt-3 text-center text-xs">
                <a
                  href={`http://localhost:8000/admin/`}
                  className="text-violet-400 hover:text-violet-300 underline underline-offset-2"
                >
                  Open Admin
                </a>
              </div>

        {processing && (
          <div className="mt-3 text-center text-xs text-gray-300">
            <div className="relative h-2 w-full overflow-hidden rounded bg-gray-700">
              <div className="absolute inset-y-0 left-0 w-1/3 bg-violet-500 animate-[slide_1.2s_linear_infinite]"></div>
            </div>
            <style jsx>{`
              @keyframes slide {
                0% {
                  transform: translateX(-100%);
                }
                100% {
                  transform: translateX(300%);
                }
              }
            `}</style>
          </div>
        )}

        {message && (
          <p
            className={`mt-4 text-center text-sm italic ${
              message.includes("success")
                ? "text-green-500"
                : message.toLowerCase().includes("invalid")
                ? "text-red-500"
                : message.startsWith("HTTP 4")
                ? "text-red-400"
                : message.startsWith("HTTP 5")
                ? "text-orange-400"
                : "text-gray-300"
            }`}
          >
            {message}
          </p>
        )}
      </form>
    </main>
  )
}
