import { Link } from "react-router-dom";
import { Check } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

const plans = [
  {
    name: "Free",
    description: "Get started with core features",
    price: "$0",
    period: "forever",
    features: [
      "5 practice sessions per week",
      "AI-generated questions",
      "Basic speech analysis",
      "Session history",
      "Progress tracking",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Pro",
    description: "Unlimited practice and advanced insights",
    price: "$12",
    period: "per month",
    features: [
      "Unlimited practice sessions",
      "Advanced AI feedback",
      "Detailed speech analytics",
      "Confidence scoring",
      "Priority support",
      "Custom question sets",
    ],
    cta: "Start Pro Trial",
    highlighted: true,
  },
];

export function Pricing() {
  return (
    <section className="bg-secondary/30 py-20 sm:py-28" aria-labelledby="pricing-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="pricing-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            Simple, Transparent Pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start free and upgrade when you need more.
          </p>
        </div>
        <div className="mx-auto mt-16 grid max-w-4xl gap-8 md:grid-cols-2">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`flex flex-col rounded-lg border p-8 ${
                plan.highlighted
                  ? "border-primary shadow-lg ring-1 ring-primary"
                  : "bg-background shadow-sm"
              }`}
            >
              <h3 className="text-xl font-semibold text-foreground">
                {plan.name}
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {plan.description}
              </p>
              <div className="mt-6">
                <span className="text-4xl font-bold text-foreground">
                  {plan.price}
                </span>
                <span className="ml-1 text-sm text-muted-foreground">
                  /{plan.period}
                </span>
              </div>
              <ul className="mt-8 flex-1 space-y-3" role="list">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
                    <span className="text-sm text-muted-foreground">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
              <Button
                className="mt-8"
                variant={plan.highlighted ? "default" : "outline"}
                size="lg"
                asChild
              >
                <Link to="/register">{plan.cta}</Link>
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
