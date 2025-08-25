import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { 
  AnalysisConfig, 
  AnalysisSettingsState, 
  AnalysisPreset,
  SecurityLevel,
  VulnerabilityCategory,
  CustomRule
} from '../types'

// Default vulnerability categories
const defaultVulnerabilityCategories: VulnerabilityCategory[] = [
  {
    id: 'reentrancy',
    name: 'Reentrancy Vulnerabilities',
    enabled: true,
    severity_threshold: 'CRITICAL',
    description: 'Detects recursive call patterns that can drain contract funds',
    detectors: ['reentrancy-eth', 'reentrancy-no-eth', 'reentrancy-unlimited-gas']
  },
  {
    id: 'access-control',
    name: 'Access Control Issues',
    enabled: true,
    severity_threshold: 'HIGH',
    description: 'Validates proper permission and authorization mechanisms',
    detectors: ['unprotected-upgrade', 'missing-zero-check', 'tx-origin']
  },
  {
    id: 'arithmetic',
    name: 'Arithmetic Issues',
    enabled: true,
    severity_threshold: 'HIGH',
    description: 'Identifies integer overflow/underflow and arithmetic errors',
    detectors: ['divide-before-multiply', 'incorrect-shift', 'weak-prng']
  },
  {
    id: 'gas-optimization',
    name: 'Gas Optimization',
    enabled: true,
    severity_threshold: 'MEDIUM',
    description: 'Analyzes gas consumption patterns and optimization opportunities',
    detectors: ['costly-loop', 'dead-code', 'unused-return']
  },
  {
    id: 'code-quality',
    name: 'Code Quality',
    enabled: true,
    severity_threshold: 'LOW',
    description: 'Reviews coding standards, best practices, and maintainability',
    detectors: ['naming-convention', 'similar-names', 'too-many-digits']
  }
]

// Default analysis configuration
const defaultConfig: AnalysisConfig = {
  security_level: 'standard',
  vulnerability_categories: defaultVulnerabilityCategories,
  custom_rules: [],
  
  language_settings: {
    solidity: {
      compiler_version: '0.8.19',
      evm_version: 'london',
      optimization_enabled: true,
      optimization_runs: 200,
      enable_experimental_features: false,
      custom_imports: []
    },
    rust: {
      edition: '2021',
      target: 'wasm32-unknown-unknown',
      features: [],
      no_default_features: false,
      enable_clippy: true,
      clippy_config: {}
    },
    go: {
      version: '1.21',
      build_tags: [],
      cgo_enabled: false,
      race_detection: true,
      enable_vet: true,
      vet_config: {}
    }
  },
  
  analysis_scope: {
    type: 'full',
    include_dependencies: true,
    include_test_files: false,
    include_examples: false,
    max_file_size_mb: 10,
    max_lines_per_file: 10000,
    exclude_patterns: ['node_modules/**', 'target/**', 'vendor/**']
  },
  
  report_config: {
    format: ['json', 'html'],
    detail_level: 'standard',
    include_code_snippets: true,
    include_recommendations: true,
    include_references: true,
    include_metrics: true,
    group_by_severity: true,
    group_by_category: false
  },
  
  notification_config: {
    email_notifications: {
      enabled: false,
      recipients: [],
      on_completion: true,
      on_critical_findings: true,
      on_errors: true,
      include_summary: true
    },
    webhook_notifications: {
      enabled: false,
      url: '',
      events: ['analysis_completed'],
      retry_attempts: 3,
      timeout_seconds: 30
    },
    slack_notifications: {
      enabled: false,
      webhook_url: '',
      channel: '#security',
      username: 'ContractQuard',
      on_completion: true,
      on_critical_findings: true
    },
    real_time_updates: true
  }
}

// Default presets
const defaultPresets: AnalysisPreset[] = [
  {
    id: 'quick-scan',
    name: 'Quick Scan',
    description: 'Fast security scan focusing on critical vulnerabilities',
    is_default: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    config: {
      ...defaultConfig,
      security_level: 'basic',
      analysis_scope: {
        ...defaultConfig.analysis_scope,
        type: 'quick',
        include_dependencies: false
      },
      vulnerability_categories: defaultVulnerabilityCategories.filter(cat => 
        ['reentrancy', 'access-control'].includes(cat.id)
      )
    }
  },
  {
    id: 'comprehensive',
    name: 'Comprehensive Analysis',
    description: 'Deep security analysis with all vulnerability categories',
    is_default: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    config: {
      ...defaultConfig,
      security_level: 'enterprise',
      analysis_scope: {
        ...defaultConfig.analysis_scope,
        include_test_files: true,
        include_examples: true
      },
      report_config: {
        ...defaultConfig.report_config,
        detail_level: 'comprehensive',
        format: ['json', 'html', 'pdf']
      }
    }
  }
]

interface AnalysisSettingsStore extends AnalysisSettingsState {
  // Actions
  updateConfig: (config: Partial<AnalysisConfig>) => void
  updateSecurityLevel: (level: SecurityLevel) => void
  updateVulnerabilityCategory: (categoryId: string, updates: Partial<VulnerabilityCategory>) => void
  addCustomRule: (rule: CustomRule) => void
  removeCustomRule: (ruleId: string) => void
  updateCustomRule: (ruleId: string, updates: Partial<CustomRule>) => void
  
