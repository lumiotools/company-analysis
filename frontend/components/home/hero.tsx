import { Button } from "@/components/ui/button"
import { ArrowRightIcon } from 'lucide-react'
import Link from "next/link"

export function Hero() {
  return (
    <section className="relative h-[75vh] flex items-center overflow-hidden">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2072&q=80')`,
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: "linear-gradient(to right, rgba(0,33,68,0.9), rgba(0,33,68,0.7))",
        }}
      />

      <div className="max-w-screen-xl w-full mx-auto px-4 relative z-10">
        <div className="max-w-4xl">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            AI-Powered Company Intelligence
          </h1>
          <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-2xl">
            Transform your company documents into actionable insights with our
            advanced AI analysis platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              size="lg"
              className="bg-[#5479ff] hover:bg-opacity-90 text-white px-8 py-6 text-lg"
              asChild
            >
              <Link href="/analyze">
                Start Free Analysis
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
