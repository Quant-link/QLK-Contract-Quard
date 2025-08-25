import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Shield, 
  Zap, 
  FileText, 
  Bell, 
  Save, 
  RotateCcw,
  Plus,
  Trash2,
  Download,
  Upload
} from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Label } from '../ui/label'
import { Input } from '../ui/input'
import { Textarea } from '../ui/textarea'
import { Switch } from '../ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Badge } from '../ui/badge'
import { Separator } from '../ui/separator'
import { useToast } from '../../hooks/use-toast'
import { useAnalysisSettingsStore } from '../../store/analysisSettingsStore'
import { SecurityLevel, VulnerabilityCategory, CustomRule } from '../../types'

export default function AnalysisSettings() {
  const { toast } = useToast()
  const {
    config,
    presets,
    current_preset,
    is_saving,
    validation_errors,
    updateConfig,
    updateSecurityLevel,
    updateVulnerabilityCategory,
    addCustomRule,
    removeCustomRule,
    updateCustomRule,
    loadPreset,
    saveAsPreset,
    deletePreset,
    validateConfig,
    saveConfig,
    resetToDefaults
  } = useAnalysisSettingsStore()

  const [newPresetName, setNewPresetName] = useState('')
  const [newPresetDescription, setNewPresetDescription] = useState('')
  const [showPresetDialog, setShowPresetDialog] = useState(false)

  const handleSaveConfig = async () => {
    if (!validateConfig()) {
      toast({
        title: "Validation Error",
        description: "Please fix the configuration errors before saving.",
        variant: "destructive"
      })
      return
    }

    try {
      await saveConfig()
      toast({
        title: "Settings Saved",
        description: "Analysis configuration has been saved successfully.",
      })
    } catch (error) {
      toast({
        title: "Save Failed",
        description: "Failed to save analysis configuration.",
        variant: "destructive"
      })
    }
  }

  const handleSaveAsPreset = () => {
    if (!newPresetName.trim()) {
      toast({
        title: "Invalid Name",
        description: "Please enter a preset name.",
        variant: "destructive"
      })
      return
    }

    saveAsPreset(newPresetName, newPresetDescription)
    setNewPresetName('')
    setNewPresetDescription('')
    setShowPresetDialog(false)
    
    toast({
      title: "Preset Saved",
      description: `Preset "${newPresetName}" has been created.`,
    })
  }

  const securityLevelOptions: { value: SecurityLevel; label: string; description: string }[] = [
    {
      value: 'basic',
      label: 'Basic',
      description: 'Essential security checks for quick analysis'
    },
    {
      value: 'standard',
      label: 'Standard',
      description: 'Comprehensive security analysis for most use cases'
    },
    {
      value: 'advanced',
      label: 'Advanced',
      description: 'Deep analysis with advanced vulnerability detection'
    },
    {
      value: 'enterprise',
      label: 'Enterprise',
      description: 'Maximum security coverage for production systems'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analysis Settings</h2>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            Configure security analysis parameters and preferences
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={resetToDefaults}
            className="border-gray-300 dark:border-gray-600"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          
          <Button
            onClick={handleSaveConfig}
            disabled={is_saving}
            className="btn-custom-primary"
          >
            <Save className="h-4 w-4 mr-2" />
            {is_saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </div>

      {/* Presets Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" style={{ color: '#4dace1' }} />
            Configuration Presets
          </CardTitle>
          <CardDescription>
            Quick-start configurations for different analysis scenarios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {presets.map((preset) => (
              <motion.div
                key={preset.id}
                whileHover={{ scale: 1.02 }}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  current_preset === preset.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
                onClick={() => loadPreset(preset.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{preset.name}</h4>
                  {!preset.is_default && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        deletePreset(preset.id)
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {preset.description}
                </p>
                <div className="mt-2">
                  <Badge 
                    variant="outline" 
                    className="text-xs"
                    style={{ borderColor: '#4dace1', color: '#4dace1' }}
                  >
                    {preset.config.security_level}
                  </Badge>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowPresetDialog(true)}
              className="border-gray-300 dark:border-gray-600"
            >
              <Plus className="h-4 w-4 mr-2" />
              Save as Preset
            </Button>
          </div>

          {/* Save Preset Dialog */}
          {showPresetDialog && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 border rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <h4 className="font-medium mb-3">Save Current Configuration as Preset</h4>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="preset-name">Preset Name</Label>
                  <Input
                    id="preset-name"
                    value={newPresetName}
                    onChange={(e) => setNewPresetName(e.target.value)}
                    placeholder="Enter preset name"
                  />
                </div>
                <div>
                  <Label htmlFor="preset-description">Description</Label>
                  <Textarea
                    id="preset-description"
                    value={newPresetDescription}
                    onChange={(e) => setNewPresetDescription(e.target.value)}
                    placeholder="Enter preset description"
                    rows={2}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Button onClick={handleSaveAsPreset} className="btn-custom-primary">
                    Save Preset
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowPresetDialog(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Main Settings Tabs */}
      <Tabs defaultValue="security" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="security" className="flex items-center">
            <Shield className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="scope" className="flex items-center">
            <Zap className="h-4 w-4 mr-2" />
            Analysis Scope
          </TabsTrigger>
          <TabsTrigger value="reports" className="flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Reports
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
        </TabsList>

        {/* Security Configuration Tab */}
        <TabsContent value="security" className="space-y-6">
          {/* Security Level */}
          <Card>
            <CardHeader>
              <CardTitle>Security Level</CardTitle>
              <CardDescription>
                Choose the depth and comprehensiveness of security analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {securityLevelOptions.map((option) => (
                  <motion.div
                    key={option.value}
                    whileHover={{ scale: 1.02 }}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      config.security_level === option.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                    onClick={() => updateSecurityLevel(option.value)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{option.label}</h4>
                      {config.security_level === option.value && (
                        <div 
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: '#4dace1' }}
                        />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {option.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Vulnerability Categories */}
          <Card>
            <CardHeader>
              <CardTitle>Vulnerability Categories</CardTitle>
              <CardDescription>
                Enable or disable specific types of security checks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {config.vulnerability_categories.map((category) => (
                  <div
                    key={category.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <Switch
                          checked={category.enabled}
                          onCheckedChange={(enabled) =>
                            updateVulnerabilityCategory(category.id, { enabled })
                          }
                        />
                        <div>
                          <h4 className="font-medium">{category.name}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {category.description}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Select
                        value={category.severity_threshold}
                        onValueChange={(value) =>
                          updateVulnerabilityCategory(category.id, {
                            severity_threshold: value as any
                          })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="CRITICAL">Critical</SelectItem>
                          <SelectItem value="HIGH">High</SelectItem>
                          <SelectItem value="MEDIUM">Medium</SelectItem>
                          <SelectItem value="LOW">Low</SelectItem>
                          <SelectItem value="INFO">Info</SelectItem>
                        </SelectContent>
                      </Select>
                      
                      <Badge 
                        variant="outline"
                        style={{ borderColor: '#4dace1', color: '#4dace1' }}
                      >
                        {category.detectors.length} detectors
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analysis Scope Tab */}
        <TabsContent value="scope" className="space-y-6">
          {/* Analysis Type */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Type</CardTitle>
              <CardDescription>
                Choose the scope and depth of analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    value: 'full',
                    label: 'Full Analysis',
                    description: 'Comprehensive analysis of all code and dependencies',
                    duration: '5-10 minutes'
                  },
                  {
                    value: 'quick',
                    label: 'Quick Scan',
                    description: 'Fast analysis focusing on critical vulnerabilities',
                    duration: '1-2 minutes'
                  },
                  {
                    value: 'custom',
                    label: 'Custom Scope',
                    description: 'Define specific files and functions to analyze',
                    duration: 'Variable'
                  }
                ].map((type) => (
                  <motion.div
                    key={type.value}
                    whileHover={{ scale: 1.02 }}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      config.analysis_scope.type === type.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                    onClick={() =>
                      updateConfig({
                        analysis_scope: { ...config.analysis_scope, type: type.value as any }
                      })
                    }
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{type.label}</h4>
                      {config.analysis_scope.type === type.value && (
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: '#4dace1' }}
                        />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                      {type.description}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      ~{type.duration}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Include Options */}
          <Card>
            <CardHeader>
              <CardTitle>Include Options</CardTitle>
              <CardDescription>
                Specify what types of files to include in analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    key: 'include_dependencies',
                    label: 'Dependencies',
                    description: 'Analyze imported libraries and external contracts'
                  },
                  {
                    key: 'include_test_files',
                    label: 'Test Files',
                    description: 'Include test files in security analysis'
                  },
                  {
                    key: 'include_examples',
                    label: 'Example Files',
                    description: 'Analyze example and demo code files'
                  }
                ].map((option) => (
                  <div key={option.key} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Switch
                        checked={config.analysis_scope[option.key as keyof typeof config.analysis_scope] as boolean}
                        onCheckedChange={(checked) =>
                          updateConfig({
                            analysis_scope: {
                              ...config.analysis_scope,
                              [option.key]: checked
                            }
                          })
                        }
                      />
                      <div>
                        <h4 className="font-medium">{option.label}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {option.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* File Limits */}
          <Card>
            <CardHeader>
              <CardTitle>File Limits</CardTitle>
              <CardDescription>
                Set limits for file size and complexity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="max-file-size">Maximum File Size (MB)</Label>
                  <Input
                    id="max-file-size"
                    type="number"
                    min="1"
                    max="100"
                    value={config.analysis_scope.max_file_size_mb}
                    onChange={(e) =>
                      updateConfig({
                        analysis_scope: {
                          ...config.analysis_scope,
                          max_file_size_mb: parseInt(e.target.value) || 10
                        }
                      })
                    }
                  />
                  <p className="text-xs text-gray-500">
                    Files larger than this will be skipped
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max-lines">Maximum Lines per File</Label>
                  <Input
                    id="max-lines"
                    type="number"
                    min="100"
                    max="50000"
                    value={config.analysis_scope.max_lines_per_file}
                    onChange={(e) =>
                      updateConfig({
                        analysis_scope: {
                          ...config.analysis_scope,
                          max_lines_per_file: parseInt(e.target.value) || 10000
                        }
                      })
                    }
                  />
                  <p className="text-xs text-gray-500">
                    Very large files will be analyzed partially
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Exclude Patterns */}
          <Card>
            <CardHeader>
              <CardTitle>Exclude Patterns</CardTitle>
              <CardDescription>
                Define file patterns to exclude from analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {config.analysis_scope.exclude_patterns.map((pattern, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="flex items-center space-x-1"
                    >
                      <span>{pattern}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-4 w-4 p-0"
                        onClick={() => {
                          const newPatterns = config.analysis_scope.exclude_patterns.filter((_, i) => i !== index)
                          updateConfig({
                            analysis_scope: {
                              ...config.analysis_scope,
                              exclude_patterns: newPatterns
                            }
                          })
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>

                <div className="flex space-x-2">
                  <Input
                    placeholder="Add exclude pattern (e.g., *.test.sol)"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const input = e.target as HTMLInputElement
                        const pattern = input.value.trim()
                        if (pattern && !config.analysis_scope.exclude_patterns.includes(pattern)) {
                          updateConfig({
                            analysis_scope: {
                              ...config.analysis_scope,
                              exclude_patterns: [...config.analysis_scope.exclude_patterns, pattern]
                            }
                          })
                          input.value = ''
                        }
                      }
                    }}
                  />
                  <Button
                    variant="outline"
                    onClick={(e) => {
                      const input = (e.target as HTMLElement).parentElement?.querySelector('input')
                      if (input) {
                        const pattern = input.value.trim()
                        if (pattern && !config.analysis_scope.exclude_patterns.includes(pattern)) {
                          updateConfig({
                            analysis_scope: {
                              ...config.analysis_scope,
                              exclude_patterns: [...config.analysis_scope.exclude_patterns, pattern]
                            }
                          })
                          input.value = ''
                        }
                      }
                    }}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                <div className="text-sm text-gray-500">
                  <p className="mb-1">Common patterns:</p>
                  <div className="flex flex-wrap gap-1">
                    {['*.test.sol', 'node_modules/**', 'target/**', 'vendor/**', '*.example.*'].map((pattern) => (
                      <Button
                        key={pattern}
                        variant="ghost"
                        size="sm"
                        className="h-6 text-xs"
                        onClick={() => {
                          if (!config.analysis_scope.exclude_patterns.includes(pattern)) {
                            updateConfig({
                              analysis_scope: {
                                ...config.analysis_scope,
                                exclude_patterns: [...config.analysis_scope.exclude_patterns, pattern]
                              }
                            })
                          }
                        }}
                      >
                        + {pattern}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          {/* Report Formats */}
          <Card>
            <CardHeader>
              <CardTitle>Report Formats</CardTitle>
              <CardDescription>
                Choose which formats to generate for analysis reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                  { value: 'json', label: 'JSON', description: 'Machine-readable format' },
                  { value: 'html', label: 'HTML', description: 'Interactive web report' },
                  { value: 'pdf', label: 'PDF', description: 'Printable document' },
                  { value: 'markdown', label: 'Markdown', description: 'Documentation format' },
                  { value: 'csv', label: 'CSV', description: 'Spreadsheet format' }
                ].map((format) => (
                  <div
                    key={format.value}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${
                      config.report_config.format.includes(format.value as any)
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      const currentFormats = config.report_config.format
                      const newFormats = currentFormats.includes(format.value as any)
                        ? currentFormats.filter(f => f !== format.value)
                        : [...currentFormats, format.value as any]

                      updateConfig({
                        report_config: {
                          ...config.report_config,
                          format: newFormats
                        }
                      })
                    }}
                  >
                    <div className="text-center">
                      <h4 className="font-medium">{format.label}</h4>
                      <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                        {format.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Detail Level */}
          <Card>
            <CardHeader>
              <CardTitle>Detail Level</CardTitle>
              <CardDescription>
                Control the amount of information included in reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  {
                    value: 'minimal',
                    label: 'Minimal',
                    description: 'Only critical findings and summary'
                  },
                  {
                    value: 'standard',
                    label: 'Standard',
                    description: 'All findings with basic details'
                  },
                  {
                    value: 'detailed',
                    label: 'Detailed',
                    description: 'Comprehensive information and context'
                  },
                  {
                    value: 'comprehensive',
                    label: 'Comprehensive',
                    description: 'Full analysis with all available data'
                  }
                ].map((level) => (
                  <motion.div
                    key={level.value}
                    whileHover={{ scale: 1.02 }}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      config.report_config.detail_level === level.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                    onClick={() =>
                      updateConfig({
                        report_config: {
                          ...config.report_config,
                          detail_level: level.value as any
                        }
                      })
                    }
                  >
                    <div className="text-center">
                      <h4 className="font-medium">{level.label}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {level.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Report Content Options */}
          <Card>
            <CardHeader>
              <CardTitle>Report Content</CardTitle>
              <CardDescription>
                Choose what information to include in reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    key: 'include_code_snippets',
                    label: 'Code Snippets',
                    description: 'Include relevant code sections in findings'
                  },
                  {
                    key: 'include_recommendations',
                    label: 'Recommendations',
                    description: 'Include fix suggestions and best practices'
                  },
                  {
                    key: 'include_references',
                    label: 'References',
                    description: 'Include links to documentation and resources'
                  },
                  {
                    key: 'include_metrics',
                    label: 'Metrics',
                    description: 'Include analysis statistics and performance data'
                  },
                  {
                    key: 'group_by_severity',
                    label: 'Group by Severity',
                    description: 'Organize findings by severity level'
                  },
                  {
                    key: 'group_by_category',
                    label: 'Group by Category',
                    description: 'Organize findings by vulnerability type'
                  }
                ].map((option) => (
                  <div key={option.key} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Switch
                        checked={config.report_config[option.key as keyof typeof config.report_config] as boolean}
                        onCheckedChange={(checked) =>
                          updateConfig({
                            report_config: {
                              ...config.report_config,
                              [option.key]: checked
                            }
                          })
                        }
                      />
                      <div>
                        <h4 className="font-medium">{option.label}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {option.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          {/* Email Notifications */}
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
              <CardDescription>
                Configure email alerts for analysis events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Enable Email Notifications</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      Receive email alerts for analysis events
                    </p>
                  </div>
                  <Switch
                    checked={config.notification_config.email_notifications.enabled}
                    onCheckedChange={(enabled) =>
                      updateConfig({
                        notification_config: {
                          ...config.notification_config,
                          email_notifications: {
                            ...config.notification_config.email_notifications,
                            enabled
                          }
                        }
                      })
                    }
                  />
                </div>

                {config.notification_config.email_notifications.enabled && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-4 pt-4 border-t"
                  >
                    <div className="space-y-2">
                      <Label htmlFor="email-recipients">Recipients</Label>
                      <Textarea
                        id="email-recipients"
                        placeholder="Enter email addresses (one per line)"
                        value={config.notification_config.email_notifications.recipients.join('\n')}
                        onChange={(e) => {
                          const recipients = e.target.value.split('\n').filter(email => email.trim())
                          updateConfig({
                            notification_config: {
                              ...config.notification_config,
                              email_notifications: {
                                ...config.notification_config.email_notifications,
                                recipients
                              }
                            }
                          })
                        }}
                        rows={3}
                      />
                    </div>

                    <div className="space-y-3">
                      <h5 className="font-medium">Send notifications for:</h5>
                      {[
                        { key: 'on_completion', label: 'Analysis Completion' },
                        { key: 'on_critical_findings', label: 'Critical Findings' },
                        { key: 'on_errors', label: 'Analysis Errors' },
                        { key: 'include_summary', label: 'Include Summary' }
                      ].map((option) => (
                        <div key={option.key} className="flex items-center space-x-2">
                          <Switch
                            checked={config.notification_config.email_notifications[option.key as keyof typeof config.notification_config.email_notifications] as boolean}
                            onCheckedChange={(checked) =>
                              updateConfig({
                                notification_config: {
                                  ...config.notification_config,
                                  email_notifications: {
                                    ...config.notification_config.email_notifications,
                                    [option.key]: checked
                                  }
                                }
                              })
                            }
                          />
                          <Label>{option.label}</Label>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Webhook Notifications */}
          <Card>
            <CardHeader>
              <CardTitle>Webhook Notifications</CardTitle>
              <CardDescription>
                Send HTTP notifications to external services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Enable Webhook Notifications</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      Send HTTP POST requests to external endpoints
                    </p>
                  </div>
                  <Switch
                    checked={config.notification_config.webhook_notifications.enabled}
                    onCheckedChange={(enabled) =>
                      updateConfig({
                        notification_config: {
                          ...config.notification_config,
                          webhook_notifications: {
                            ...config.notification_config.webhook_notifications,
                            enabled
                          }
                        }
                      })
                    }
                  />
                </div>

                {config.notification_config.webhook_notifications.enabled && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-4 pt-4 border-t"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="webhook-url">Webhook URL</Label>
                        <Input
                          id="webhook-url"
                          type="url"
                          placeholder="https://your-service.com/webhook"
                          value={config.notification_config.webhook_notifications.url}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                webhook_notifications: {
                                  ...config.notification_config.webhook_notifications,
                                  url: e.target.value
                                }
                              }
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="webhook-secret">Secret (Optional)</Label>
                        <Input
                          id="webhook-secret"
                          type="password"
                          placeholder="Webhook secret for verification"
                          value={config.notification_config.webhook_notifications.secret || ''}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                webhook_notifications: {
                                  ...config.notification_config.webhook_notifications,
                                  secret: e.target.value
                                }
                              }
                            })
                          }
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="retry-attempts">Retry Attempts</Label>
                        <Input
                          id="retry-attempts"
                          type="number"
                          min="0"
                          max="10"
                          value={config.notification_config.webhook_notifications.retry_attempts}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                webhook_notifications: {
                                  ...config.notification_config.webhook_notifications,
                                  retry_attempts: parseInt(e.target.value) || 0
                                }
                              }
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="timeout">Timeout (seconds)</Label>
                        <Input
                          id="timeout"
                          type="number"
                          min="5"
                          max="300"
                          value={config.notification_config.webhook_notifications.timeout_seconds}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                webhook_notifications: {
                                  ...config.notification_config.webhook_notifications,
                                  timeout_seconds: parseInt(e.target.value) || 30
                                }
                              }
                            })
                          }
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Slack Notifications */}
          <Card>
            <CardHeader>
              <CardTitle>Slack Notifications</CardTitle>
              <CardDescription>
                Send notifications to Slack channels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Enable Slack Notifications</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      Send messages to Slack channels via webhook
                    </p>
                  </div>
                  <Switch
                    checked={config.notification_config.slack_notifications.enabled}
                    onCheckedChange={(enabled) =>
                      updateConfig({
                        notification_config: {
                          ...config.notification_config,
                          slack_notifications: {
                            ...config.notification_config.slack_notifications,
                            enabled
                          }
                        }
                      })
                    }
                  />
                </div>

                {config.notification_config.slack_notifications.enabled && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-4 pt-4 border-t"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="slack-webhook">Slack Webhook URL</Label>
                        <Input
                          id="slack-webhook"
                          type="url"
                          placeholder="https://hooks.slack.com/services/..."
                          value={config.notification_config.slack_notifications.webhook_url}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                slack_notifications: {
                                  ...config.notification_config.slack_notifications,
                                  webhook_url: e.target.value
                                }
                              }
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="slack-channel">Channel</Label>
                        <Input
                          id="slack-channel"
                          placeholder="#security"
                          value={config.notification_config.slack_notifications.channel}
                          onChange={(e) =>
                            updateConfig({
                              notification_config: {
                                ...config.notification_config,
                                slack_notifications: {
                                  ...config.notification_config.slack_notifications,
                                  channel: e.target.value
                                }
                              }
                            })
                          }
                        />
                      </div>
                    </div>

                    <div className="space-y-3">
                      <h5 className="font-medium">Send notifications for:</h5>
                      {[
                        { key: 'on_completion', label: 'Analysis Completion' },
                        { key: 'on_critical_findings', label: 'Critical Findings' }
                      ].map((option) => (
                        <div key={option.key} className="flex items-center space-x-2">
                          <Switch
                            checked={config.notification_config.slack_notifications[option.key as keyof typeof config.notification_config.slack_notifications] as boolean}
                            onCheckedChange={(checked) =>
                              updateConfig({
                                notification_config: {
                                  ...config.notification_config,
                                  slack_notifications: {
                                    ...config.notification_config.slack_notifications,
                                    [option.key]: checked
                                  }
                                }
                              })
                            }
                          />
                          <Label>{option.label}</Label>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Real-time Updates */}
          <Card>
            <CardHeader>
              <CardTitle>Real-time Updates</CardTitle>
              <CardDescription>
                Configure live updates during analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Enable Real-time Updates</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Receive live progress updates via WebSocket
                  </p>
                </div>
                <Switch
                  checked={config.notification_config.real_time_updates}
                  onCheckedChange={(enabled) =>
                    updateConfig({
                      notification_config: {
                        ...config.notification_config,
                        real_time_updates: enabled
                      }
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
