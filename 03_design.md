# Design Document
## RA HousingBot — UI/UX Design Specifications

---

## 1. Design Philosophy

The interface should feel **calm, trustworthy, and efficient**. RAs often consult this tool during stressful situations (resident conflicts, emergencies, late-night incidents). The design must minimize cognitive load — clean layout, clear typography, no clutter. It should feel like a knowledgeable colleague, not a generic chatbot.

---

## 2. Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#1A3A5C` | Header bar, primary buttons, active states |
| Secondary | `#2E86AB` | Links, highlights, citation tags |
| Background | `#F5F7FA` | Page background |
| Surface | `#FFFFFF` | Chat bubbles, cards |
| User Bubble | `#DCE8F5` | User message background |
| Bot Bubble | `#FFFFFF` | Assistant message background (with border) |
| Success | `#27AE60` | Thumbs up confirmation, upload success |
| Warning | `#E67E22` | Fallback message border |
| Error | `#C0392B` | Error states |
| Text Primary | `#1C1C1E` | Main body text |
| Text Muted | `#6B7280` | Citations, metadata, timestamps |
| Border | `#E2E8F0` | Card borders, dividers |

---

## 3. Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| App Title | Inter | 22px | Bold |
| Section Headings | Inter | 16px | SemiBold |
| Body / Chat Text | Inter | 14px | Regular |
| Citations | Inter | 12px | Regular, Italic |
| Buttons | Inter | 14px | Medium |
| Placeholder Text | Inter | 14px | Regular, color: Text Muted |

Use system font stack as fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`

---

## 4. Layout

### 4a. Main Chat Page

```
┌─────────────────────────────────────────────────────┐
│  🏠 RA HousingBot                    [Admin Login]   │  ← Header (Primary color)
├─────────────────────────────────────────────────────┤
│                                                       │
│  💬 Ask me anything about housing policies...        │  ← Hero subtitle
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │ Suggested: "What's the guest policy?"        │    │  ← Suggestion chips
│  │ "How do I file an incident report?"          │    │
│  │ "What are quiet hours?"                      │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ──────────────── Chat History ──────────────────    │
│                                                       │
│            ┌────────────────────────────┐            │
│            │ What is the guest policy?  │  ← User   │
│            └────────────────────────────┘            │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │ 🤖 According to the RA Handbook (Section 4), │   │  ← Bot reply
│  │ guests may stay up to 2 consecutive nights...│   │
│  │                                               │   │
│  │ 📄 Source: RA Handbook 2024, Section 4.2     │   │  ← Citation
│  │                                               │   │
│  │                              👍  👎           │   │  ← Feedback
│  └──────────────────────────────────────────────┘   │
│                                                       │
├─────────────────────────────────────────────────────┤
│  [ Ask a question about housing policies...    ] [→] │  ← Input bar (sticky bottom)
└─────────────────────────────────────────────────────┘
```

### 4b. Admin Document Management Page

```
┌─────────────────────────────────────────────────────┐
│  🏠 RA HousingBot — Admin Panel              [Logout]│
├─────────────────────────────────────────────────────┤
│                                                       │
│  📁 Upload New Document                              │
│  ┌────────────────────────────────────────────────┐ │
│  │        Drag & drop PDF or DOCX here            │ │
│  │              or [Browse Files]                  │ │
│  └────────────────────────────────────────────────┘ │
│                                                       │
│  📚 Ingested Documents (4)                           │
│  ┌──────────────────────────────────────────────┐   │
│  │ RA Handbook 2024.pdf       42 chunks  [🗑 Delete]│
│  │ Emergency Procedures.pdf   18 chunks  [🗑 Delete]│
│  │ Conduct Policy.docx        31 chunks  [🗑 Delete]│
│  │ Resident Agreement.pdf     25 chunks  [🗑 Delete]│
│  └──────────────────────────────────────────────┘   │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 5. Component Specs

### Chat Bubble — User
- Background: `#DCE8F5`
- Border radius: `12px 12px 2px 12px` (right-aligned, pointed bottom-right)
- Max width: 70% of chat area
- Padding: `12px 16px`
- Aligned: right

### Chat Bubble — Assistant
- Background: `#FFFFFF`
- Border: `1px solid #E2E8F0`
- Border radius: `12px 12px 12px 2px` (left-aligned, pointed bottom-left)
- Max width: 85% of chat area
- Padding: `16px`
- Includes: answer text, citation block, feedback row

### Citation Tag
- Background: `#EFF6FF`
- Border: `1px solid #BFDBFE`
- Border radius: `6px`
- Font: 12px, italic, color `#2563EB`
- Icon: 📄 before document name

### Feedback Buttons
- Unselected: ghost style, gray
- Selected thumbs up: green fill
- Selected thumbs down: red fill
- Size: 20px icon, 8px padding

### Input Bar
- Sticky to bottom of chat container
- Border: `1px solid #CBD5E1`
- Border radius: `24px`
- Send button: circle, Primary color
- Placeholder: "Ask a question about housing policies..."

### Fallback Message
- Left border: `4px solid #E67E22`
- Background: `#FFF7ED`
- Includes icon ⚠️ and suggestion to contact Hall Director

---

## 6. Responsive Design

- **Desktop (>1024px):** Sidebar (optional) + main chat, max content width 800px centered
- **Tablet (768–1024px):** Single column, full width chat
- **Mobile (<768px):** Streamlit default mobile rendering (acceptable for v1)

---

## 7. Accessibility

- All interactive elements keyboard-navigable
- Color contrast ratio ≥ 4.5:1 for all text
- Loading states announced via ARIA live regions
- Error messages always include text (not just color)
- Input field has proper label/placeholder

---

## 8. Loading & Empty States

| State | Display |
|-------|---------|
| Querying Pinecone + Gemini | Animated 3-dot typing indicator in bot bubble |
| Empty chat (first visit) | Suggested questions + welcome message |
| No documents ingested | Warning banner: "No documents have been uploaded yet." |
| Upload in progress | Progress bar with filename |
