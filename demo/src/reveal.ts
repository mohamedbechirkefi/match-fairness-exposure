// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Reveal a chart once, the first time it scrolls into view. Without
// IntersectionObserver the chart is simply shown.
import { useEffect, useRef, useState } from "react";

export function useRevealOnce<T extends Element>() {
  const ref = useRef<T | null>(null);
  const [state, setState] = useState<"idle" | "armed" | "in">("idle");
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    setState("armed");
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setState("in");
          io.disconnect();
        }
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return [ref, state === "idle" ? "" : state === "armed" ? " reveal-armed" : " reveal-armed is-in"] as const;
}
