import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Eye, 
  Download, 
  Maximize2, 
  Minimize2,
  RefreshCw,
  Monitor
} from 'lucide-react'

export const ScreenshotViewer = ({ 
  screenshot, 
  isLoading = false, 
  onRefresh,
  className = "" 
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [imageError, setImageError] = useState(false)

  const handleDownload = () => {
    if (!screenshot) return
    
    const link = document.createElement('a')
    link.href = screenshot
    link.download = `agent-screenshot-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleImageError = () => {
    setImageError(true)
  }

  const handleImageLoad = () => {
    setImageError(false)
  }

  return (
    <Card className={`${className} ${isExpanded ? 'fixed inset-4 z-50 bg-white dark:bg-gray-900' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg">
            <Monitor className="w-5 h-5 mr-2" />
            Browser View
            {isLoading && (
              <RefreshCw className="w-4 h-4 ml-2 animate-spin text-blue-500" />
            )}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              Live Preview
            </Badge>
            {onRefresh && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRefresh}
                disabled={isLoading}
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}
            {screenshot && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleDownload}
              >
                <Download className="w-4 h-4" />
              </Button>
            )}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`relative ${isExpanded ? 'h-[calc(100vh-200px)]' : 'h-64'} bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden`}>
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Capturing screenshot...
                </p>
              </div>
            </div>
          ) : screenshot && !imageError ? (
            <img 
              src={screenshot} 
              alt="Browser Screenshot" 
              className="w-full h-full object-contain"
              onError={handleImageError}
              onLoad={handleImageLoad}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Eye className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {imageError ? 'Failed to load screenshot' : 'No screenshot available'}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Screenshots will appear here during task execution
                </p>
              </div>
            </div>
          )}
        </div>
        
        {screenshot && (
          <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
            <p>Last updated: {new Date().toLocaleTimeString()}</p>
          </div>
        )}
      </CardContent>
      
      {isExpanded && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </Card>
  )
}

