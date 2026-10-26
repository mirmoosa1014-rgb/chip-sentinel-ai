# Explanation

Imagine a calculator made of small blocks. One block may be broken. Each input is a question we ask the calculator. The response rules out blocks whose predicted behavior disagrees. A useful question separates the remaining possibilities into different answers. Some broken blocks always behave the same way, so no question in our pool can tell them apart. The learned model sorts hypotheses using past synthetic examples; it does not make impossible distinctions possible.

## Ten reviewer questions

1. What is measured? Exact output values under selected vectors, not internal hidden fault identity.
2. What is a fault? A single 4-bit bus forced low/high, inverted, or open-to-zero.
3. Why an independent oracle? The tests use arithmetic addition, while the engine uses a carry loop.
4. Why hold out topologies? Repeated vectors from one circuit would give overly optimistic generalization.
5. Does ML choose tests? No. Entropy over the public fault table selects tests.
6. Why can accuracy remain low? Equivalent hypotheses and insufficient evidence prevent unique diagnosis.
7. What does score mean? A learned ordering; it is not a calibrated likelihood.
8. What does 9 tests mean? The eight-test budget did not reach three candidates.
9. Does this diagnose silicon? No, it is synthetic, idealized, noiseless bus-level logic.
10. What comes next? Per-bit faults, noisy observations, richer topologies, and learned test selection assessed against the exact heuristic.
