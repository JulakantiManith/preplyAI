import { useEffect, useRef } from "react";

/**
 * Hook that observes elements with the `.animate-on-scroll` class
 * within the given container ref, adding `.animate-visible` when they
 * enter the viewport.
 *
 * Usage:
 *   const containerRef = useScrollAnimation();
 *   <div ref={containerRef}>...sections with .animate-on-scroll...</div>
 */
export function useScrollAnimation<T extends HTMLElement = HTMLElement>() {
  const containerRef = useRef<T>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const elements = container.querySelectorAll(".animate-on-scroll");

    if (elements.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
        rootMargin: "0px 0px -40px 0px",
      }
    );

    elements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return containerRef;
}
