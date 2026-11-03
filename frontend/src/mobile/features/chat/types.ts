export type ChatRole = "system" | "user" | "assistant"

export interface ChatMessage {
  role: ChatRole
  content: string
}

export interface ChatResult {
  content: string
  model: string
  request_id: string | null
  usage: {
    input_tokens: number | null
    output_tokens: number | null
    total_tokens: number | null
  }
}

export interface ChatEntry extends ChatMessage {
  id: string
}

