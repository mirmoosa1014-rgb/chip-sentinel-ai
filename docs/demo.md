# 90-second demo

0–15 seconds: explain that this is a synthetic digital circuit, with one hidden bus fault and no physical-chip claims. Open the local app on family 6, seed 31, zero evidence.

15–35: drag the circuit volume; explain that green nodes still fit the evidence. Run the next test and compare binary expected and observed outputs.

35–55: increase to four tests. Compare remaining hypotheses and the fixed-policy plot. Point out that equal budgets do not mean identical selected vectors; both policies face the same fault.

55–75: inspect learned ranks and reveal the injected fault. Explain why open versus stuck-zero cannot be distinguished under this simulator. The learned score is a ranking score, not a probability.

75–90: export the transcript. Show measured evaluation and the unfavorable counterexample. State that the heuristic chooses tests and ML only ranks candidates; the result does not validate real chips.
