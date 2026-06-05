# Topic → Mode Map

When a topic comes in, classify it first. The topic mode overrides the format dial in `voice-rules.md` for register choices.

## Modes

### Security mode
**Triggers:** topic mentions vulnerability, CVE, supply chain, RCE, exploit, breach, incident, attacker, malicious, compromise, threat model, attack surface.

**Voice:** Direct. Forensic. No hedge. State what happened, what was at risk, who's responsible. Cite CVEs or PoCs by ID.

**Structural defaults:**
- Timeline / chain-of-custody sections work well.
- "What an attacker can do" / "What you should check tonight" framing.
- For GitHub Pages → use **dark-cyberpunk theme**.

**Example posts:** `litellm-supply-chain-attack`, `mcp-supply-chain-rce`.

### Architecture / agents / inference mode
**Triggers:** agent, LLM, model, inference, context window, retrieval, RAG, MCP, tool-use, agentic, prompt, fine-tune, distillation, evals, benchmarks.

**Voice:** Sharp technical opinion. Production-grounded. Push back on hype. Cite specific benchmarks or product behaviors.

**Structural defaults:**
- Dichotomy framings (X vs Y, marketed vs measured).
- Concrete code/config snippets > abstract diagrams.
- "Where this breaks in production" section.

**Example posts:** `contextual-retrieval-tradeoffs`, `gemini-3-5-flash-agent-first`, `ai-coding-agent-stack`.

### Leadership / governance / data product mode
**Triggers:** leadership, hiring, mentoring, governance, policy, compliance, data product, team, organization, strategy, decision-making, judgment.

**Voice:** Measured, evidence-first. Less edge. Still opinionated. Cite Wharton, MIT, Harvard Business Review, McKinsey when relevant — but only with specific findings.

**Structural defaults:**
- Frameworks and decision trees acceptable here (sparingly).
- "Personal Heuristics" / "Structural Moves" sections.
- For GitHub Pages → warm-light theme.

**Example posts:** `data-product-manifesto`, `moral-surrender`.

### Cost / infra optimization mode
**Triggers:** cost, latency, throughput, batch, flex, inference, GPU, scaling, S3, storage, infra.

**Voice:** Pragmatic-flex (see voice-samples.md). Lead with a specific number + ship outcome.

**Example posts:** `gemini-flex-inference`, `amazon-s3-files`.

## When Topic Spans Multiple Modes

Default to the **dominant** mode (the one most concretely supported by the topic phrasing). If ambiguous, ask the user once.
