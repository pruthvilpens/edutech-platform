'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import Link from 'next/link'

interface Document {
  id: string
  original_filename: string
  file_size: number
  status: string
  created_at: string
  processed_text?: string
}

export default function InstructorDocumentViewPage() {
  const params = useParams()
  const { data: session } = useSession()
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<string>('')
  const [studyQuestions, setStudyQuestions] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'info' | 'summary' | 'questions'>('info')
  
  const documentId = params.id as string

  useEffect(() => {
    fetchDocument()
  }, [documentId])

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

  const fetchSummary = async () => {
    try {
      const response = await fetch(`/api/documents/${documentId}/summary`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setSummary(data.summary)
      }
    } catch (err) {
      console.error('Error loading summary:', err)
    }
  }

  const fetchStudyQuestions = async () => {
    try {
      const response = await fetch(`/api/documents/${documentId}/study-questions`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setStudyQuestions(data.questions)
      }
    } catch (err) {
      console.error('Error loading study questions:', err)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
          href="/dashboard/instructor/documents"
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
          href="/dashboard/instructor/documents"
          className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
        >
          ← Back to Documents
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{document.original_filename}</h1>
        <div className="flex items-center space-x-4 mt-2">
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${
              document.status === 'processed'
                ? 'bg-green-100 text-green-800'
                : document.status === 'processing'
                ? 'bg-yellow-100 text-yellow-800'
                : document.status === 'failed'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {document.status}
          </span>
          <span className="text-gray-600">
            Size: {formatFileSize(document.file_size)}
          </span>
          <span className="text-gray-600">
            Uploaded: {formatDate(document.created_at)}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('info')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'info'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Document Info
          </button>
          {document.status === 'processed' && (
            <>
              <button
                onClick={() => {
                  setActiveTab('summary')
                  if (!summary) fetchSummary()
                }}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'summary'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                AI Summary
              </button>
              <button
                onClick={() => {
                  setActiveTab('questions')
                  if (!studyQuestions) fetchStudyQuestions()
                }}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'questions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Study Questions
              </button>
            </>
          )}
        </nav>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 gap-6">
        {activeTab === 'info' && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Document Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Filename</label>
                <p className="mt-1 text-sm text-gray-900">{document.original_filename}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">File Size</label>
                <p className="mt-1 text-sm text-gray-900">{formatFileSize(document.file_size)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <p className="mt-1">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      document.status === 'processed'
                        ? 'bg-green-100 text-green-800'
                        : document.status === 'processing'
                        ? 'bg-yellow-100 text-yellow-800'
                        : document.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {document.status}
                  </span>
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Upload Date</label>
                <p className="mt-1 text-sm text-gray-900">{formatDate(document.created_at)}</p>
              </div>
            </div>

            {document.status === 'processed' && (
              <div className="mt-6">
                <label className="text-sm font-medium text-gray-700">Usage</label>
                <p className="mt-2 text-sm text-gray-600">
                  This document is now available for students to view and chat with. 
                  Students can ask questions about the content and receive AI-powered responses.
                </p>
              </div>
            )}

            {document.status === 'processing' && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="animate-spin h-5 w-5 border-2 border-yellow-400 border-t-transparent rounded-full"></div>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Processing Document</h3>
                    <p className="mt-1 text-sm text-yellow-700">
                      The document is being processed to extract text content. This may take a few minutes.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {document.status === 'failed' && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Processing Failed</h3>
                    <p className="mt-1 text-sm text-red-700">
                      There was an error processing this document. Please try uploading again.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">AI-Generated Summary</h3>
            {summary ? (
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap text-gray-700">{summary}</p>
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
            <h3 className="text-lg font-semibold mb-4">AI-Generated Study Questions</h3>
            {studyQuestions ? (
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap text-gray-700">{studyQuestions}</div>
              </div>
            ) : (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}