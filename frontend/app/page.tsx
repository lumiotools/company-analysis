import { Header } from "@/components/common/header";
import { Hero } from "@/components/home/hero";
import { Features } from "@/components/home/features";
import { ProcessFlow } from "@/components/home/process-flow";
import { Footer } from "@/components/common/footer";
import { CTASection } from "@/components/home/cta";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main>
        <Hero />
        <Features />
        <ProcessFlow />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}
