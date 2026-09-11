import axios, { type AxiosRequestConfig } from "axios"

import { createTraceId } from "@/utils/trace"

import { ApiError, normalizeApiError } from "./errors"
import type { ApiEnvelope } from "./types"

const timeout = Number(import.meta.env.VITE_API_TIMEOUT || 30000)

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: Number.isFinite(timeout) ? timeout : 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
})

http.interceptors.request.use((config) => {
  config.headers = config.headers ?? {}
  const traceId = config.headers["X-Trace-ID"] ?? config.headers["x-trace-id"]
  if (!traceId) {
    config.headers["X-Trace-ID"] = createTraceId()
  }
  const accessToken = localStorage.getItem("dingchi.access_token")
  if (accessToken && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error: unknown) => Promise.reject(normalizeApiError(error)),
)

export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await http.request<ApiEnvelope<T>>(config)
  const payload = response.data

  if (!payload.success) {
    throw new ApiError(
      payload.error.message,
      payload.error.code,
      response.status,
      payload.error.details,
    )
  }

  return payload.data
}
