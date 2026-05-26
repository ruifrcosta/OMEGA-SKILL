# Marketing, Growth, & Customer Conversion Reference

## Table of Contents
1. [A/B Testing & Conversion Rate Optimization (CRO)](#cro)
2. [AI SEO & Programmatic Search Optimization](#seo)
3. [Viral Growth Loops: Paywalls, Referrals, & Onboarding](#growth-loops)
4. [Copywriting & Brand-Guidelines Principles](#copywriting)
5. [Pricing Models & Competitor Analysis](#pricing)

---

## 1. A/B Testing & Conversion Rate Optimization (CRO) {#cro}

To maximize business conversion rates, OMEGA structures programmatic A/B testing interfaces utilizing Edge Middleware (e.g., Vercel Edge Config) for zero-latency bucket assignment.

### Vercel Edge A/B testing Middleware (Next.js)
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const cookieName = 'ab-variant-pricing';
  let variant = req.cookies.get(cookieName)?.value;

  if (!variant) {
    // 50/50 bucket assignment
    variant = Math.random() < 0.5 ? 'control' : 'treatment';
  }

  // Rewrite request path transparently based on variant
  const url = req.nextUrl.clone();
  if (variant === 'treatment') {
    url.pathname = `/variant-b${url.pathname}`;
  }

  const response = NextResponse.rewrite(url);
  response.cookies.set(cookieName, variant, { maxAge: 60 * 60 * 24 * 30 }); // 30 days
  return response;
}
```

---

## 2. AI SEO & Programmatic Search Optimization {#seo}

Programmatic SEO leverages structured relational data models to build thousands of highly localized, indexable pages programmatically.

### Programmatic Dynamic Route Generation (Next.js App Router)
```tsx
// app/integrations/[slug]/page.tsx
import { fetchIntegrationBySlug, fetchAllIntegrationSlugs } from '@/lib/db';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

export async function generateStaticParams() {
  const slugs = await fetchAllIntegrationSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const data = await fetchIntegrationBySlug(params.slug);
  if (!data) return {};

  return {
    title: `Integrate OMEGA with ${data.name} | Programmatic Automation`,
    description: `Connect OMEGA with ${data.name} to sync your enterprise database pipelines and security configurations instantly.`,
    alternates: {
      canonical: `https://omega.com/integrations/${params.slug}`,
    },
  };
}

export default async function IntegrationPage({ params }: { params: { slug: string } }) {
  const data = await fetchIntegrationBySlug(params.slug);
  if (!data) notFound();

  return (
    <article class="max-w-3xl mx-auto py-12 px-6">
      <h1 class="text-3xl font-extrabold tracking-tight">Connect OMEGA to {data.name}</h1>
      <p class="text-neutral-500 mt-4 leading-relaxed">{data.description}</p>
    </article>
  );
}
```

---

## 3. Viral Growth Loops: Paywalls, Referrals, & Onboarding {#growth-loops}

*   **Paywall Optimization**: Never interrupt users with hard paywalls immediately. Leverage soft metered paywalls allowing up to 3 actions, followed by clear feature comparisons.
*   **Referral Loops**: Incentivize organic user expansion by offering double-sided credits (both referrer and referee receive $20 credit upon sign-up).
*   **Frictionless Onboarding**: Keep mandatory registration inputs down to a single field (Email) with immediate OAuth fallbacks. Offload detailed workspace customization steps until after successful session initiation.

---

## 4. Copywriting & Brand-Guidelines Principles {#copywriting}

Maintain a clean, premium brand voice across all touchpoints (mimicking Stripe and Linear):

*   **Plain, Objective Copy**: Reject hyperbole. Write plain, mathematically factual value propositions. E.g. *"Compute and database synchronization under 5ms"* instead of *"Experience lightning-fast next-gen synchronization"*.
*   **Banned Clichés**: Never use terms like: "elevate", "seamless", "next-gen", "game-changer", "unleash", or "delve".
*   **Visual Continuity**: All promotional assets, newsletters, or emails must share the exact HSL design system tokens (`--bg-primary`, `--accent-primary`) defined in `02-design-system.md`.

---

## 5. Pricing Models & Competitor Analysis {#pricing}

*   **Transparent Tiers**: Maintain exactly 3 transparent pricing tiers: **Free** (sandbox), **Pro** (per-seat with usage meters), and **Enterprise** (custom billing, high-security RBAC, mTLS, dedicated clusters).
*   **Usage Metering**: Expose precise real-time cost indicators reflecting data transfer volumes, database requests count, and AI tokens consumed inside user dashboards.

---

## 6. Retention & Notification Psychology {#retention}

**Timing rules (when to send, not just what):**

| Moment | Right action |
|--------|-------------|
| First launch (session 1) | Zero friction. No paywall. No signup until value shown. |
| End of first session | Show progress made. Preview what comes next. |
| Day 2 notification | Reference the specific thing they did on day 1. |
| After first positive outcome | Right moment for app store rating request. |
| After 7 days | "Week in review" — make progress visible. |
| After inactivity 3+ days | Reference what they'll lose/miss, not just "come back". |
| At streak risk | Send within user's historically active time window. |

**Notification content rules:**
- Specific > generic: "Your dashboard had 3 new visitors" not "Check your dashboard"
- Loss framing > gain framing for retention: "Your streak ends tonight" outperforms "Keep your streak"
- Never: "We miss you" · "We thought you'd like to know" · "Just checking in"

## 7. CTA Psychology Matrix {#cta-matrix}

```
Formula: [Action Verb] + [Specific Outcome] + [Optional Qualifier]

BANNED CTAs:
  "Submit" "Send" "Click here" "Learn more" "Sign up" "Get started"

HIGH-CONVERTING CTAs by goal:
  Acquisition:  "Get your free audit" / "Start building free" / "See it in 60 seconds"
  Trial:        "Try free for 14 days" / "No credit card needed" / "Start free trial"
  Purchase:     "Get lifetime access" / "Upgrade to Pro" / "Unlock all features"
  Referral:     "Invite your team, get 3 months free" / "Share and earn $20 credit"
  Re-engagement: "Pick up where you left off" / "Your report is ready" / "3 items need review"
```

## 8. Landing Page Conversion Order {#landing-order}

Always build in this sequence — each step reduces bounce before the next CTA:

```
1. Hero — Value proposition (what you get, not what we do)
         Above fold. No scroll required to understand.

2. Social proof — Logos, numbers, or quotes (immediately below hero)
                  "Trusted by 10,000 engineers" > "Enterprise-grade"

3. Problem statement — Agitate the pain before showing the solution
                       Makes solution feel more valuable

4. Solution — Show, don't tell. Screenshots, demos, or specific outcomes.

5. Objection handling — Address the 3 most common reasons not to buy
                        "What if it doesn't work for my team?" → answer it

6. Pricing — Clear tiers, one recommended option highlighted
             Remove risk: free trial, money-back guarantee

7. Final CTA — Repeat the primary CTA with urgency or scarcity if honest
```
