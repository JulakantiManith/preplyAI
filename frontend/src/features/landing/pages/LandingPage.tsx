import { Hero } from "@/features/landing/components/Hero";
import { Features } from "@/features/landing/components/Features";
import { HowItWorks } from "@/features/landing/components/HowItWorks";
import { Benefits } from "@/features/landing/components/Benefits";
import { Testimonials } from "@/features/landing/components/Testimonials";
import { Pricing } from "@/features/landing/components/Pricing";
import { FAQ } from "@/features/landing/components/FAQ";
import { Footer } from "@/shared/components/Footer";

export function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <Hero />
      <Features />
      <HowItWorks />
      <Benefits />
      <Testimonials />
      <Pricing />
      <FAQ />
      <Footer />
    </main>
  );
}
