import { HomeIcon } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-[#002144] py-8 !text-white">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <HomeIcon className="h-6 w-6 text-white" />
            <span className="font-bold text-xl">MDSV AI</span>
          </div>
          <nav className="flex space-x-4 mb-4 md:mb-0">
            <a href="#features" className="text-sm text-gray-300 hover:text-white">
              Features
            </a>
            <a href="#process" className="text-sm text-gray-300 hover:text-white">
              How It Works
            </a>
            <a href="#" className="text-sm text-gray-300 hover:text-white">
              About
            </a>
            <a href="#" className="text-sm text-gray-300 hover:text-white">
              Contact
            </a>
          </nav>
          <div className="text-sm text-gray-300">&copy; 2025 MDSV AI. All rights reserved.</div>
        </div>
      </div>
    </footer>
  )
}

