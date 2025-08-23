import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, AlertCircle, AlertTriangle } from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent } from '../ui/card'
import { Badge } from '../ui/badge'
import { Alert, AlertDescription, AlertTitle } from '../ui/alert'
import { formatFileSize, getFileTypeInfo } from '../../lib/utils'
import { validateFiles, validateFile } from '../../utils/fileValidation'
import { UploadedFile } from '../../types'

interface FileUploadProps {
  onFilesSelected: (files: UploadedFile[]) => void
  maxFiles?: number
  maxSize?: number // in MB
}

export default function FileUpload({ 
  onFilesSelected, 
  maxFiles = 5, 
  maxSize = 10 
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [warnings, setWarnings] = useState<string[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    const newErrors: string[] = []
    const newWarnings: string[] = []

    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error: any) => {
        if (error.code === 'file-too-large') {
          newErrors.push(`${file.name}: File too large (max ${maxSize}MB)`)
        } else if (error.code === 'file-invalid-type') {
          newErrors.push(`${file.name}: Invalid file type (only .sol, .rs, .go allowed)`)
        } else {
          newErrors.push(`${file.name}: ${error.message}`)
        }
      })
    })

    // Process accepted files with comprehensive validation
    const processedFiles: UploadedFile[] = []

    for (const file of acceptedFiles) {
      try {
        const content = await file.text()

        // Validate individual file
        const validationResult = validateFile(file, content, {
          maxSizeBytes: maxSize * 1024 * 1024,
          allowedExtensions: ['.sol', '.rs', '.go'],
          maxLines: 10000,
          requireContent: true,
          checkSyntax: true
        })

        if (!validationResult.isValid) {
          newErrors.push(...validationResult.errors.map(err => `${file.name}: ${err}`))
        }

        if (validationResult.warnings.length > 0) {
          newWarnings.push(...validationResult.warnings.map(warn => `${file.name}: ${warn}`))
        }

        // Only add file if validation passed
        if (validationResult.isValid) {
          const uploadedFile: UploadedFile = {
            file,
            content,
            name: file.name,
            size: file.size,
            lastModified: file.lastModified
          }
          processedFiles.push(uploadedFile)
        }
      } catch (error) {
        newErrors.push(`${file.name}: Failed to read file content - ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }

    // Check total file limit
    const totalFiles = uploadedFiles.length + processedFiles.length
    if (totalFiles > maxFiles) {
      newErrors.push(`Maximum ${maxFiles} files allowed. Currently have ${uploadedFiles.length}, trying to add ${processedFiles.length}`)
      return
    }

    // Validate all files together (check for duplicates, etc.)
    if (processedFiles.length > 0) {
      const allFiles = [...uploadedFiles, ...processedFiles]
      const batchValidation = validateFiles(allFiles)

      if (!batchValidation.isValid) {
        newErrors.push(...batchValidation.errors)
      }

      if (batchValidation.warnings.length > 0) {
        newWarnings.push(...batchValidation.warnings)
      }
    }

    setErrors(newErrors)
    setWarnings(newWarnings)

    if (processedFiles.length > 0 && newErrors.length === 0) {
      const updatedFiles = [...uploadedFiles, ...processedFiles]
      setUploadedFiles(updatedFiles)
      onFilesSelected(updatedFiles)
    }
  }, [uploadedFiles, maxFiles, maxSize, onFilesSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.sol', '.rs', '.go']
    },
    maxSize: maxSize * 1024 * 1024, // Convert MB to bytes
    multiple: true
  })

  const removeFile = (index: number) => {
    const updatedFiles = uploadedFiles.filter((_, i) => i !== index)
    setUploadedFiles(updatedFiles)
    onFilesSelected(updatedFiles)
  }

  const clearAll = () => {
    setUploadedFiles([])
    setErrors([])
    onFilesSelected([])
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-Quantlink-cyan bg-Quantlink-cyan/5' 
                : 'border-muted-foreground/25 hover:border-Quantlink-cyan/50'
              }
            `}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            
            {isDragActive ? (
              <p className="text-lg font-medium text-Quantlink-cyan">
                Drop your files here...
              </p>
            ) : (
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  Drag & drop your smart contract files here
                </p>
                <p className="text-sm text-muted-foreground">
                  or click to browse files
                </p>
                <div className="flex flex-wrap justify-center gap-2 mt-4">
                  <Badge variant="outline">.sol</Badge>
                  <Badge variant="outline">.rs</Badge>
                  <Badge variant="outline">.go</Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Max {maxFiles} files, {maxSize}MB each
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Messages */}
      {errors.length > 0 && (
        <Card className="border-destructive">
          <CardContent className="p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-sm font-medium text-destructive">Upload Errors:</p>
                <ul className="text-sm text-destructive space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Warning Messages */}
      {warnings.length > 0 && (
        <Alert variant="warning">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Warnings</AlertTitle>
          <AlertDescription>
            <ul className="list-disc list-inside space-y-1">
              {warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium">
                Uploaded Files ({uploadedFiles.length})
              </h3>
              <Button variant="ghost" size="sm" onClick={clearAll}>
                Clear All
              </Button>
            </div>
            
            <div className="space-y-2">
              {uploadedFiles.map((file, index) => {
                const fileInfo = getFileTypeInfo(file.name)
                return (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded ${fileInfo.bgColor}`}>
                        <File className={`h-4 w-4 ${fileInfo.color}`} />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)} • {fileInfo.language}
                        </p>
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
