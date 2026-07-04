# Welcome Screen Implementation

## Overview

When a user logs in (via OTP verification or password login), they are shown a welcome screen that:
1. Displays their current location and date of sowing (DOS)
2. Allows them to update these values
3. Provides two action buttons with descriptions

## API Endpoints

### 1. Login/Verify OTP Response

Both `/api/auth/verify-otp` and `/api/auth/login` now return a `welcome_screen` object:

```json
{
  "success": true,
  "token": "...",
  "user_id": "...",
  "email": "...",
  "welcome_screen": {
    "show": true,
    "location": "Coventry, UK",
    "sowing_date": "2025-04-15",
    "has_existing_data": true,
    "options": {
      "predict_agent": {
        "button_text": "Continue to Predict Agent",
        "description": "Get AI-powered disease risk predictions based on weather conditions. The system analyzes temperature, humidity, precipitation, and other environmental factors to forecast the likelihood of Late Blight and Early Blight in your potato crop. Receive actionable recommendations and preventive measures tailored to your location and crop stage.",
        "action": "predict"
      },
      "chat": {
        "button_text": "Continue to Chat",
        "description": "Start a conversation with our agricultural assistant. Ask questions about potato farming, get advice on crop management, discuss disease symptoms, or update your field information. The AI assistant can help with general queries, diagnose diseases from images, or guide you through various farming challenges.",
        "action": "chat"
      }
    }
  }
}
```

### 2. Update Welcome Screen

**Endpoint:** `POST /api/welcome/update`

**Request Body:**
```json
{
  "location": "Coventry, UK",  // Optional - only if user wants to update
  "sowing_date": "2025-04-15",  // Optional - only if user wants to update
  "action": "predict"  // Required: "predict" or "chat"
}
```

**Response (for "predict" action):**
```json
{
  "success": true,
  "action": "predict",
  "message": "Redirecting to Predict Agent. Your location and sowing date have been saved.",
  "redirect": "/predict",
  "field_data": {
    "location": "Coventry, UK",
    "sowing_date": "2025-04-15"
  }
}
```

**Response (for "chat" action):**
```json
{
  "success": true,
  "action": "chat",
  "message": "Redirecting to Chat. Your location and sowing date have been saved.",
  "redirect": "/chat",
  "field_data": {
    "location": "Coventry, UK",
    "sowing_date": "2025-04-15"
  }
}
```

## Data Flow

### 1. User Login Flow

```
User logs in → API returns welcome_screen data
→ Frontend displays welcome screen
→ User can update location/DOS (optional)
→ User clicks button (predict or chat)
→ Frontend calls /api/welcome/update
→ API updates field in database
→ API returns redirect info
→ Frontend navigates to appropriate page
```

### 2. Predict Agent Data Flow

When user clicks "Continue to Predict Agent":
1. Location and DOS are saved to database via `/api/welcome/update`
2. User is redirected to predict page
3. When predict agent is called, it reads location and DOS from `user_profile.fields[0]`
4. The `BlightPredictionAgent._extract_user_data()` method automatically extracts:
   - `location` from `current_field.location`
   - `sowing_date` from `current_field.sowing_date`
   - Calculates `days_after_planting` from sowing_date
   - Detects `country` from location

### 3. Chat Agent Data Flow

When user clicks "Continue to Chat":
1. Location and DOS are saved to database via `/api/welcome/update`
2. User is redirected to chat page
3. Chat agent can reference location/DOS from user profile when needed
4. User can update field info through conversation

## Frontend Implementation

### Welcome Screen Component

```typescript
interface WelcomeScreenData {
  show: boolean;
  location: string;
  sowing_date: string;
  has_existing_data: boolean;
  options: {
    predict_agent: {
      button_text: string;
      description: string;
      action: "predict";
    };
    chat: {
      button_text: string;
      description: string;
      action: "chat";
    };
  };
}

// Component should:
// 1. Display current location and DOS (if available)
// 2. Allow editing location/DOS
// 3. Show two buttons with descriptions
// 4. Handle button clicks to call /api/welcome/update
// 5. Navigate based on response
```

### Example Usage

```typescript
// After login
const response = await login(email, otp);
if (response.welcome_screen?.show) {
  // Show welcome screen
  setWelcomeScreen(response.welcome_screen);
}

// When user clicks button
const handleAction = async (action: "predict" | "chat") => {
  const updateData = {
    location: editedLocation || welcomeScreen.location,
    sowing_date: editedSowingDate || welcomeScreen.sowing_date,
    action: action
  };
  
  const result = await fetch("/api/welcome/update", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(updateData)
  });
  
  const data = await result.json();
  // Navigate to data.redirect
  navigate(data.redirect);
};
```

## Database Updates

### Field Update Methods

Both SQLite and DynamoDB implementations now support:

1. **`update_field(field_id, user_id, location=None, sowing_date=None, area_hectares=None)`**
   - Updates specific fields without replacing entire record
   - Only updates provided fields

2. **`add_field(user_id, location, sowing_date, area_hectares=None, field_id=None)`**
   - Creates new field if `field_id` is None
   - Updates existing field if `field_id` is provided

## Key Points

1. **Location and DOS are automatically passed to Predict Agent**
   - No need to re-ask user
   - Data flows from welcome screen → database → predict agent

2. **User can update location/DOS on welcome screen**
   - Changes are saved before navigation
   - Predict agent uses updated values

3. **Two clear paths:**
   - **Predict Agent**: For disease risk prediction
   - **Chat**: For general conversation and assistance

4. **Memory is updated immediately**
   - Field data is saved to database
   - Available for all subsequent agent calls

## Testing

1. Login with new user (no existing data)
   - Welcome screen should show empty location/DOS
   - User can enter values and choose action

2. Login with existing user
   - Welcome screen should show saved location/DOS
   - User can update or keep existing values

3. Click "Continue to Predict Agent"
   - Location/DOS should be saved
   - Navigate to predict page
   - Predict agent should use saved location/DOS

4. Click "Continue to Chat"
   - Location/DOS should be saved
   - Navigate to chat page
   - Chat can reference saved location/DOS

