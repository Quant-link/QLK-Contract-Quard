import { Link, useLocation } from 'react-router-dom'
import { Moon, Sun, Monitor } from 'lucide-react'
import { Button } from '../ui/button'
import { useTheme } from '../theme-provider'
import LogoBlack from '../../assets/logos/logo-black.svg'
import LogoWhite from '../../assets/logos/logo-white.svg'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu'
import NotificationCenter from '../notifications/NotificationCenter'

export default function Header() {
  const location = useLocation()
  const { theme, setTheme } = useTheme()

  const isActive = (path: string) => location.pathname === path

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
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
        {/* Logo and Brand */}
        <Link to="/" className="flex items-center hover:opacity-80 transition-opacity">
          <img
            src={getLogoSrc()}
            alt="ContractQuard"
            className="h-8 w-auto"
          />
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <Link
            to="/"
            className={`text-sm font-medium transition-all duration-200 relative py-2 ${
              isActive('/') ? 'nav-link-active' : 'text-muted-foreground hover:nav-link-hover'
            }`}
          >
            Home
            {isActive('/') && (
              <div className="absolute -bottom-1 left-0 right-0 h-0.5 rounded-full" style={{ backgroundColor: '#4dace1' }} />
            )}
          </Link>
          <Link
            to="/analyze"
            className={`text-sm font-medium transition-all duration-200 relative py-2 ${
              isActive('/analyze') ? 'nav-link-active' : 'text-muted-foreground hover:nav-link-hover'
            }`}
          >
            Analyze
            {isActive('/analyze') && (
              <div className="absolute -bottom-1 left-0 right-0 h-0.5 rounded-full" style={{ backgroundColor: '#4dace1' }} />
            )}
          </Link>
        </nav>

        {/* Theme Toggle and Actions */}
        <div className="flex items-center space-x-4">
          <NotificationCenter />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme("light")}>
                <Sun className="mr-2 h-4 w-4" />
                <span>Light</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")}>
                <Moon className="mr-2 h-4 w-4" />
                <span>Dark</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("system")}>
                <Monitor className="mr-2 h-4 w-4" />
                <span>System</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button asChild size="sm" className="btn-custom-primary font-medium px-6 hidden sm:inline-flex">
            <Link to="/analyze">Start Analysis</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
