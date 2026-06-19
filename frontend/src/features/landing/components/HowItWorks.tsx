import { Settings2, Mic, MessageSquareText } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: Settings2,
    title: "Choose Your Mode",
    description:
      "Select interview practice or presentation coaching. Pick your industry, role, and difficulty level.",
  },
  {
    number: 2,
    icon: Mic,
    title: "Practice",
    description:
      "Answer AI-generated questions or deliver your presentation while the system records and analyzes in real time.",
  },
  {
    number: 3,
    icon: MessageSquareText,
    title: "Get Feedback",
    description:
      "Review detailed AI feedback on content, delivery, confidence, and areas for improvement.",
  },
];

export function HowItWorks() {
  return (
    <section className="py-20 sm:py-28" aria-labelledby="how-it-works-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="how-it-works-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Three simple steps to better performance.
          </p>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.number} className="flex flex-col items-center text-center">
              <div className="relative mb-6">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <step.icon className="h-7 w-7" />
                </div>
                <span className="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-xs font-bold text-secondary-foreground">
                  {step.number}
                </span>
              </div>
              <h3 className="text-xl font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="mt-3 max-w-xs text-sm text-muted-foreground">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
