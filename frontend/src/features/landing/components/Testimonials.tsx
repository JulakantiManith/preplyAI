import { Quote } from "lucide-react";

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Software Engineer at Google",
    quote:
      "The AI feedback on my technical explanations was incredibly detailed. I went from fumbling through system design questions to confidently articulating my approach.",
    avatar: "SC",
  },
  {
    name: "Marcus Johnson",
    role: "Product Manager",
    quote:
      "I used to dread behavioral interviews. After two weeks of practice with this tool, I landed offers from three different companies.",
    avatar: "MJ",
  },
  {
    name: "Priya Patel",
    role: "MBA Graduate",
    quote:
      "The presentation coach helped me nail my capstone presentation. The real-time pacing feedback was a game-changer for my delivery.",
    avatar: "PP",
  },
];

export function Testimonials() {
  return (
    <section className="py-20 sm:py-28" aria-labelledby="testimonials-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="testimonials-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            What Our Users Say
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join thousands of professionals who improved their performance.
          </p>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.name}
              className="flex flex-col rounded-lg border bg-background p-6 shadow-sm"
            >
              <Quote className="mb-4 h-8 w-8 text-primary/40" />
              <p className="flex-1 text-sm leading-relaxed text-muted-foreground">
                &ldquo;{testimonial.quote}&rdquo;
              </p>
              <div className="mt-6 flex items-center gap-3">
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground"
                  aria-hidden="true"
                >
                  {testimonial.avatar}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {testimonial.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {testimonial.role}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
