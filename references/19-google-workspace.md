# Google Workspace (GWS) & Apps Script Reference

## Table of Contents
1. [GWS OAuth & API Integration Patterns](#gws-auth)
2. [Google Sheets, Docs, & Drive Automation Recipes](#docs-automation)
3. [Calendar, Forms, & Meeting Agenda Triage](#calendar-triage)
4. [Apps Script Pushes & Automated Deployments](#apps-script)
5. [Model Armor Content Sanitization](#model-armor)

---

## 1. GWS OAuth & API Integration Patterns {#gws-auth}

To coordinate activities, share metrics reports, and run operations programmatically, OMEGA integrates with Google Workspace APIs using secure scoped OAuth credentials.

### Lightweight Google API Client Singleton (NodeJS)
```typescript
import { google } from 'googleapis';

export class GoogleWorkspaceService {
  private static instance: GoogleWorkspaceService;
  private auth = new google.auth.GoogleAuth({
    scopes: [
      'https://www.googleapis.com/auth/spreadsheets',
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/gmail.send',
    ],
  });

  public static getInstance(): GoogleWorkspaceService {
    if (!GoogleWorkspaceService.instance) {
      GoogleWorkspaceService.instance = new GoogleWorkspaceService();
    }
    return GoogleWorkspaceService.instance;
  }

  async getSheetsClient() {
    const authClient = await this.auth.getClient();
    return google.sheets({ version: 'v4', auth: authClient as any });
  }

  async getDriveClient() {
    const authClient = await this.auth.getClient();
    return google.drive({ version: 'v3', auth: authClient as any });
  }
}
```

---

## 2. Google Sheets, Docs, & Drive Automation Recipes {#docs-automation}

Use automated scripts to sync database reports with accessible spreadsheet dashboards and backup assets cleanly.

### Logging Sales Events to Google Sheets
```typescript
export async function logTransactionToSheet(sheetId: string, rowData: any[]): Promise<void> {
  const gws = GoogleWorkspaceService.getInstance();
  const sheets = await gws.getSheetsClient();

  await sheets.spreadsheets.values.append({
    spreadsheetId: sheetId,
    range: 'Transactions!A:E',
    valueInputOption: 'USER_ENTERED',
    requestBody: {
      values: [rowData],
    },
  });
}
```

### Folder Asset Archiver (Drive Sync)
```typescript
export async function uploadBackupToDrive(folderId: string, fileName: string, fileBuffer: Buffer): Promise<string | null> {
  const gws = GoogleWorkspaceService.getInstance();
  const drive = await gws.getDriveClient();

  const fileMetadata = {
    name: fileName,
    parents: [folderId],
  };
  const media = {
    mimeType: 'application/octet-stream',
    body: Readable.from(fileBuffer),
  };

  const response = await drive.files.create({
    requestBody: fileMetadata,
    media: media,
    fields: 'id',
  });

  return response.data.id ?? null;
}
```

---

## 3. Calendar, Forms, & Meeting Agenda Triage {#calendar-triage}

Automate corporate operations by synchronizing team calendars and triaging unread communications.

*   **Meeting Room Synchronization**: Fetch free/busy timetables from Google Calendar before scheduling events to prevent booking collisions.
*   **Form Trigger Pipeline**: Subscribe to Google Forms webhook payloads to automatically append contacts or generate workspace billing entities inside Supabase.
*   **Gmail Agenda Triage**: Schedule recurrent cron workers to extract unread email headers, parsing them for urgent notifications using the SRE incident SLA scales.

---

## 4. Apps Script Pushes & Automated Deployments {#apps-script}

OMEGA deploys localized Google Apps Scripts using `clasp` (Command Line Apps Script Projects) to allow automated macros execution directly inside Google Spreadsheets.

```bash
# Push local javascript modules to remote Google Apps Script container
rtk npx clasp push --force
```

---

## 5. Model Armor Content Sanitization {#model-armor}

Before forwarding user inputs to downstream LLM modules, evaluate and filter payloads using **Google Model Armor** templates to prevent prompt injection and data leakages.

### Content Sanitizer Pipeline
```typescript
import { ModelArmor } from '@google/model-armor';

export async function sanitizeUserPrompt(rawPrompt: string): Promise<string> {
  const armor = new ModelArmor({
    templateName: 'titan-prompt-security',
  });

  const assessment = await armor.assess({
    text: rawPrompt,
  });

  if (assessment.hasViolation) {
    throw new SecurityException('Input violates enterprise prompt security guidelines');
  }

  return rawPrompt;
}
```
