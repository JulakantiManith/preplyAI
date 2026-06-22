import { Hero } from "@/features/landing/components/Hero";
import { Features } from "@/features/landing/components/Features";
import { HowItWorks } from "@/features/landing/components/HowItWorks";
import { Benefits } from "@/features/landing/components/Benefits";
import { Testimonials } from "@/features/landing/components/Testimonials";
import { Pricing } from "@/features/landing/components/Pricing";
import { FAQ } from "@/features/landing/components/FAQ";
import { Footer } from "@/shared/components/Footer";
import { useScrollAnimation } from "@/shared/hooks/useScrollAnimation";

export function LandingPage() {
  const containerRef = useScrollAnimation<HTMLElement>();

  return (
    <main ref={containerRef} className="min-h-screen bg-background">
      <Hero />
      <div className="animate-on-scroll">
        <Features />
      </div>
      <div className="animate-on-scroll">
        <HowItWorks />
      </div>
      <div className="animate-on-scroll">
        <Benefits />
      </div>
      <div className="animate-on-scroll">
        <Testimonials />
      </div>
      <div className="animate-on-scroll">
        <Pricing />
      </div>
      <div className="animate-on-scroll">
        <FAQ />
      </div>
      <Footer />
    </main>
  );
}
