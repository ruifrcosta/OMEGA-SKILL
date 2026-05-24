# Supabase & Resend Orchestration Reference

## Table of Contents
1. [Supabase Row-Level Security (RLS) Rules](#rls-rules)
2. [Secure database Schemas & Auth](#db-auth)
3. [Secure Serverless Edge Functions](#edge-functions)
4. [Resend Transactional Communication Workflows](#resend-workflows)

---

## 1. Supabase Row-Level Security (RLS) Rules {#rls-rules}

All tables created inside Supabase production databases must enforce strict Row-Level Security (RLS). Public read/write permissions are strictly prohibited.

```sql
-- Mandated table creation pipeline
CREATE TABLE workspaces (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL,
  owner_id uuid REFERENCES auth.users(id) NOT NULL,
  created_at timestamp DEFAULT now() NOT NULL
);

-- 1. Enable RLS explicitly
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;

-- 2. Define secure scoped policies
CREATE POLICY "Users can only read workspaces they own"
ON workspaces
FOR SELECT
TO authenticated
USING (auth.uid() = owner_id);

CREATE POLICY "Users can only mutate workspaces they own"
ON workspaces
FOR ALL
TO authenticated
USING (auth.uid() = owner_id)
WITH CHECK (auth.uid() = owner_id);
```

---

## 2. Secure Database Schemas & Auth {#db-auth}

Database schemas must prevent SQL injections and automate user creation transitions.

### Automated Profile Creation Trigger
```sql
-- Automatically generate a profile entry when auth.users is populated
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

---

## 3. Secure Serverless Edge Functions {#edge-functions}

Deno-based serverless Edge Functions must validate request signatures, authenticate tenants, and enforce secure CORS scopes.

### Deno Edge Function Template (`supabase/functions/create-invite/index.ts`)
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://workspace.omega-titan.com',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // 1. Handle preflight CORS requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 2. Resolve client connection
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // 3. Authenticate User Context
    const { data: { user }, error } = await supabaseClient.auth.getUser()
    if (error || !user) throw new Error('Unauthorized')

    const { email, role } = await req.json()

    // 4. Secure business logic
    // Execute DB insert or target operations here

    return new Response(
      JSON.stringify({ success: true, message: 'Invite created' }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (err: any) {
    return new Response(
      JSON.stringify({ error: err.message }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
```

---

## 4. Resend Transactional Communication Workflows {#resend-workflows}

Transaction communication utilizes **Resend** with robust fallback structures to prevent notification loss during outages.

### Robust Resend Transaction Service
```typescript
import { Resend } from 'resend';

export class NotificationService {
  private resend = new Resend(process.env.RESEND_API_KEY);

  async sendWorkspaceInvite(email: string, inviteUrl: string): Promise<boolean> {
    try {
      const response = await this.resend.emails.send({
        from: 'Omega Titan Workspace <no-reply@omega-titan.com>',
        to: [email],
        subject: 'You have been invited to OMEGA TITAN',
        html: `<p>Click <a href="${inviteUrl}">here</a> to access your enterprise workspace.</p>`,
      });

      return !!response.data?.id;
    } catch (err) {
      console.error('Primary Resend notification pipeline failed, queuing fallback...', err);
      // Execute database fallback queue insertion
      await this.queueFallbackNotification(email, inviteUrl);
      return false;
    }
  }

  private async queueFallbackNotification(email: string, inviteUrl: string) {
    // Write notification payload to failover table for background worker processing
  }
}
```
