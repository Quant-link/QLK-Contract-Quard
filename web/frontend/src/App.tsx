import { Routes, Route, useLocation } from 'react-router-dom'
import { Toaster } from './components/ui/toaster'
import { ThemeProvider } from './components/theme-provider'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import ResultsPage from './pages/ResultsPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  const location = useLocation()

  // Simple routing based on pathname
  const renderPage = () => {
    switch (location.pathname) {
      case '/':
        return <HomePage />
      case '/analyze':
        return <AnalysisPage />
      default:
        if (location.pathname.startsWith('/results/')) {
          return <ResultsPage />
        }
        return <NotFoundPage />
    }
  }

  return (
    <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
      <Layout>
        {renderPage()}
      </Layout>
      <Toaster />
    </ThemeProvider>
  )
}

export default App
