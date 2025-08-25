import { Github, Twitter, Globe } from 'lucide-react'
import { useTheme } from '../theme-provider'
import LogoBlack from '../../assets/logos/logo-black.svg'
import LogoWhite from '../../assets/logos/logo-white.svg'

export default function Footer() {
  const { theme } = useTheme()

  // Determine which logo to use based on theme
  const getLogoSrc = () => {
    if (theme === 'dark') {
      return LogoWhite
    } else if (theme === 'light') {
      return LogoBlack
    } else {
      // System theme - check actual applied theme
      const isDark = document.documentElement.classList.contains('dark')
      return isDark ? LogoWhite : LogoBlack
    }
  }

  return (
    <footer className="border-t bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center">
              <img
                src={getLogoSrc()}
                alt="ContractQuard"
                className="h-6 w-auto"
              />
            </div>
            <p className="text-sm text-muted-foreground">
              AI-augmented smart contract security analysis tool by QuantLink.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="/analyze" className="hover:text-primary transition-colors">
                  Security Analysis
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  API Reference
                </a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Company</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  About QuantLink
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Privacy Policy
                </a>
              </li>
            </ul>
          </div>

          {/* Connect */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Connect</h3>
            <div className="flex space-x-4">
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Github className="h-5 w-5" />
                <span className="sr-only">GitHub</span>
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Twitter className="h-5 w-5" />
                <span className="sr-only">Twitter</span>
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                <Globe className="h-5 w-5" />
                <span className="sr-only">Website</span>
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
          <p>&copy; 2024 QuantLink. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
