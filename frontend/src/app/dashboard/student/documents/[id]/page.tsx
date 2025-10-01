'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import Link from 'next/link'
import MindMap from '@/components/features/MindMap'

interface Document {
  id: string
  original_filename: string
  file_size: number
  status: string
  created_at: string
  processed_text?: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface ChatResponse {
  message: ChatMessage
  ai_response: ChatMessage
}

export default function DocumentViewPage() {
  const params = useParams()
  const { data: session } = useSession()
  const [document, setDocument] = useState<Document | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [chatLoading, setChatLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<string>('')
  const [studyQuestions, setStudyQuestions] = useState<string>('')
  const [summaryLoaded, setSummaryLoaded] = useState(false)
  const [questionsLoaded, setQuestionsLoaded] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'summary' | 'questions' | 'mindmap'>('chat')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const documentId = params.id as string

  useEffect(() => {
    fetchDocument()
  }, [documentId])

  useEffect(() => {
    if (session?.accessToken) {
      fetchChatHistory()
    }
  }, [documentId, session?.accessToken])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchDocument = async () => {
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setDocument(data)
      } else {
        setError('Failed to fetch document')
      }
    } catch (err) {
      setError('Error loading document')
    } finally {
      setLoading(false)
    }
  }

  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`/api/documents/${documentId}/chat/sessions`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const sessions = await response.json()
        if (sessions.length > 0) {
          setMessages(sessions[0].messages || [])
        }
      }
    } catch (err) {
      console.error('Error loading chat history:', err)
    }
  }

  const fetchSummary = async () => {
    if (summaryLoaded) return // Don't fetch if already loaded
    
    try {
      const response = await fetch(`/api/documents/${documentId}/summary`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setSummary(data.summary)
        setSummaryLoaded(true)
      }
    } catch (err) {
      console.error('Error loading summary:', err)
    }
  }

  const fetchStudyQuestions = async () => {
    if (questionsLoaded) return // Don't fetch if already loaded
    
    try {
      const response = await fetch(`/api/documents/${documentId}/study-questions`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setStudyQuestions(data.questions)
        setQuestionsLoaded(true)
      }
    } catch (err) {
      console.error('Error loading study questions:', err)
    }
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || chatLoading) return

    setChatLoading(true)
    const userMessage = currentMessage
    setCurrentMessage('')

    try {
      const response = await fetch(`/api/documents/${documentId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.accessToken}`,
        },
        body: JSON.stringify({ content: userMessage }),
      })

      if (response.ok) {
        const data: ChatResponse = await response.json()
        setMessages(prev => [...prev, data.message, data.ai_response])
      } else {
        setError('Failed to send message')
      }
    } catch (err) {
      setError('Error sending message')
    } finally {
      setChatLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="container mx-auto py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || 'Document not found'}
        </div>
        <Link
          href="/dashboard/student/documents"
          className="mt-4 inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Back to Documents
        </Link>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard/student/documents"
          className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
        >
          ← Back to Documents
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{document.original_filename}</h1>
        <p className="text-gray-600 mt-2">
          Uploaded on {formatDate(document.created_at)}
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('chat')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'chat'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Chat
          </button>
          <button
            onClick={() => {
              setActiveTab('summary')
              fetchSummary()
            }}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'summary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Summary
          </button>
          <button
            onClick={() => {
              setActiveTab('questions')
              fetchStudyQuestions()
            }}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'questions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Study Questions
          </button>
          <button
            onClick={() => setActiveTab('mindmap')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'mindmap'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Mind Map
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 gap-6">
        {activeTab === 'chat' && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200">
            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <p>Start a conversation about this document!</p>
                  <p className="text-sm mt-2">Ask questions, request explanations, or discuss the content.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                      }`}>
                        {formatDate(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full"></div>
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full" style={{ animationDelay: '0.1s' }}></div>
                      <div className="animate-bounce h-2 w-2 bg-gray-400 rounded-full" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="border-t border-gray-200 p-4">
              <div className="flex space-x-2">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about this document..."
                  className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={2}
                  disabled={chatLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!currentMessage.trim() || chatLoading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Document Summary</h3>
            {summary ? (
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap">{summary}</p>
              </div>
            ) : (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'questions' && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Study Questions</h3>
            {studyQuestions ? (
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap">{studyQuestions}</div>
              </div>
            ) : (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'mindmap' && (
          <MindMap documentId={documentId} />
        )}
      </div>
    </div>
  )
}