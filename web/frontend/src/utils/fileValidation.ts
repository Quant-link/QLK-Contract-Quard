import { UploadedFile } from '../types'

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}

export interface FileValidationOptions {
  maxSizeBytes?: number
  allowedExtensions?: string[]
  maxLines?: number
  requireContent?: boolean
  checkSyntax?: boolean
}

const DEFAULT_OPTIONS: Required<FileValidationOptions> = {
  maxSizeBytes: 10 * 1024 * 1024, // 10MB
  allowedExtensions: ['.sol', '.rs', '.go'],
  maxLines: 10000,
  requireContent: true,
  checkSyntax: true
}

/**
 * Comprehensive file validation for smart contract uploads
 */
export function validateFile(
  file: File, 
  content: string, 
  options: FileValidationOptions = {}
): ValidationResult {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  const errors: string[] = []
  const warnings: string[] = []

  // File name validation
  if (!file.name || file.name.trim().length === 0) {
    errors.push('File name is required')
  }

  // File extension validation
  const extension = getFileExtension(file.name)
  if (!opts.allowedExtensions.includes(extension)) {
    errors.push(
      `Unsupported file type '${extension}'. Allowed types: ${opts.allowedExtensions.join(', ')}`
    )
  }

  // File size validation
  if (file.size > opts.maxSizeBytes) {
    errors.push(
      `File too large (${formatFileSize(file.size)}). Maximum size: ${formatFileSize(opts.maxSizeBytes)}`
    )
  }

  // Content validation
  if (opts.requireContent && (!content || content.trim().length === 0)) {
    errors.push('File cannot be empty')
  }

  // Line count validation
  const lineCount = content.split('\n').length
  if (lineCount > opts.maxLines) {
    errors.push(`Too many lines (${lineCount}). Maximum: ${opts.maxLines}`)
  }

  // Content size validation (separate from file size)
  const contentSizeBytes = new TextEncoder().encode(content).length
  if (contentSizeBytes > opts.maxSizeBytes) {
    errors.push(`Content too large. Maximum: ${formatFileSize(opts.maxSizeBytes)}`)
  }

  // Basic syntax validation
  if (opts.checkSyntax && content.trim().length > 0) {
    const syntaxResult = validateBasicSyntax(content, extension)
    errors.push(...syntaxResult.errors)
    warnings.push(...syntaxResult.warnings)
  }

  // Security checks
  const securityResult = performSecurityChecks(content, file.name)
  errors.push(...securityResult.errors)
  warnings.push(...securityResult.warnings)

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
}

/**
 * Validate multiple files for batch upload
 */
export function validateFiles(
  files: UploadedFile[], 
  options: FileValidationOptions = {}
): ValidationResult {
  const allErrors: string[] = []
  const allWarnings: string[] = []

  // Check for duplicate filenames
  const filenames = files.map(f => f.name.toLowerCase())
  const duplicates = filenames.filter((name, index) => filenames.indexOf(name) !== index)
  if (duplicates.length > 0) {
    allErrors.push(`Duplicate filenames detected: ${[...new Set(duplicates)].join(', ')}`)
  }

  // Validate each file
  files.forEach((uploadedFile, index) => {
    const result = validateFile(uploadedFile.file, uploadedFile.content, options)
    
    // Prefix errors with file identifier
    result.errors.forEach(error => {
      allErrors.push(`File ${index + 1} (${uploadedFile.name}): ${error}`)
    })
    
    result.warnings.forEach(warning => {
      allWarnings.push(`File ${index + 1} (${uploadedFile.name}): ${warning}`)
    })
  })

  return {
    isValid: allErrors.length === 0,
    errors: allErrors,
    warnings: allWarnings
  }
}

/**
 * Basic syntax validation for different file types
 */
function validateBasicSyntax(content: string, extension: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  switch (extension) {
    case '.sol':
      return validateSoliditySyntax(content)
    case '.rs':
      return validateRustSyntax(content)
    case '.go':
      return validateGoSyntax(content)
    default:
      return { isValid: true, errors, warnings }
  }
}

/**
 * Basic Solidity syntax validation
 */
