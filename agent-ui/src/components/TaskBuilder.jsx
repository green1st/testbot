import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Wand2, 
  Globe, 
  Search, 
  FileText, 
  ShoppingCart,
  Mail,
  Plus,
  X
} from 'lucide-react'

const TASK_TEMPLATES = [
  {
    id: 'web-search',
    name: 'Web Search',
    icon: Search,
    description: 'Search for information on the web',
    template: 'Navigate to Google and search for "{query}"',
    fields: [
      { name: 'query', label: 'Search Query', type: 'text', placeholder: 'autonomous agents' }
    ]
  },
  {
    id: 'website-visit',
    name: 'Visit Website',
    icon: Globe,
    description: 'Navigate to a specific website',
    template: 'Navigate to {url} and read the page content',
    fields: [
      { name: 'url', label: 'Website URL', type: 'url', placeholder: 'https://example.com' }
    ]
  },
  {
    id: 'form-fill',
    name: 'Fill Form',
    icon: FileText,
    description: 'Fill out a form on a website',
    template: 'Navigate to {url}, find the form, and fill it with the following data: {data}',
    fields: [
      { name: 'url', label: 'Form URL', type: 'url', placeholder: 'https://example.com/contact' },
      { name: 'data', label: 'Form Data', type: 'textarea', placeholder: 'Name: John Doe\nEmail: john@example.com' }
    ]
  },
  {
    id: 'data-extract',
    name: 'Extract Data',
    icon: FileText,
    description: 'Extract specific data from a webpage',
    template: 'Navigate to {url} and extract {dataType} from the page',
    fields: [
      { name: 'url', label: 'Website URL', type: 'url', placeholder: 'https://example.com' },
      { name: 'dataType', label: 'Data to Extract', type: 'text', placeholder: 'product prices, contact information, etc.' }
    ]
  },
  {
    id: 'online-shopping',
    name: 'Product Search',
    icon: ShoppingCart,
    description: 'Search for products online',
    template: 'Navigate to {site} and search for "{product}", then show me the top results with prices',
    fields: [
      { name: 'site', label: 'Shopping Site', type: 'text', placeholder: 'Amazon, eBay, etc.' },
      { name: 'product', label: 'Product Name', type: 'text', placeholder: 'wireless headphones' }
    ]
  },
  {
    id: 'email-compose',
    name: 'Email Task',
    icon: Mail,
    description: 'Help with email-related tasks',
    template: 'Navigate to {emailSite} and help me {action}',
    fields: [
      { name: 'emailSite', label: 'Email Service', type: 'text', placeholder: 'Gmail, Outlook, etc.' },
      { name: 'action', label: 'Action', type: 'text', placeholder: 'compose an email, check inbox, etc.' }
    ]
  }
]

export const TaskBuilder = ({ onTaskGenerated, className = "" }) => {
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [fieldValues, setFieldValues] = useState({})
  const [customTask, setCustomTask] = useState('')
  const [showCustom, setShowCustom] = useState(false)

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template)
    setFieldValues({})
    setShowCustom(false)
  }

  const handleFieldChange = (fieldName, value) => {
    setFieldValues(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const generateTask = () => {
    if (showCustom) {
      onTaskGenerated(customTask)
      setCustomTask('')
      return
    }

    if (!selectedTemplate) return

    let task = selectedTemplate.template
    selectedTemplate.fields.forEach(field => {
      const value = fieldValues[field.name] || ''
      task = task.replace(`{${field.name}}`, value)
    })

    onTaskGenerated(task)
    setFieldValues({})
    setSelectedTemplate(null)
  }

  const isFormValid = () => {
    if (showCustom) return customTask.trim().length > 0
    
    if (!selectedTemplate) return false
    
    return selectedTemplate.fields.every(field => {
      const value = fieldValues[field.name]
      return value && value.trim().length > 0
    })
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Wand2 className="w-5 h-5 mr-2" />
          Task Builder
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Template Selection */}
        {!selectedTemplate && !showCustom && (
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {TASK_TEMPLATES.map((template) => (
                <Button
                  key={template.id}
                  variant="outline"
                  className="h-auto p-4 text-left justify-start"
                  onClick={() => handleTemplateSelect(template)}
                >
                  <div className="flex items-start space-x-3">
                    <template.icon className="w-5 h-5 mt-0.5 text-blue-500" />
                    <div>
                      <div className="font-medium">{template.name}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {template.description}
                      </div>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
            
            <div className="text-center">
              <Button 
                variant="ghost" 
                onClick={() => setShowCustom(true)}
                className="text-sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                Write Custom Task
              </Button>
            </div>
          </div>
        )}

        {/* Template Form */}
        {selectedTemplate && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <selectedTemplate.icon className="w-5 h-5 text-blue-500" />
                <Badge variant="secondary">{selectedTemplate.name}</Badge>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setSelectedTemplate(null)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {selectedTemplate.fields.map((field) => (
              <div key={field.name} className="space-y-2">
                <Label htmlFor={field.name}>{field.label}</Label>
                {field.type === 'textarea' ? (
                  <Textarea
                    id={field.name}
                    placeholder={field.placeholder}
                    value={fieldValues[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    rows={3}
                  />
                ) : (
                  <Input
                    id={field.name}
                    type={field.type}
                    placeholder={field.placeholder}
                    value={fieldValues[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  />
                )}
              </div>
            ))}

            {/* Preview */}
            <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Label className="text-xs text-gray-500 dark:text-gray-400">Preview:</Label>
              <p className="text-sm mt-1">
                {selectedTemplate.fields.reduce((template, field) => {
                  const value = fieldValues[field.name] || `{${field.name}}`
                  return template.replace(`{${field.name}}`, value)
                }, selectedTemplate.template)}
              </p>
            </div>
          </div>
        )}

        {/* Custom Task */}
        {showCustom && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant="secondary">Custom Task</Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowCustom(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="custom-task">Task Description</Label>
              <Textarea
                id="custom-task"
                placeholder="Describe what you want the agent to do..."
                value={customTask}
                onChange={(e) => setCustomTask(e.target.value)}
                rows={4}
              />
            </div>
          </div>
        )}

        {/* Generate Button */}
        {(selectedTemplate || showCustom) && (
          <Button 
            onClick={generateTask} 
            disabled={!isFormValid()}
            className="w-full"
          >
            <Wand2 className="w-4 h-4 mr-2" />
            Generate Task
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

