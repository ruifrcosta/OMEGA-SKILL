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