function validateSoliditySyntax(content: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  // Check for pragma directive
  if (!content.includes('pragma solidity')) {
    warnings.push('Missing pragma solidity directive')
  }

  // Check for basic contract structure
  if (!content.includes('contract ') && !content.includes('library ') && !content.includes('interface ')) {
    errors.push('No contract, library, or interface declaration found')
  }

  // Check for balanced braces
  const openBraces = (content.match(/{/g) || []).length
  const closeBraces = (content.match(/}/g) || []).length
  if (openBraces !== closeBraces) {
    errors.push('Unbalanced braces detected')
  }

  // Check for balanced parentheses
  const openParens = (content.match(/\(/g) || []).length
  const closeParens = (content.match(/\)/g) || []).length
  if (openParens !== closeParens) {
    errors.push('Unbalanced parentheses detected')
  }

  return { isValid: errors.length === 0, errors, warnings }
}

/**
 * Basic Rust syntax validation
 */
function validateRustSyntax(content: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  // Check for basic Rust structure
  if (!content.includes('fn ') && !content.includes('struct ') && !content.includes('impl ')) {
    warnings.push('No function, struct, or impl block found')
  }

  // Check for balanced braces
  const openBraces = (content.match(/{/g) || []).length
  const closeBraces = (content.match(/}/g) || []).length
  if (openBraces !== closeBraces) {
    errors.push('Unbalanced braces detected')
  }

  return { isValid: errors.length === 0, errors, warnings }
}

/**
 * Basic Go syntax validation
 */
function validateGoSyntax(content: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  // Check for package declaration
  if (!content.includes('package ')) {
    errors.push('Missing package declaration')
  }

  // Check for balanced braces
  const openBraces = (content.match(/{/g) || []).length
  const closeBraces = (content.match(/}/g) || []).length
  if (openBraces !== closeBraces) {
    errors.push('Unbalanced braces detected')
  }

  return { isValid: errors.length === 0, errors, warnings }
}

/**
 * Security checks for uploaded content
 */
function performSecurityChecks(content: string, filename: string): ValidationResult {
  const errors: string[] = []
  const warnings: string[] = []

  // Check for potentially malicious patterns
  const suspiciousPatterns = [
    /eval\s*\(/i,
    /exec\s*\(/i,
    /<script/i,
    /javascript:/i,
    /data:text\/html/i
  ]

  suspiciousPatterns.forEach(pattern => {
    if (pattern.test(content)) {
      warnings.push('Potentially suspicious content detected')
    }
  })

  // Check for excessively long lines (potential obfuscation)
  const lines = content.split('\n')
  const longLines = lines.filter(line => line.length > 500)
  if (longLines.length > 0) {
    warnings.push(`${longLines.length} very long lines detected (>500 chars)`)
  }

  // Check for unusual file name patterns
  if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    errors.push('Invalid characters in filename')
  }

  return { isValid: errors.length === 0, errors, warnings }
}

/**
 * Get file extension from filename
 */
function getFileExtension(filename: string): string {
  const lastDot = filename.lastIndexOf('.')
  return lastDot === -1 ? '' : filename.substring(lastDot).toLowerCase()
}

/**
 * Format file size in human readable format
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Check if file type is supported
 */
export function isSupportedFileType(filename: string): boolean {
  const extension = getFileExtension(filename)
  return DEFAULT_OPTIONS.allowedExtensions.includes(extension)
}

/**
 * Get file type information
 */
export function getFileTypeInfo(filename: string) {
  const extension = getFileExtension(filename)
  
  switch (extension) {
    case '.sol':
      return {
        language: 'Solidity',
        icon: '⟠',
        color: 'text-purple-600',
        bgColor: 'bg-purple-50',
        description: 'Ethereum Smart Contract'
      }
    case '.rs':
      return {
        language: 'Rust',
        icon: '🦀',
        color: 'text-orange-600',
        bgColor: 'bg-orange-50',
        description: 'Substrate/ink! Contract'
      }
    case '.go':
      return {
        language: 'Go',
        icon: '🐹',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        description: 'Cosmos SDK Module'
      }
    default:
      return {
        language: 'Unknown',
        icon: '📄',
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        description: 'Unknown File Type'
      }
  }
}
