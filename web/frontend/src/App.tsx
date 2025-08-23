import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import Layout from '@/components/layout/Layout'
import HomePage from '@/pages/HomePage'
import AnalysisPage from '@/pages/AnalysisPage'
import ResultsPage from '@/pages/ResultsPage'
import NotFoundPage from '@/pages/NotFoundPage'

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalysisPage />} />
          <Route path="/results/:analysisId" element={<ResultsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
