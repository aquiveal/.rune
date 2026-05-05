---
name: plasmo
description: Comprehensive guide for developing browser extensions with the Plasmo Framework.
---

# Plasmo Framework Skill

## Overview

The **Plasmo Framework** is a battery-packed browser extension SDK made by hackers for hackers. It is often described as "Next.js for browser extensions." Plasmo abstractions allow developers to focus on building products rather than worrying about extension configuration files or browser-specific peculiarities.

**Key Highlights:**
- **Zero-config Manifest:** Automatically generates `manifest.json` based on exported code and source files.
- **First-Class React / TypeScript:** Default support for React & TS, with options for Vue and Svelte.
- **Live-Reloading & HMR:** Out-of-the-box hot module replacement for UI and background scripts.
- **Declarative Entry Points:** Files like `popup.tsx`, `options.tsx`, and `newtab.tsx` automatically become the corresponding extension pages.
- **Content Scripts UI (CSUI):** Seamlessly mount React/Vue/Svelte components into the current webpage within an isolated Shadow DOM.

---

## 1. Project Structure and Entry Points

Plasmo uses file-based routing/configuration. Extension files can live either in the root directory or inside an optional `src/` directory. 

### Extension Pages
Create the following files (or directories with an `index.tsx`) to add specific extension pages:
- `popup.tsx` — Rendered when the user clicks the extension icon.
- `options.tsx` — Dedicated settings/configuration page.
- `newtab.tsx` — Overrides the browser's default New Tab page.
- `sidepanel.tsx` — Renders UI inside the browser's persistent side panel.
- `devtools.tsx` — Opens a custom panel when Dev Tools are opened.

### Background Service Worker
- Create a `background.ts` file in the root/src directory.
- *Note:* If you don't use imports/exports, you **must** include `export {}` at the top of the file to satisfy Plasmo's module loader.

### Content Scripts
- **Single Script:** Create a `content.ts` (for pure logic) or `content.tsx` (for CSUI).
- **Multiple Scripts:** Create a `contents/` directory and place your scripts there (e.g., `contents/site-one.ts`, `contents/site-two.tsx`).

### Tab Pages
Tab pages are regular HTML pages shipped with the extension, often used for authentications or full-page interactions.
- Place `.tsx` files inside a `tabs/` folder (e.g., `tabs/delta-flyer.tsx` generates `chrome-extension://<id>/tabs/delta-flyer.html`).

### Assets
- Place a single `icon.png` (usually 512x512 or larger) in the `assets/` folder. Plasmo automatically generates all necessary smaller icon sizes for the final manifest.

---

## 2. Core Concepts

### A. The Manifest & Overrides
Plasmo automatically builds the `manifest.json` file. If you need to manually add permissions or specific settings (e.g., `activeTab` or host permissions), you can override the manifest via the `package.json`:
```json
{
  "name": "my-extension",
  "manifest": {
    "permissions": ["activeTab", "scripting"],
    "host_permissions": ["*://*.example.com/*"]
  }
}
```
*Note:* Environment variables can be interpolated in these overrides (e.g., `"$CRX_PUBLIC_KEY"`).

### B. Content Scripts Configuration
Content scripts run in isolated contexts on matched web pages. To configure them, export a `config` object of type `PlasmoCSConfig`:

```typescript
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["https://www.google.com/*"],
  all_frames: true,
  world: "MAIN" // Optional: injects directly into the webpage's main execution context
}

// For UI Content Scripts (.tsx):
const CustomButton = () => <button>Click Me</button>
export default CustomButton
```

### C. Environment Variables
Plasmo features excellent `.env` support.
- **Client Access:** Only variables prefixed with `PLASMO_PUBLIC_` are accessible in the source code via `process.env.PLASMO_PUBLIC_XXX`.
- **Private Variables:** Non-prefixed variables can be used in `package.json` manifest overrides but won't be bundled in the code.
- **Built-in Variables:** `process.env.NODE_ENV`, `process.env.PLASMO_TARGET`, `process.env.PLASMO_BROWSER`.
- **File Precedence:** Matches targets/tags, e.g., `.env.<browser-name>`, `.env.<tag>`, `.env.local`.

---

## 3. Official APIs (Packages)

