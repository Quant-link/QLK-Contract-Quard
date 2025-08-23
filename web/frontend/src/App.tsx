import { Routes, Route, createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Toaster } from './components/ui/toaster'
import { ThemeProvider } from './components/theme-provider'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import AnalysisPage from './pages/AnalysisPage'
import ResultsPage from './pages/ResultsPage'
import NotFoundPage from './pages/NotFoundPage'

// Create router with future flags
const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
        <Layout>
          <HomePage />
        </Layout>
        <Toaster />
      </ThemeProvider>
    ),
  },
  {
    path: "/analyze",
    element: (
      <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
        <Layout>
          <AnalysisPage />
        </Layout>
        <Toaster />
      </ThemeProvider>
    ),
  },
  {
    path: "/results/:analysisId",
    element: (
      <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
        <Layout>
          <ResultsPage />
        </Layout>
        <Toaster />
      </ThemeProvider>
    ),
  },
  {
    path: "*",
    element: (
      <ThemeProvider defaultTheme="light" storageKey="contractquard-ui-theme">
        <Layout>
          <NotFoundPage />
        </Layout>
        <Toaster />
      </ThemeProvider>
    ),
  },
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
})

function App() {
  return <RouterProvider router={router} />
}

export default App
