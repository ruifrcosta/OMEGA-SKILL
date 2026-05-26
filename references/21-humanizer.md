# Humanizer — Anti-AI Writing Reference

Sourced from: blader/humanizer (based on Wikipedia's "Signs of AI writing" guide).
Read before writing ANY documentation, copy, ADR body text, runbooks, or user-facing content.

---

## Core Rule

After writing any text, ask internally: **"What makes this obviously AI-generated?"**
Then fix it. Then ask again. Ship only after the answer is "nothing obvious."

---

## THE 29 PATTERNS TO ELIMINATE

### Content Patterns

**1. Significance Inflation**
Words: `stands as`, `serves as`, `testament`, `vital/pivotal/crucial role`, `underscores`, `evolving landscape`, `reflects broader`
Fix: State the plain fact. Remove the "this matters because..." wrapper.
- ❌ "marking a pivotal moment in the evolution of..."
- ✅ "established in 1989 to collect regional statistics"

**2. Notability Claims**
Words: `independent coverage`, `active social media presence`, `written by a leading expert`
Fix: Cite the specific source and what it said, not the fact that sources exist.

**3. Superficial -ing Analyses**
Words: `highlighting`, `underscoring`, `symbolizing`, `contributing to`, `fostering`, `showcasing`
Fix: Remove the -ing phrase entirely. The sentence works without it.
- ❌ "...showcasing how AI can contribute to better outcomes, highlighting the interplay..."
- ✅ Remove both phrases.

**4. Promotional Language**
Words: `boasts`, `vibrant`, `rich`, `nestled`, `in the heart of`, `groundbreaking`, `breathtaking`, `stunning`
Fix: Neutral descriptive language only.

**5. Vague Attributions**
Words: `industry reports`, `observers have cited`, `experts argue`, `some critics`
Fix: Name the specific person/source + what they said + when.

**6. "Challenges and Future Prospects" sections**
Fix: Dissolve these into factual statements. "Traffic increased after 2015" not "faces challenges typical of urban areas."

---

### Language Patterns

**7. AI Vocabulary Words** (statistically overrepresented post-2023)
Banned: `actually`, `additionally`, `align with`, `crucial`, `delve`, `emphasizing`, `enhance`, `fostering`, `garner`, `highlight (verb)`, `interplay`, `intricate`, `landscape (abstract)`, `pivotal`, `tapestry (abstract)`, `testament`, `underscore (verb)`, `vibrant`
Fix: Replace with plain equivalents or restructure.

**8. Copula Avoidance**
Words: `serves as`, `stands as`, `marks`, `represents`, `boasts`, `features`
Fix: Use `is`, `are`, `has`, `have`.
- ❌ "Gallery 825 serves as LAAA's exhibition space"
- ✅ "Gallery 825 is LAAA's exhibition space"

**9. Negative Parallelisms and Tailing Negations**
Words: `not only...but`, `it's not just about...it's`, `no guessing` (tacked on)
Fix: Write one clean declarative sentence.

**10. Rule of Three Overuse**
Fix: Say what's true. Don't pad to three.
- ❌ "innovation, inspiration, and industry insights"
- ✅ "talks and panels"

**11. Elegant Variation (Synonym Cycling)**
Fix: Repeat the noun. Don't cycle synonyms.
- ❌ "protagonist... main character... central figure... hero"
- ✅ "protagonist" throughout

**12. False Ranges**
Words: `from X to Y` when X and Y aren't on a meaningful scale
Fix: List the specific things.

**13. Passive Voice and Subjectless Fragments**
- ❌ "No configuration file needed. Results are preserved automatically."
- ✅ "You don't need a config file. The system preserves results."

---

### Style Patterns

**14. Em Dash Overuse** — EM DASH IS BANNED. (Aligns with Taste Engine §9.G)
Fix: Period, comma, or parentheses.
- ❌ "not by the people themselves—even in official documents"
- ✅ "not by the people themselves, even in official documents"

**15. Overuse of Boldface**
Fix: Bold only genuinely critical terms, not every technical phrase.

**16. Inline-Header Vertical Lists**
Fix: Merge bolded headers + content into prose.

**17. Title Case in Headings**
Fix: Sentence case only.
- ❌ "Strategic Negotiations And Global Partnerships"
- ✅ "Strategic negotiations and global partnerships"

**18. Emojis** (unless brief is explicitly playful/social)
Fix: Remove. Use icon library glyphs in UI.

**19. Curly Quotation Marks**
Fix: Use straight quotes `"..."` in code/markdown.

---

### Communication Patterns

**20. Collaborative Artifacts**
Words: `I hope this helps`, `Of course!`, `Certainly!`, `Would you like...`, `let me know`
Fix: Remove entirely. State the content directly.

**21. Knowledge-Cutoff Disclaimers**
Words: `as of my last update`, `while specific details are limited`
Fix: State what is known. If unknown, verify or omit.

**22. Sycophantic Tone**
Words: `great question!`, `you're absolutely right`, `that's an excellent point`
Fix: Remove. Start with the substance.

---

### Filler and Hedging

**23. Filler Phrases**
- "In order to" → "To"
- "Due to the fact that" → "Because"
- "At this point in time" → "Now"
- "Has the ability to" → "Can"
- "It is important to note that" → remove

**24. Excessive Hedging**
- ❌ "could potentially possibly be argued that... might have some effect"
- ✅ "may affect"

**25. Generic Positive Conclusions**
Words: `the future looks bright`, `exciting times lie ahead`, `journey toward excellence`
Fix: End with a specific concrete fact.

**26. Hyphenated Word Pair Overuse**
Avoid hyphenating these consistently: `third-party`, `cross-functional`, `client-facing`, `data-driven`, `decision-making`, `well-known`, `high-quality`, `real-time`, `long-term`

**27. Persuasive Authority Tropes**
Words: `the real question is`, `at its core`, `in reality`, `what really matters`, `fundamentally`
Fix: Remove the trope. State the point directly.

**28. Signposting and Announcements**
Words: `let's dive in`, `let's explore`, `here's what you need to know`, `without further ado`
Fix: Just do the thing. Don't announce it.

**29. Fragmented Headers**
Fix: Remove the one-line paragraph that restates the header before content begins.
- ❌ "## Performance\n\nSpeed matters.\n\nWhen users hit a slow page..."
- ✅ "## Performance\n\nWhen users hit a slow page..."

---

## VOICE AND SOUL

Clean-of-AI-patterns is only half. Sterile voiceless prose is also obvious.

**Signs of soulless writing:**
- Every sentence the same length
- No opinions, only neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person when appropriate
- No humor, no edge, no personality

**How to add voice:**
- Have opinions. React to facts, don't just report them.
- Vary rhythm. Short punchy sentences. Then ones that take their time.
- Acknowledge complexity. "Impressive but unsettling" beats "impressive."
- Use "I" when it fits.
- Be specific about feelings. Not "concerning" but "there's something unsettling about..."

---

## APPLICATION IN OMEGA

Apply this reference whenever writing:
- ADR body text (`{vault}/14-ADRs/`)
- Runbook prose (`{vault}/15-Runbooks/`)
- User-facing copy, hero text, CTAs
- README files and documentation
- Post-mortems and sprint retrospectives
- Any text that will be read by humans (not machines)

The Humanizer pre-flight: after writing, ask "What makes this AI-generated?" → answer with bullets → fix → final pass.