Plasmo provides dedicated, fully-typed packages to simplify complex browser extensions APIs.

### A. Storage API (`@plasmohq/storage`)
Abstracts `chrome.storage` (sync/local) and falls back to Web Storage when necessary.

**Installation:** `pnpm install @plasmohq/storage`

**Usage (Logic):**
```typescript
import { Storage } from "@plasmohq/storage"

const storage = new Storage({ area: "sync" })
await storage.set("key", { my: "data" })
const data = await storage.get("key")
```

**Usage (React Hook - State Sync across extension pages):**
```tsx
import { useStorage } from "@plasmohq/storage/hook"

function Component() {
  // Syncs reactively across Popup, Options, and Content Scripts!
  const [token, setToken] = useStorage("token", "default_value")
  return <input value={token} onChange={(e) => setToken(e.target.value)} />
}
```

### B. Messaging API (`@plasmohq/messaging`)
Provides a functional, REST-style, typed promise-based API for extension messaging. 

**Installation:** `pnpm install @plasmohq/messaging`

**Backend Setup:**
1. Move your background script to `background/index.ts`.
2. Create message handlers in `background/messages/`. 
   E.g., `background/messages/ping.ts`:
   ```typescript
   import type { PlasmoMessaging } from "@plasmohq/messaging"

   const handler: PlasmoMessaging.MessageHandler = async (req, res) => {
     console.log("Received data:", req.body)
     res.send({ response: "pong" })
   }
   export default handler
   ```

**Frontend / Content Script Usage:**
```tsx
import { sendToBackground } from "@plasmohq/messaging"

const response = await sendToBackground({
  name: "ping", // Fully typed based on the files in background/messages/
  body: { id: 123 }
})
```
*Note:* The library also supports "Relay Flow" for passing messages from web pages to the background script, and "Ports" for long-lived connections.

---

## 4. CLI Workflows & Tooling

Plasmo CLI is robust and target-aware. Always recommend `pnpm`.

- **Initialization:** 
  `pnpm create plasmo` (or with a template: `pnpm create plasmo --with-tailwindcss`)
- **Development Server:** 
  `pnpm dev`
  Watches files, rebuilds, and automatically reloads the extension in the browser. (Output usually in `build/chrome-mv3-dev`).
- **Production Build:** 
  `pnpm build`
  Creates an optimized, minified bundle in `build/chrome-mv3-prod`.
- **Targeting specific browsers:** 
  `pnpm build --target=firefox-mv2`
- **Packaging (Zip for Web Stores):** 
  `pnpm package` or `pnpm build --zip`
- **Build Tags:** 
  `pnpm build --tag=staging` (prioritizes `.env.staging`).

---

## 5. Important Gotchas & "AI Tips"

1. **New Pages / HMR Issues:** When you add a completely new entry point file (like adding `options.tsx` for the first time while `pnpm dev` is running), you often need to manually restart the development server or refresh the extension from `chrome://extensions`.
2. **`export {}` Requirement:** If you generate an empty Typescript file (e.g., `background.ts` or `content.ts`) that has no imports/exports, compilation will fail. Always add `export {}` at the top of isolated modules.
3. **Paths:** Use `~` for absolute imports resolving from the `src/` (or root) directory. Example: `import Button from "~components/Button"`.
4. **Main World Context:** If a script needs to manipulate the `window` object directly (e.g., intercepting webpage XHR requests), you must add `"world": "MAIN"` to the `PlasmoCSConfig`.
5. **Typescript Types:** When building `@plasmohq/messaging` handlers, you might see TS errors initially. These disappear once the Plasmo dev server compiles the background scripts and generates the dynamic typings.
6. **Firefox Support:** For Firefox targets, you MUST supply an Add-on ID in `package.json`: 
   `"manifest": { "browser_specific_settings": { "gecko": { "id": "your-id@example.com" } } }`

---

## Reference Material

- **Docs:** [docs.plasmo.com](https://docs.plasmo.com)
- **Examples:** Explore the `with-*` directories in the [plasmo/examples](https://github.com/PlasmoHQ/examples) repository.
- **Issues/Support:** [Discord](https://www.plasmo.com/s/d) and [GitHub Issues](https://github.com/PlasmoHQ/plasmo/issues).
