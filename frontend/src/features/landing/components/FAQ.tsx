import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/shared/lib/utils";

const faqs = [
  {
    question: "How does the AI interview coach work?",
    answer:
      "Our platform uses advanced AI to generate realistic interview questions tailored to your role and industry. You respond via microphone, and the AI analyzes your content, delivery, and confidence to provide actionable feedback.",
  },
  {
    question: "Is the platform free to use?",
    answer:
      "Yes! You can get started with our free plan which includes 5 practice sessions per week. For unlimited sessions and advanced analytics, you can upgrade to the Pro plan.",
  },
  {
    question: "What types of interviews can I practice?",
    answer:
      "You can practice behavioral, technical, and situational interviews across various industries including tech, finance, consulting, healthcare, and more.",
  },
  {
    question: "Do I need any special equipment?",
    answer:
      "Just a working microphone and a modern web browser. The platform works on desktop, tablet, and mobile devices.",
  },
  {
    question: "How accurate is the AI feedback?",
    answer:
      "Our AI models are trained to evaluate communication skills similar to how professional coaches assess candidates. While no AI is perfect, users consistently report that the feedback helps them improve significantly.",
  },
  {
    question: "Can I track my progress over time?",
    answer:
      "Absolutely. The platform provides detailed analytics showing your improvement across sessions, including confidence scores, speech patterns, and content quality trends.",
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  function toggleFaq(index: number) {
    setOpenIndex(openIndex === index ? null : index);
  }

  return (
    <section className="py-20 sm:py-28" aria-labelledby="faq-heading">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2
            id="faq-heading"
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Got questions? We have answers.
          </p>
        </div>
        <div className="mt-12 divide-y border-t">
          {faqs.map((faq, index) => (
            <div key={index} className="border-b">
              <button
                onClick={() => toggleFaq(index)}
                className="flex w-full items-center justify-between py-5 text-left"
                aria-expanded={openIndex === index}
                aria-controls={`faq-answer-${index}`}
              >
                <span className="text-sm font-medium text-foreground sm:text-base">
                  {faq.question}
                </span>
                <ChevronDown
                  className={cn(
                    "h-5 w-5 flex-shrink-0 text-muted-foreground transition-transform duration-200",
                    openIndex === index && "rotate-180"
                  )}
                />
              </button>
              <div
                id={`faq-answer-${index}`}
                role="region"
                className={cn(
                  "overflow-hidden transition-all duration-200",
                  openIndex === index ? "max-h-96 pb-5" : "max-h-0"
                )}
              >
                <p className="text-sm text-muted-foreground">{faq.answer}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