  // Presets
  loadPreset: (presetId: string) => void
  saveAsPreset: (name: string, description: string) => void
  deletePreset: (presetId: string) => void
  
  // Validation
  validateConfig: () => boolean
  clearValidationErrors: () => void
  
  // Persistence
  saveConfig: () => Promise<void>
  loadConfig: () => Promise<void>
  resetToDefaults: () => void
}

export const useAnalysisSettingsStore = create<AnalysisSettingsStore>()(
  persist(
    (set, get) => ({
      // Initial state
      config: defaultConfig,
      presets: defaultPresets,
      current_preset: null,
      is_loading: false,
      is_saving: false,
      last_saved: null,
      validation_errors: {},

      // Actions
      updateConfig: (updates) => {
        set((state) => ({
          config: { ...state.config, ...updates },
          current_preset: null // Clear preset when manually editing
        }))
      },

      updateSecurityLevel: (level) => {
        set((state) => ({
          config: { ...state.config, security_level: level },
          current_preset: null
        }))
      },

      updateVulnerabilityCategory: (categoryId, updates) => {
        set((state) => ({
          config: {
            ...state.config,
            vulnerability_categories: state.config.vulnerability_categories.map(cat =>
              cat.id === categoryId ? { ...cat, ...updates } : cat
            )
          },
          current_preset: null
        }))
      },

      addCustomRule: (rule) => {
        set((state) => ({
          config: {
            ...state.config,
            custom_rules: [...state.config.custom_rules, rule]
          },
          current_preset: null
        }))
      },

      removeCustomRule: (ruleId) => {
        set((state) => ({
          config: {
            ...state.config,
            custom_rules: state.config.custom_rules.filter(rule => rule.id !== ruleId)
          },
          current_preset: null
        }))
      },

      updateCustomRule: (ruleId, updates) => {
        set((state) => ({
          config: {
            ...state.config,
            custom_rules: state.config.custom_rules.map(rule =>
              rule.id === ruleId ? { ...rule, ...updates } : rule
            )
          },
          current_preset: null
        }))
      },

      loadPreset: (presetId) => {
        const preset = get().presets.find(p => p.id === presetId)
        if (preset) {
          set({
            config: preset.config,
            current_preset: presetId
          })
        }
      },

      saveAsPreset: (name, description) => {
        const newPreset: AnalysisPreset = {
          id: `preset-${Date.now()}`,
          name,
          description,
          config: get().config,
          is_default: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        set((state) => ({
          presets: [...state.presets, newPreset],
          current_preset: newPreset.id
        }))
      },

      deletePreset: (presetId) => {
        set((state) => ({
          presets: state.presets.filter(p => p.id !== presetId),
          current_preset: state.current_preset === presetId ? null : state.current_preset
        }))
      },

      validateConfig: () => {
        const errors: Record<string, string[]> = {}
        const config = get().config
        
        // Validate security level
        if (!['basic', 'standard', 'advanced', 'enterprise'].includes(config.security_level)) {
          errors.security_level = ['Invalid security level']
        }
        
        // Validate vulnerability categories
        if (config.vulnerability_categories.length === 0) {
          errors.vulnerability_categories = ['At least one vulnerability category must be enabled']
        }
        
        // Validate custom rules
        config.custom_rules.forEach((rule, index) => {
          if (!rule.name.trim()) {
            errors[`custom_rule_${index}_name`] = ['Rule name is required']
          }
          if (!rule.pattern.trim()) {
            errors[`custom_rule_${index}_pattern`] = ['Rule pattern is required']
          }
        })
        
        // Validate language settings
        if (config.language_settings.solidity.optimization_runs < 1) {
          errors.solidity_optimization_runs = ['Optimization runs must be at least 1']
        }
        
        // Validate analysis scope
        if (config.analysis_scope.max_file_size_mb < 1) {
          errors.max_file_size = ['Maximum file size must be at least 1MB']
        }
        
        set({ validation_errors: errors })
        return Object.keys(errors).length === 0
      },

      clearValidationErrors: () => {
        set({ validation_errors: {} })
      },

      saveConfig: async () => {
        set({ is_saving: true })
        try {
          // Here you would make an API call to save the configuration
          // await apiService.saveAnalysisConfig(get().config)
          
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          set({ 
            is_saving: false,
            last_saved: new Date().toISOString()
          })
        } catch (error) {
          set({ is_saving: false })
          throw error
        }
      },

      loadConfig: async () => {
        set({ is_loading: true })
        try {
          // Here you would make an API call to load the configuration
          // const config = await apiService.getAnalysisConfig()
          
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 500))
          
          set({ 
            is_loading: false
          })
        } catch (error) {
          set({ is_loading: false })
          throw error
        }
      },

      resetToDefaults: () => {
        set({
          config: defaultConfig,
          current_preset: null,
          validation_errors: {}
        })
      }
    }),
    {
      name: 'analysis-settings-store',
      partialize: (state) => ({
        config: state.config,
        presets: state.presets,
        current_preset: state.current_preset
      })
    }
  )
)
