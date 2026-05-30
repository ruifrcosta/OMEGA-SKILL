# Mobile Engineering Reference

## Table of Contents
1. [Architecture & Folder Structure](#architecture)
2. [Expo Router — Navigation Patterns](#routing)
3. [Offline-First: MMKV + WatermelonDB](#offline)
4. [Performance: FlashList, Reanimated, Native Driver](#perf)
5. [Secure Storage & Biometrics](#security)
6. [OTA Updates & Build Pipeline](#ota)
7. [Troubleshooting Playbook](#troubleshooting)

---

## 1. Architecture & Folder Structure {#architecture}

```
mobile/
├── app/                       # Expo Router file-based routes
│   ├── (auth)/                # Auth group — unauthenticated
│   │   ├── sign-in.tsx
│   │   └── _layout.tsx
│   ├── (app)/                 # Main group — requires auth
│   │   ├── (tabs)/
│   │   │   ├── index.tsx      # Home tab
│   │   │   ├── settings.tsx
│   │   │   └── _layout.tsx
│   │   └── _layout.tsx        # Auth guard here
│   ├── _layout.tsx            # Root: providers, fonts, SplashScreen
│   └── +not-found.tsx
├── components/
│   ├── ui/                    # Base: Button, Input, Card
│   └── features/              # Feature-specific
├── lib/
│   ├── supabase.ts            # Supabase client (singleton)
│   ├── db/                    # WatermelonDB schema + models
│   └── stores/                # Zustand stores
├── hooks/                     # useAuth, useSync, useColorScheme
└── constants/                 # Colors, typography, spacing
```

### Root Layout — mandatory providers
```tsx
// app/_layout.tsx
export default function RootLayout() {
  const [fontsLoaded] = useFonts({ /* fonts */ });

  useEffect(() => {
    if (fontsLoaded) SplashScreen.hideAsync();
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SupabaseProvider>
        <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
          <Stack screenOptions={{ headerShown: false }} />
          <StatusBar style="auto" />
        </ThemeProvider>
      </SupabaseProvider>
    </GestureHandlerRootView>
  );
}
```

---

## 2. Expo Router — Navigation Patterns {#routing}

### Auth Guard (protect authenticated routes)
```tsx
// app/(app)/_layout.tsx
export default function AppLayout() {
  const { session, loading } = useAuth();

  if (loading) return <LoadingScreen />;

  if (!session) {
    return <Redirect href="/(auth)/sign-in" />;
  }

  return <Stack />;
}
```

### Typed Navigation (always use typed params)
```typescript
// types/navigation.ts — generate with expo-router types
// Access: const { id } = useLocalSearchParams<{ id: string }>();
// Navigate: router.push({ pathname: '/workspace/[id]', params: { id: workspace.id } });
```

---

## 3. Offline-First: MMKV + WatermelonDB {#offline}

### MMKV — fast key-value (replace AsyncStorage everywhere)
```typescript
import { MMKV } from 'react-native-mmkv';

export const storage = new MMKV({ id: 'app-storage' });

// Zustand persist middleware with MMKV
const mmkvStorage = {
  getItem: (key: string) => storage.getString(key) ?? null,
  setItem: (key: string, value: string) => storage.set(key, value),
  removeItem: (key: string) => storage.delete(key),
};
```

### WatermelonDB — relational offline SQL
```typescript
// lib/db/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 3,
  tables: [
    tableSchema({
      name: 'workspaces',
      columns: [
        { name: 'remote_id', type: 'string', isIndexed: true },
        { name: 'name', type: 'string' },
        { name: 'updated_at', type: 'number' },
        { name: 'is_synced', type: 'boolean' },
      ],
    }),
  ],
});

// Sync pattern: local-first, push/pull on reconnect
async function syncWithServer(db: Database, userId: string) {
  await synchronize({
    database: db,
    pullChanges: async ({ lastPulledAt }) => {
      const { data } = await supabase.rpc('pull_changes', { last_pulled_at: lastPulledAt, user_id: userId });
      return { changes: data.changes, timestamp: data.timestamp };
    },
    pushChanges: async ({ changes }) => {
      await supabase.rpc('push_changes', { changes });
    },
    migrationsEnabledAtVersion: 1,
  });
}
```

---

## 4. Performance: FlashList, Reanimated, Native Driver {#perf}

### FlashList — replace ALL FlatList with 50+ items
```tsx
import { FlashList } from '@shopify/flash-list';

// estimatedItemSize is REQUIRED — measure your actual item height
<FlashList
  data={items}
  renderItem={({ item }) => <ItemRow item={item} />}
  estimatedItemSize={72}
  keyExtractor={(item) => item.id}
  getItemType={(item) => item.type}  // optimize heterogeneous lists
/>
```

### Reanimated — ALWAYS useNativeDriver
```typescript
// NEVER: animation that runs on JS thread
Animated.timing(value, { toValue: 1, useNativeDriver: false }).start(); // ❌ drops frames

// ALWAYS: runs on UI thread
const opacity = useSharedValue(0);
const style = useAnimatedStyle(() => ({
  opacity: withTiming(opacity.value, { duration: 300, easing: Easing.out(Easing.quad) }),
}));

// Gesture + animation (always on UI thread)
const gesture = Gesture.Pan()
  .onUpdate((e) => { translateX.value = e.translationX; })
  .onEnd((e) => {
    if (Math.abs(e.velocityX) > 500 || Math.abs(e.translationX) > DISMISS_THRESHOLD) {
      translateX.value = withSpring(e.translationX > 0 ? 500 : -500, {}, () => {
        runOnJS(onDismiss)();
      });
    } else {
      translateX.value = withSpring(0);
    }
  });
```

### Performance Budget
```
App launch (cold)    : < 3s on mid-range Android
App launch (warm)    : < 1s
List scroll          : 60fps locked (no JS thread drops)
Network request      : show skeleton within 100ms
Image load           : use expo-image with blurhash placeholder
Bundle size          : < 2MB JS bundle (measure with expo export --analyze)
```

---

## 5. Secure Storage & Biometrics {#security}

```typescript
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';

// NEVER: AsyncStorage for tokens
// NEVER: MMKV for tokens (not encrypted by default on all platforms)
// ALWAYS: SecureStore (Keychain on iOS, Keystore on Android)

export const tokenStorage = {
  async save(key: string, value: string): Promise<void> {
    await SecureStore.setItemAsync(key, value, {
      keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    });
  },
  async get(key: string): Promise<string | null> {
    return SecureStore.getItemAsync(key);
  },
  async delete(key: string): Promise<void> {
    await SecureStore.deleteItemAsync(key);
  },
};

export async function requireBiometrics(): Promise<boolean> {
  const compatible = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  if (!compatible || !enrolled) return true; // fallback: allow without biometrics

  const { success } = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Verify your identity',
    cancelLabel: 'Cancel',
    disableDeviceFallback: false,
  });
  return success;
}
```

---

## 6. OTA Updates & Build Pipeline {#ota}

### EAS Update — channel strategy
```json
// eas.json
{
  "build": {
    "development": { "developmentClient": true, "distribution": "internal", "channel": "development" },
    "staging":     { "distribution": "internal", "channel": "staging" },
    "production":  { "distribution": "store",    "channel": "production", "autoIncrement": true }
  },
  "submit": {
    "production": {
      "ios":     { "appleId": "${APPLE_ID}", "ascAppId": "${ASC_APP_ID}" },
      "android": { "serviceAccountKeyPath": "./google-play-key.json", "track": "production" }
    }
  }
}
```

```bash
# Deploy hotfix to production (JS-only change, no native)
eas update --branch production --message "fix: resolve checkout crash on Android 14"

# Force update check at app start
import * as Updates from 'expo-updates';

async function checkForUpdate() {
  if (!Updates.isEmbeddedLaunch) return;
  const { isAvailable } = await Updates.checkForUpdateAsync();
  if (isAvailable) {
    await Updates.fetchUpdateAsync();
    await Updates.reloadAsync();
  }
}
```

---

## 7. Troubleshooting Playbook {#troubleshooting}

### Metro bundler hangs / fails
```bash
# Nuclear clear — solves 80% of Metro issues
npx expo start --clear
watchman watch-del-all && watchman shutdown-server
rm -rf node_modules .expo && npm install
```

### "Invariant Violation: No such key" (navigation)
```
Cause: accessing params before navigation is ready, OR wrong route name
Fix:
1. Use useLocalSearchParams() instead of route.params
2. Wrap with useFocusEffect if you need params on focus
3. Check Expo Router route groups: (auth) not (auth)/sign-in in the href
```

### Android white screen on launch
```
Cause: SplashScreen.preventAutoHideAsync() called but SplashScreen.hideAsync() never fires
Fix: ensure hideAsync() is called in a finally block, even on font load errors
```

### iOS simulator "Build failed: clang error"
```bash
cd ios && pod install --repo-update && cd ..
# If still failing:
sudo xcode-select --switch /Applications/Xcode.app
```

### Reanimated "Worklet" crash
```
Cause: calling a JS function from worklet without runOnJS()
Fix: wrap ALL JS callbacks called from gesture handlers with runOnJS(callback)()
```

### Performance — identify JS thread drops
```bash
# Enable Flipper profiler OR:
# React Native DevTools → Profiler → record during scroll
# Look for: JS thread > 16ms per frame = drop
# Common fix: move animation values to useSharedValue, never useState
```
