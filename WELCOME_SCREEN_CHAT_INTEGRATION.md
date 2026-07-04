# Welcome Screen Chat Integration

## Overview

When a user creates a new chat, the welcome screen should appear in the chat interface itself, allowing them to:
1. View/update location and date of sowing (DOS)
2. Choose to continue with Predict Agent or Chat
3. Have their preferences saved automatically

## API Endpoints

### 1. Create New Conversation
**Endpoint:** `POST /api/conversations`

**Response (when location/DOS missing):**
```json
{
  "success": true,
  "conversation_id": "conv_123",
  "welcome_screen": {
    "show": true,
    "location": "",
    "sowing_date": "",
    "has_existing_data": false,
    "options": {
      "predict_agent": {
        "button_text": "Continue to Predict Agent",
        "description": "...",
        "action": "predict"
      },
      "chat": {
        "button_text": "Continue to Chat",
        "description": "...",
        "action": "chat"
      }
    }
  }
}
```

### 2. Get Conversation Messages (for new/empty chats)
**Endpoint:** `GET /api/conversations/{conversation_id}/messages`

**Response (when location/DOS missing and chat is empty):**
```json
{
  "success": true,
  "messages": [],
  "welcome_screen": {
    "show": true,
    "location": "",
    "sowing_date": "",
    "has_existing_data": false,
    "message": "Please provide your location and date of sowing to get started.",
    "options": {
      "predict_agent": {...},
      "chat": {...}
    }
  }
}
```

### 3. Update Welcome Screen
**Endpoint:** `POST /api/welcome/update`

**Request:**
```json
{
  "location": "Coventry, UK",
  "sowing_date": "2025-04-15",
  "action": "predict"  // or "chat"
}
```

**Response:**
```json
{
  "success": true,
  "action": "predict",
  "message": "Location and sowing date saved. You can now use the Predict Agent to get disease risk predictions.",
  "redirect": "/chat",
  "field_data": {
    "location": "Coventry, UK",
    "sowing_date": "2025-04-15"
  },
  "ready_for_predict": true
}
```

### 4. Check Welcome Screen Status
**Endpoint:** `GET /api/welcome/check`

Returns welcome screen data if location/DOS is missing.

## Frontend Implementation

### When Creating New Chat

```typescript
// 1. User clicks "NEW CHAT"
const createNewChat = async () => {
  const response = await fetch("/api/conversations", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title: null })
  });
  
  const data = await response.json();
  
  // 2. Check if welcome screen is needed
  if (data.welcome_screen?.show) {
    // Display welcome screen in chat area
    displayWelcomeScreen(data.welcome_screen, data.conversation_id);
  } else {
    // Show normal empty chat
    showEmptyChat(data.conversation_id);
  }
};
```

### Display Welcome Screen Component

```typescript
const displayWelcomeScreen = (welcomeData, conversationId) => {
  // Render welcome screen in chat area:
  // - Location input field (pre-filled if exists)
  // - Sowing date input field (pre-filled if exists)
  // - Two buttons with descriptions
  // - Save button to update preferences
};
```

### When User Clicks Button

```typescript
const handleWelcomeAction = async (action: "predict" | "chat", location, sowingDate) => {
  // 1. Save location and DOS
  const updateResponse = await fetch("/api/welcome/update", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      location: location,
      sowing_date: sowingDate,
      action: action
    })
  });
  
  const updateData = await updateResponse.json();
  
  // 2. Hide welcome screen
  hideWelcomeScreen();
  
  // 3. Show appropriate interface
  if (action === "predict") {
    // Show message suggesting user ask about disease risk
    showMessage("You can now ask about disease risk predictions. Try: 'What's the disease risk for my crop?'");
  } else {
    // Show normal chat interface
    showChatInterface();
  }
};
```

### When Loading Existing Chat

```typescript
// When loading a conversation
const loadConversation = async (conversationId) => {
  const response = await fetch(`/api/conversations/${conversationId}/messages`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  // If welcome screen is needed and chat is empty
  if (data.welcome_screen?.show && data.messages.length === 0) {
    displayWelcomeScreen(data.welcome_screen, conversationId);
  } else {
    // Display messages normally
    displayMessages(data.messages);
  }
};
```

## UI Flow

1. **User clicks "NEW CHAT"**
   - API creates conversation
   - API checks for location/DOS
   - If missing → Returns welcome_screen data

2. **Frontend displays welcome screen in chat area:**
   ```
   ┌─────────────────────────────────┐
   │  Welcome to Potato Shield       │
   │                                 │
   │  Location: [Coventry, UK    ]  │
   │  Date of Sowing: [2025-04-15]  │
   │                                 │
   │  ┌───────────────────────────┐ │
   │  │ Continue to Predict Agent │ │
   │  │ [Description text...]     │ │
   │  └───────────────────────────┘ │
   │                                 │
   │  ┌───────────────────────────┐ │
   │  │ Continue to Chat          │ │
   │  │ [Description text...]     │ │
   │  └───────────────────────────┘ │
   └─────────────────────────────────┘
   ```

3. **User updates location/DOS and clicks button**
   - Frontend calls `/api/welcome/update`
   - API saves data
   - Welcome screen disappears
   - Chat interface appears

4. **User can now chat or ask for predictions**
   - Location and DOS are automatically used by agents
   - No need to re-ask

## Key Points

- Welcome screen appears **in the chat area**, not as a separate page
- User can **edit location and DOS** before proceeding
- Two clear **action buttons** with descriptions
- Data is **saved automatically** when button is clicked
- After saving, user can **immediately use** predict agent or chat
- Welcome screen only shows for **new/empty chats** when location/DOS is missing

