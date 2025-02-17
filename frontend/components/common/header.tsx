import { Button } from "@/components/ui/button";
import { HomeIcon } from "lucide-react";
import Link from "next/link";

export function Header() {
  return (
    <header className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-sm border-b">
      <div className="max-w-screen-xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/#" className="flex items-center space-x-2">
          <HomeIcon className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">CompanyAI</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-8">
          <a
            href="/#features"
            className="text-sm font-medium hover:text-primary"
          >
            Features
          </a>
          <a href="/#process" className="text-sm font-medium hover:text-primary">
            Process
          </a>
          <a
            href="/#use-cases"
            className="text-sm font-medium hover:text-primary"
          >
            Use Cases
          </a>
        </nav>

        <div className="flex items-center space-x-4">
          <Button asChild>
            <Link href="/analyze">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
