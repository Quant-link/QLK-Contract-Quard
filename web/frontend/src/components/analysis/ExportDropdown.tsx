import { useState } from 'react'
import { Download, FileText, FileSpreadsheet, FileImage, Loader2 } from 'lucide-react'
import { Button } from '../ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu'
import { useToast } from '../../hooks/use-toast'
import { apiService } from '../../services/api'

interface ExportDropdownProps {
  analysisId: string
  filename: string
  disabled?: boolean
}

export default function ExportDropdown({ analysisId, filename, disabled = false }: ExportDropdownProps) {
  const [isExporting, setIsExporting] = useState(false)
  const [exportingFormat, setExportingFormat] = useState<string | null>(null)
  const { toast } = useToast()

  const handleExport = async (format: 'json' | 'csv' | 'pdf') => {
    try {
      setIsExporting(true)
      setExportingFormat(format)

      await apiService.downloadAnalysis(analysisId, format, filename)

      toast({
        title: "Export successful",
        description: `Analysis exported as ${format.toUpperCase()} file.`,
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast({
        title: "Export failed",
        description: `Failed to export analysis as ${format.toUpperCase()}.`,
        variant: "destructive",
      })
    } finally {
      setIsExporting(false)
      setExportingFormat(null)
    }
  }

  const exportOptions = [
    {
      format: 'json' as const,
      label: 'JSON',
      description: 'Machine-readable format',
      icon: FileText,
    },
    {
      format: 'csv' as const,
      label: 'CSV',
      description: 'Spreadsheet format',
      icon: FileSpreadsheet,
    },
    {
      format: 'pdf' as const,
      label: 'PDF',
      description: 'Professional report',
      icon: FileImage,
    },
  ]

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          disabled={disabled || isExporting}
          className="gap-2"
        >
          {isExporting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          {isExporting ? `Exporting ${exportingFormat?.toUpperCase()}...` : 'Export'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <div className="px-2 py-1.5 text-sm font-medium text-muted-foreground">
          Export Analysis
        </div>
        <DropdownMenuSeparator />
        {exportOptions.map((option) => {
          const Icon = option.icon
          const isCurrentlyExporting = isExporting && exportingFormat === option.format
          
          return (
            <DropdownMenuItem
              key={option.format}
              onClick={() => handleExport(option.format)}
              disabled={isExporting}
              className="flex items-center gap-3 cursor-pointer"
            >
              <div className="flex items-center gap-2 flex-1">
                {isCurrentlyExporting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
                <div className="flex flex-col">
                  <span className="font-medium">{option.label}</span>
                  <span className="text-xs text-muted-foreground">
                    {option.description}
                  </span>
                </div>
              </div>
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
