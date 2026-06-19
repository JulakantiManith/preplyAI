import { BotMessageSquare, Activity, Target, LineChart } from "lucide-react";

const benefits = [
  {
    icon: BotMessageSquare,
    title: "AI-Powered Feedback",
    description:
      "Get instant, detailed feedback from advanced AI models that understand context, nuance, and industry expectations.",
  },
  {
    icon: Activity,
    title: "Real-Time Analysis",
    description:
      "Monitor your speech patterns, filler words, and pacing as you practice — no waiting for results.",
  },
  {
    icon: Target,
    title: "Personalized Practice",
    description:
      "Questions and scenarios adapt to your role, industry, and skill level for relevant preparation.",
  },
  {
    icon: LineChart,
    title: "Track Your Progress",
    description:
      "Visualize improvement over time with session history, trend charts, and confidence scores.",
  },
];

export function Benefits() {
  const appName = import.meta.env.VITE_APP_NAME || "AI Interview & Presentation Coach";

  return (
    <section className="bg-secondary/30 py-20 sm:py-28" aria-labelledby="benefits-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="benefits-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            Why Choose {appName}?
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Built to help you succeed in every conversation that matters.
          </p>
        </div>
        <div className="mt-16 grid gap-10 sm:grid-cols-2">
          {benefits.map((benefit) => (
            <div key={benefit.title} className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <benefit.icon className="h-6 w-6 text-primary" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  {benefit.title}
                </h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  {benefit.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
