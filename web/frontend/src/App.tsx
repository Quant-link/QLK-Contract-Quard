import { Routes, Route, Navigate, useParams } from 'react-router-dom'
import { Toaster } from './components/ui/toaster'
import { ThemeProvider } from './components/theme-provider'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import AnalysisResultsPage from './pages/AnalysisResultsPage'
import NotFoundPage from './pages/NotFoundPage'

// Redirect component for old results route
function ResultsRedirect() {
  const { analysisId } = useParams<{ analysisId: string }>()
  return <Navigate to={`/analysis/${analysisId}`} replace />
}

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalysisPage />} />
          {/* Redirect old results route to new detailed analysis route */}
          <Route path="/results/:analysisId" element={<ResultsRedirect />} />
          <Route path="/analysis/:analysisId" element={<AnalysisResultsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
