---
name: frappe-ui
description: A guide for using frappe-ui components and composables in Vue 3 applications.
---

# Frappe UI Development Guide

This document defines the standard practices, tools, and components for developing applications using `frappe-ui`. Coding agents should adhere to these guidelines when building features or fixing bugs in projects utilizing the Frappe UI library.

## Ecosystem & Tooling

*   **Framework:** Vue 3 (Composition API)
*   **Styling:** Tailwind CSS (via `frappe-ui/tailwind`)
*   **Icons:** Lucide Icons or Feather Icons integration
*   **Data Fetching:** Frappe-specific API hooks (`useCall`, `useList`, `useDoc`, `useFrappeFetch`)
*   **State & Utility:** Uses `@vueuse/core` under the hood.

## Component Library

Frappe UI provides a comprehensive set of polished UI components. Always prefer these built-in components before creating custom ones or installing external libraries.

### Importing Components
All primary components and hooks can be imported directly from `frappe-ui`.

```javascript
import { Button, Input, Dialog, useDoc } from 'frappe-ui'
```

### Core Components Reference

*   **Inputs & Controls:**
    *   `Button`, `Input`, `TextInput`, `Password`, `Textarea`
    *   `Checkbox`, `Switch`, `Slider`, `FileUploader`
    *   `FormControl` (wrapper for labels and error messages)
    *   `DatePicker`, `TimePicker`, `MonthPicker`
*   **Selection & Dropdowns:**
    *   `Select`, `MultiSelect`, `Combobox`, `Autocomplete`, `Dropdown`
*   **Layout & Data Display:**
    *   `Card`, `ListView` (and its subcomponents like `ListHeader`, `ListRow`, etc.), `ItemListRow`
    *   `Tabs`, `TabButtons`, `Breadcrumbs`, `Sidebar`, `Tree`, `CommandPalette`
    *   **Charts:** `AxisChart`, `DonutChart`, `FunnelChart`, `ECharts`, `NumberChart`
    *   `Calendar`
*   **Overlays & Feedback:**
    *   `Dialog`, `ConfirmDialog`, `Popover`, `Tooltip`, `NestedPopover`
    *   `Alert`, `Badge`, `ErrorMessage`
    *   `LoadingIndicator`, `LoadingText`, `Spinner`
    *   `Toast` (and the `toast` utility method)
*   **Formatting:**
    *   `Avatar`, `TextEditor` (Tiptap based rich text editor)

## Data Fetching (Frappe Backend)

Frappe UI provides highly optimized composables to interact directly with the Frappe backend. These abstract away authentication (session management) and standard REST/RPC API mechanics.

### 1. `useCall` (General RPC)
Used for calling whitelist methods.

```javascript
import { useCall } from 'frappe-ui'

const loginCall = useCall({
  method: 'login', // Frappe method path
  args: { usr: 'test@example.com', pwd: 'password' },
  onSuccess: (data) => console.log('Logged in', data),
  onError: (error) => console.error(error),
})

// Trigger the call
loginCall.submit() // or loginCall.fetch()
```

### 2. `useDoc` / `useNewDoc` (Single Document Management)
Used to fetch, track changes, update, and manage the lifecycle of a specific Frappe document.

```javascript
import { useDoc, useNewDoc } from 'frappe-ui'

// Existing Document
const userDoc = useDoc({
  doctype: 'User',
  name: 'Administrator',
})
await userDoc.fetch()

// Access data
console.log(userDoc.doc)

// Mutate data directly locally
userDoc.setValue('first_name', 'Admin')

// Save changes back to server
await userDoc.save()

// New Document
const newUser = useNewDoc({
  doctype: 'User',
})
newUser.setValue('email', 'new@example.com')
await newUser.insert()
```

### 3. `useList` (List of Documents)
Used to fetch a paginated list of documents.

```javascript
import { useList } from 'frappe-ui'

const users = useList({
  doctype: 'User',
  fields: ['name', 'full_name', 'email'],
  filters: { enabled: 1 },
  limit: 20,
  orderBy: 'creation desc',
})

await users.fetch()
// users.data contains the list of records
// users.next() fetches the next page
```

### 4. `useFrappeFetch` (General Fetch)
A general-purpose composable similar to `useFetch` tailored for Frappe endpoints.

## Setup & Configuration

### Vite Plugin
Frappe UI provides a Vite plugin for common integrations like proxying API calls to the Frappe backend server, resolving Frappe types, injecting Jinja boot data, and enabling Lucide icons.

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'

export default defineConfig({
  plugins: [
    vue(),
    frappeui({
      frontendRoute: 'app',    // Route used to host the Vue app in Frappe
      lucideIcons: true,       // Enable lucide icons resolution
      frappeProxy: true,       // Proxy /api to Frappe backend on port 8000
    })
  ]
})
```

### Tailwind Preset
Frappe UI brings its own Tailwind plugin and preset. It includes `@tailwindcss/forms` and `@tailwindcss/typography` by default and injects a robust set of UI variable styles.

```javascript
// tailwind.config.js
import preset from 'frappe-ui/tailwind/preset'

export default {
  presets: [preset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
}
```

## Best Practices

1.  **Vue 3 Composition API:** Exclusively use `<script setup>` syntax for all new Vue components.
2.  **Tailwind Utility Classes:** Rely strictly on standard Tailwind classes. Avoid custom CSS unless absolutely necessary.
3.  **Form Controls:** Instead of manual label management, use `FormControl` for rendering form inputs alongside their labels and potential error states.
4.  **Icons Integration:** Utilize `FeatherIcon` or resolved `lucide-vue-next` icons natively without needing standalone icon library installations.
5.  **Directives:** Utilize exported directives like `v-on-outside-click` (`onOutsideClickDirective`) for handling dropdown or popover logic rather than rolling custom event listeners.
