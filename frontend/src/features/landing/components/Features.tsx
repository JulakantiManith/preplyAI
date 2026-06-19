import {
  Mic,
  Presentation,
  AudioLines,
  BotMessageSquare,
  TrendingUp,
  BarChart3,
} from "lucide-react";

const features = [
  {
    icon: Mic,
    title: "Interview Practice",
    description:
      "Practice behavioral, technical, and situational interview questions tailored to your role.",
  },
  {
    icon: Presentation,
    title: "Presentation Coach",
    description:
      "Rehearse presentations and get feedback on pacing, clarity, and engagement.",
  },
  {
    icon: AudioLines,
    title: "Speech Analysis",
    description:
      "Real-time analysis of filler words, pacing, and vocal patterns to sharpen delivery.",
  },
  {
    icon: BotMessageSquare,
    title: "AI Feedback",
    description:
      "Receive instant, actionable suggestions powered by advanced language models.",
  },
  {
    icon: TrendingUp,
    title: "Confidence Scoring",
    description:
      "Track your confidence level across sessions and see measurable improvement.",
  },
  {
    icon: BarChart3,
    title: "Progress Analytics",
    description:
      "Visualize trends and identify areas to focus on with detailed analytics dashboards.",
  },
];

export function Features() {
  return (
    <section className="bg-secondary/30 py-20 sm:py-28" aria-labelledby="features-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="features-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            Everything You Need to Succeed
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Comprehensive tools to prepare you for any interview or presentation.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-lg border bg-background p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 inline-flex rounded-md bg-primary/10 p-3">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
