/* eslint-disable @typescript-eslint/no-unused-vars */
import { Header } from "@/components/common/header";
import { Hero } from "@/components/home/hero";
import { Features } from "@/components/home/features";
import { ProcessFlow } from "@/components/home/process-flow";
import { Footer } from "@/components/common/footer";
import { CTASection } from "@/components/home/cta";

export default function LandingPage() {
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Header />
      <main className="flex-grow overflow-hidden">
        <Hero />
      </main>
      <Footer />
    </div>
  );
}
