import { Button } from "@/components/ui/button"
import Link from "next/link"

export function CTASection() {
  return (
    <section className="py-40" id="use-cases">
      <div className="container mx-auto px-4 text-center">
      <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Business Intelligence?</h2>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Start leveraging AI-powered insights to make data-driven decisions and stay ahead of the competition.
        </p>
        <Link href="/analyze">
          <Button size="lg" variant="secondary">
            Get Started Now
          </Button>
        </Link>
      </div>
    </section>
  )
}
