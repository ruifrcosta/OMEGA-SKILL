# Mobile Engineering Reference

## Table of Contents
1. [Expo Router App Architecture](#expo-router)
2. [Offline-First Data Synchronization](#offline-first)
3. [Secure Storage & Biometrics](#security)
4. [OTA Deployments using EAS Update](#eas-update)

---

## 1. Expo Router App Architecture {#expo-router}

OMEGA TITAN mobile applications utilize Expo and Expo Router for robust type-safe file-based routing across iOS and Android systems.

### Directory Structure
```
mobile/
├── app/                    # File-based routes
│   ├── (auth)/             # Auth group
│   │   ├── sign-in.tsx
│   │   └── sign-up.tsx
│   ├── (tabs)/             # Tab navigation group
│   │   ├── index.tsx       # Home
│   │   ├── settings.tsx
│   │   └── _layout.tsx     # Tab composition
│   ├── _layout.tsx         # Root provider composition
│   └── +not-found.tsx
├── components/             # Reusable UI elements
├── hooks/                  # Custom hooks (sync, bio)
└── lib/                    # SDK definitions (Supabase)
```

---

## 2. Offline-First Data Synchronization {#offline-first}

Mobile architectures require offline resilience. State mutations must occur locally first and synchronize with central database systems when internet connectivity becomes available.

### WatermelonDB Initialization Pattern
We utilize WatermelonDB or SQLite for raw, high-performance offline SQL storage:

```typescript
// db/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export default appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'tasks',
      columns: [
        { name: 'title', type: 'string' },
        { name: 'completed', type: 'boolean' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
      ]
    }),
  ]
});
```

---

## 3. Secure Storage & Biometrics {#security}

Never save sensitive properties (JWT auth tokens, private API keys, user biometrics) in plain text files or AsyncStorage. Enforce hardware-level security context.

### Secure Credentials Handler
```typescript
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';

export async function saveAuthToken(token: string): Promise<void> {
  await SecureStore.setItemAsync('user_auth_token', token, {
    keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
}

export async function authenticateWithBiometrics(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();

  if (!hasHardware || !isEnrolled) return false;

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Authenticate with FaceID / TouchID to unlock your workspace',
    fallbackLabel: 'Use passcode',
    disableDeviceFallback: false,
  });

  return result.success;
}
```

---

## 4. OTA Deployments using EAS Update {#eas-update}

To optimize hotfix cycles without undergoing App Store / Play Store reviews, configure **EAS Update** for safe OTA deliveries.

### EAS Configurations (`eas.json`)
```json
{
  "cli": {
    "version": ">= 9.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "production": {
      "distribution": "store",
      "ios": {
        "simulator": false
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

Deploy OTA Hotfixes using command pipeline:
```bash
rtk eas update --branch production --message "Hotfix: resolve layout shift in workspace tab"
```
