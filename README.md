# Etherea — Desktop Adaptive Workspace (Project)

Etherea is a desktop-first adaptive interface that responds to user focus, stress, and activity.  
The goal is to create a calm, distraction-aware digital workspace that feels responsive, personal, and supportive.

This project currently focuses on the **UI layer**, with future plans for sensor inputs, avatars, and adaptive behavior.

---

## 📂 Project Structure

```
etherea-tutorial/
├── README.md
├── .gitignore
├── main.py
├── requirements.txt
├── assets/
│   └── (images, sounds, models, etc.)
├── components/
│   ├── __init__.py
│   ├── audio.py
│   ├── avatar.py
│   ├── background.py
│   ├── ei_signals.py
│   ├── db.py
│   └── utils.py
└── data/
    └── (sqlite db, logs, runtime files)
```

> Important: There should be **no duplicated folders** such as  
> `src/components/src/components`.

---

## 🎯 Core Idea

Etherea aims to:

1. Reduce on-screen distractions.
2. Adapt visuals and interactions based on user context.
3. Create a workspace that “feels alive,” but always stays under user control.

This is a **desktop-first** project.  
Mobile development is secondary and planned for later.

---

## 🛠️ Technologies Used

- React + TypeScript
- Vite
- Three.js (for 3D/visual effects where applicable)
- Custom UI components

---

## 🚀 Getting Started (Development)

### 1️⃣ Install dependencies

```bash
npm install
```

### 2️⃣ Start development server

```bash
npm run dev
```

### 3️⃣ Open in browser

Open the local URL printed in terminal, usually:

```
http://localhost:5173
```

---

## 🧩 Components Overview

### `ScenePlayer.tsx`
Loads and renders background scenes.

### `Avatar3D.tsx`
Interactive avatar (future adaptive/emotion behavior planned).

### `Background3D.tsx`
Controls animated background visuals.

### `EIVisualizer.tsx`
Prototype visualization for emotional/adaptive responses.

### `AudioPlayer.tsx`
Handles ambient focus audio.

---

## 🔒 Privacy & Control

- No tracking without consent.
- Clear “kill switch” for adaptive behavior.
- User remains fully in control of data.

---

## 🧭 Roadmap (High Level)

- Adaptive UI themes
- Emotion-aware avatar behavior
- Local database + learning logic
- Strong privacy design
- Desktop app packaging

> Not designed for Android/iOS right now.

---

## 🐛 Troubleshooting

### Duplicate folders
Delete any folders like:

```
src/components/src
```

All components should live only in:

```
src/components
```

### Dev server fails
Run:

```bash
npm install
npm run dev
```

Ensure Node.js is installed and updated.

---

## 📄 License

Currently for learning and academic purposes.  
A formal license may be added later.

---

## ✨ Credits

**Brunda G**
Lead developer, concept, implementation, documentation.
