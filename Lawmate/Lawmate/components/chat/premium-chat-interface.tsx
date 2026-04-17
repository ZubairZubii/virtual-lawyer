"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Send,
  Paperclip,
  Mic,
  Sparkles,
  User,
  Bot,
  ChevronDown,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  status?: "sending" | "sent" | "error"
}

interface PremiumChatInterfaceProps {
  onSendMessage?: (message: string) => Promise<void>
  initialMessages?: Message[]
  placeholder?: string
  suggestedQuestions?: string[]
}

export function PremiumChatInterface({
  onSendMessage,
  initialMessages = [],
  placeholder = "Ask anything about criminal law...",
  suggestedQuestions = [
    "What are my rights during police custody?",
    "How do I apply for bail?",
    "What documents do I need for an FIR?",
    "Can you explain IPC Section 302?",
  ],
}: PremiumChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [showScrollDown, setShowScrollDown] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const handleScroll = () => {
      if (chatContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current
        setShowScrollDown(scrollHeight - scrollTop - clientHeight > 100)
      }
    }

    const container = chatContainerRef.current
    container?.addEventListener("scroll", handleScroll)
    return () => container?.removeEventListener("scroll", handleScroll)
  }, [])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
      status: "sent",
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }

    try {
      await onSendMessage?.(input.trim())

      // Simulate AI response
      setTimeout(() => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "This is a simulated AI response. In production, this would connect to your backend API for real legal guidance.",
          timestamp: new Date(),
          status: "sent",
        }
        setMessages((prev) => [...prev, aiMessage])
        setIsTyping(false)
      }, 1500)
    } catch (error) {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    setInput(question)
    textareaRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Chat Header */}
      <div className="border-b border-border/50 bg-card/30 backdrop-blur-sm px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <motion.div
              animate={{
                boxShadow: [
                  "0 0 0 0 rgba(59, 130, 246, 0)",
                  "0 0 0 8px rgba(59, 130, 246, 0.1)",
                  "0 0 0 0 rgba(59, 130, 246, 0)",
                ],
              }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="rounded-full"
            >
              <Avatar className="w-10 h-10 border-2 border-primary/20">
                <AvatarFallback className="bg-gradient-to-br from-primary to-accent">
                  <Bot className="w-5 h-5 text-primary-foreground" />
                </AvatarFallback>
              </Avatar>
            </motion.div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-background" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              Lawmate AI Assistant
              <Badge variant="secondary" className="text-xs gap-1">
                <Sparkles className="w-3 h-3" />
                Online
              </Badge>
            </h3>
            <p className="text-xs text-muted-foreground">Expert in Pakistan Criminal Law</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
        style={{ scrollBehavior: "smooth" }}
      >
        {/* Welcome Message */}
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Sparkles className="w-8 h-8 text-primary-foreground" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">Welcome to Lawmate AI</h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              I'm here to help you with criminal law questions, legal procedures, and case guidance.
            </p>

            {/* Suggested Questions */}
            <div className="max-w-2xl mx-auto">
              <p className="text-sm text-muted-foreground mb-3">Try asking:</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {suggestedQuestions.map((question, i) => (
                  <motion.button
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="p-4 rounded-lg border border-border bg-card hover:border-primary/50 hover:bg-card/80 transition-all text-left group"
                  >
                    <p className="text-sm text-foreground group-hover:text-primary transition-colors">
                      {question}
                    </p>
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false}>
          {messages.map((message, index) => (
            <MessageBubble key={message.id} message={message} index={index} />
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex gap-3"
          >
            <Avatar className="w-8 h-8 border border-border">
              <AvatarFallback className="bg-gradient-to-br from-primary to-accent">
                <Bot className="w-4 h-4 text-primary-foreground" />
              </AvatarFallback>
            </Avatar>
            <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl bg-card border border-border">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-primary rounded-full"
                  animate={{ y: [0, -8, 0] }}
                  transition={{
                    repeat: Infinity,
                    duration: 0.6,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll to Bottom Button */}
      <AnimatePresence>
        {showScrollDown && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute bottom-32 left-1/2 -translate-x-1/2"
          >
            <Button
              size="sm"
              variant="outline"
              className="rounded-full shadow-lg"
              onClick={scrollToBottom}
            >
              <ChevronDown className="w-4 h-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="border-t border-border/50 bg-card/30 backdrop-blur-sm p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end gap-2">
            <Button variant="outline" size="icon" className="shrink-0">
              <Paperclip className="w-4 h-4" />
            </Button>

            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                className="min-h-[44px] max-h-32 resize-none pr-12 bg-background"
                rows={1}
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-1 bottom-1 shrink-0"
              >
                <Mic className="w-4 h-4" />
              </Button>
            </div>

            <Button
              onClick={handleSend}
              disabled={!input.trim()}
              size="icon"
              className="shrink-0 bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg transition-all"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          <p className="text-xs text-muted-foreground mt-2 text-center">
            AI can make mistakes. Verify important information with a qualified lawyer.
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message, index }: { message: Message; index: number }) {
  const isUser = message.role === "user"
  const [showActions, setShowActions] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Avatar */}
      <Avatar className="w-8 h-8 border border-border shrink-0">
        {isUser ? (
          <AvatarFallback className="bg-muted">
            <User className="w-4 h-4" />
          </AvatarFallback>
        ) : (
          <AvatarFallback className="bg-gradient-to-br from-primary to-accent">
            <Bot className="w-4 h-4 text-primary-foreground" />
          </AvatarFallback>
        )}
      </Avatar>

      {/* Message Content */}
      <div className={cn("flex flex-col gap-2 max-w-[70%]", isUser && "items-end")}>
        <div
          className={cn(
            "px-4 py-3 rounded-2xl",
            isUser
              ? "bg-gradient-to-br from-primary to-accent text-primary-foreground rounded-tr-sm"
              : "bg-card border border-border rounded-tl-sm"
          )}
        >
          <p className={cn("text-sm leading-relaxed", isUser ? "text-primary-foreground" : "text-foreground")}>
            {message.content}
          </p>
        </div>

        {/* Message Actions */}
        <AnimatePresence>
          {showActions && !isUser && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="flex items-center gap-1"
            >
              <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">
                <Copy className="w-3 h-3 mr-1" />
                Copy
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2">
                <ThumbsUp className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2">
                <ThumbsDown className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2">
                <RefreshCw className="w-3 h-3" />
              </Button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Timestamp */}
        <span className="text-xs text-muted-foreground px-1">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>
    </motion.div>
  )
}
