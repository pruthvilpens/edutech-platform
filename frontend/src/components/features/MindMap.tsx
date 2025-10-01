'use client'

import { useState, useEffect } from 'react'

interface MindMapNode {
  name: string
  children?: MindMapNode[]
}

interface MindMapData {
  title: string
  children: MindMapNode[]
}

interface MindMapProps {
  documentId: string
}

interface TreeNodeProps {
  node: MindMapNode
  level: number
  isLast: boolean
  isFirst: boolean
}

const TreeNode: React.FC<TreeNodeProps> = ({ node, level, isLast, isFirst }) => {
  const [isExpanded, setIsExpanded] = useState(level < 3) // Auto-expand first 3 levels

  const hasChildren = node.children && node.children.length > 0
  
  // Color scheme based on level
  const getNodeStyle = (level: number) => {
    const styles = [
      'bg-blue-100 border-blue-300 text-blue-800', // Level 0
      'bg-green-100 border-green-300 text-green-800', // Level 1
      'bg-purple-100 border-purple-300 text-purple-800', // Level 2
      'bg-orange-100 border-orange-300 text-orange-800', // Level 3
      'bg-gray-100 border-gray-300 text-gray-800', // Level 4+
    ]
    return styles[Math.min(level, styles.length - 1)]
  }

  return (
    <div className="relative">
      <div className="flex items-center mb-2">
        {/* Connection lines */}
        {level > 0 && (
          <div className="flex items-center mr-2">
            <div className="w-4 h-px bg-gray-300"></div>
            {hasChildren && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-4 h-4 flex items-center justify-center text-xs bg-gray-200 border border-gray-300 rounded-full hover:bg-gray-300 transition-colors"
              >
                {isExpanded ? '−' : '+'}
              </button>
            )}
          </div>
        )}
        
        {/* Node content */}
        <div className={`
          px-3 py-2 rounded-lg border-2 shadow-sm
          ${getNodeStyle(level)}
          ${level === 0 ? 'font-bold text-lg' : level === 1 ? 'font-semibold' : 'font-medium'}
          max-w-xs
        `}>
          <div className="flex items-center">
            {level === 0 && hasChildren && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mr-2 text-sm"
              >
                {isExpanded ? '▼' : '▶'}
              </button>
            )}
            <span className="break-words">{node.name}</span>
          </div>
        </div>
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="ml-6 pl-4 border-l-2 border-gray-200">
          {node.children!.map((child, index) => (
            <TreeNode
              key={index}
              node={child}
              level={level + 1}
              isLast={index === node.children!.length - 1}
              isFirst={index === 0}
            />
          ))}
        </div>
      )}
    </div>
  )
}

const MindMap: React.FC<MindMapProps> = ({ documentId }) => {
  const [mindMapData, setMindMapData] = useState<MindMapData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMindMap = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/documents/${documentId}/mind-map`)
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setMindMapData(data.mind_map)
        } else {
          setError(data.error || 'Failed to generate mind map')
        }
      } else {
        setError('Failed to fetch mind map')
      }
    } catch (err) {
      setError('Error loading mind map')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMindMap()
  }, [documentId])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating mind map...</p>
          <p className="text-sm text-gray-500 mt-1">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <button
          onClick={fetchMindMap}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!mindMapData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No mind map data available</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Mind Map</h3>
        <p className="text-sm text-gray-600">
          Click on nodes with + or ▶ to expand/collapse sections
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <div className="min-w-max">
          {/* Root node */}
          <div className="mb-4">
            <div className="px-4 py-3 bg-indigo-100 border-2 border-indigo-300 text-indigo-900 rounded-lg font-bold text-xl inline-block shadow-md">
              {mindMapData.title}
            </div>
          </div>
          
          {/* Tree structure */}
          <div className="ml-6">
            {mindMapData.children.map((child, index) => (
              <TreeNode
                key={index}
                node={child}
                level={0}
                isLast={index === mindMapData.children.length - 1}
                isFirst={index === 0}
              />
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-xs text-gray-500 border-t pt-4">
        <p>💡 Tip: This mind map was automatically generated based on the document content. 
        Use it to visualize the document's structure and key concepts.</p>
      </div>
    </div>
  )
}

export default MindMap