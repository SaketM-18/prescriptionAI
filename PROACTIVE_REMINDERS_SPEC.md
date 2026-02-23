# 🔔 Proactive Reminder System - Specification

## Current Problem

**Existing Alarm Feature:**
- ✅ Opens native Clock app (Android)
- ✅ Shows instructions (iOS)
- ❌ Requires manual setup (user must click "Set Alarm")
- ❌ Only works on results page
- ❌ Not persistent
- ❌ No automatic reminders
- ❌ No missed dose tracking

**Result:** Users forget to set alarms, miss doses

---

## Solution: Automatic Proactive Reminder System

### Features

#### 1. **Automatic Reminder Setup** ✅
- Automatically create reminders when prescription is scanned
- No manual action required
- Persistent across app restarts
- Works even if app is closed

#### 2. **Multiple Reminder Types** ✅
- Push Notifications (smartphones)
- Browser Notifications (desktop)
- Persistent Notifications (Android)
- Badge notifications (iOS)

#### 3. **Smart Scheduling** ✅
- Based on dosage pattern (1-0-1, 1-1-1, etc.)
- Respects timing (before/after food)
- Adjusts for user's timezone
- Skips if already taken

#### 4. **Missed Dose Tracking** ✅
- Detects missed doses
- Sends follow-up reminders
- Tracks adherence
- Shows streak

#### 5. **Easy Management** ✅
- View all reminders
- Snooze for 15/30/60 minutes
- Mark as taken
- Disable specific reminders

---

## Implementation Plan

### Phase 1: Enhanced Browser Notifications (Week 1-2)

#### A. Automatic Reminder Creation
```javascript
// When prescription is processed
function autoCreateReminders(medicines) {
    medicines.forEach(med => {
        const schedule = parseDosage(med.dosage);
        schedule.forEach(time => {
            createReminder({
                medicine: med.name,
                time: time,
                timing: med.timing,
                duration: med.duration
            });
        });
    });
}
```

#### B. Persistent Storage
```javascript
// Store in localStorage
const reminders = {
    "reminder-1": {
        id: "reminder-1",
        medicine: "Paracetamol 500mg",
        time: "08:00",
        timing: "After food",
        days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        enabled: true,
        lastTaken: null,
        streak: 5
    }
}
```

#### C. Background Service Worker
```javascript
// Service worker for persistent notifications
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    // Open app and mark as taken
    event.waitUntil(
        clients.openWindow('/?action=mark_taken&id=' + event.notification.tag)
    );
});
```

### Phase 2: Push Notifications (Week 3-4)

#### A. Web Push API
```javascript
// Request permission
Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
        subscribeUserToPush();
    }
});

// Subscribe to push service
function subscribeUserToPush() {
    navigator.serviceWorker.ready.then(registration => {
        registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
        });
    });
}
```

#### B. Backend Push Service
```python
# app.py
from pywebpush import webpush, WebPushException

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    subscription = request.json
    # Store subscription in database/localStorage
    return jsonify({'success': True})

def send_reminder(subscription, reminder):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps({
                'title': 'Medicine Reminder',
                'body': f"Time to take {reminder['medicine']}",
                'icon': '/static/icon.png',
                'badge': '/static/badge.png'
            }),
            vapid_private_key=private_key,
            vapid_claims={"sub": "mailto:support@example.com"}
        )
    except WebPushException as ex:
        print(f"Push failed: {ex}")
```

### Phase 3: SMS Reminders (Week 5-6)

#### A. Twilio Integration
```python
from twilio.rest import Client

def send_sms_reminder(phone, medicine, time):
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=f"⏰ Time to take {medicine}. Reply DONE when taken.",
        from_='+1234567890',
        to=phone
    )
    
    return message.sid
```

#### B. Two-Way SMS
```python
@app.route('/sms/webhook', methods=['POST'])
def sms_webhook():
    body = request.form.get('Body', '').upper()
    from_number = request.form.get('From')
    
    if body == 'DONE':
        mark_dose_taken(from_number)
        return respond("✅ Marked as taken. Great job!")
    elif body == 'SKIP':
        skip_dose(from_number)
        return respond("Dose skipped. Remember to take next dose.")
    elif body == 'HELP':
        return respond("Reply DONE when taken, SKIP to skip, STOP to disable.")
```

---

## UI Components

### 1. Reminder Dashboard
```
┌─────────────────────────────────┐
│  📅 Today's Reminders           │
├─────────────────────────────────┤
│ ☀️ 8:00 AM - Morning            │
│ Paracetamol 500mg               │
│ After food                      │
│ [✓ Taken] [Snooze] [Skip]      │
├─────────────────────────────────┤
│ 🌤️ 1:00 PM - Afternoon          │
│ Vitamin D3                      │
│ After food                      │
│ [Take Now] [Snooze] [Skip]     │
├─────────────────────────────────┤
│ 🌙 9:00 PM - Night              │
│ Paracetamol 500mg               │
│ After food                      │
│ [Remind Me] [Snooze] [Skip]    │
└─────────────────────────────────┘

Streak: 🔥 5 days
Adherence: 95%
```

### 2. Notification UI
```
┌─────────────────────────────────┐
│ 💊 Medicine Reminder            │
├─────────────────────────────────┤
│ Time to take:                   │
│ Paracetamol 500mg               │
│                                 │
│ After food                      │
│                                 │
│ [✓ Taken] [Snooze 15min]       │
└─────────────────────────────────┘
```

### 3. Settings Panel
```
┌─────────────────────────────────┐
│  ⚙️ Reminder Settings            │
├─────────────────────────────────┤
│ Notification Type:              │
│ ○ Push Notifications            │
│ ○ Browser Notifications         │
│ ● SMS (Feature phones)          │
│                                 │
│ Phone Number:                   │
│ [+91 98765 43210]              │
│                                 │
│ Snooze Duration:                │
│ [15 min ▼]                      │
│                                 │
│ Reminder Sound:                 │
│ [Gentle Bell ▼]                 │
│                                 │
│ Quiet Hours:                    │
│ 10:00 PM - 7:00 AM             │
│                                 │
│ [Save Settings]                 │
└─────────────────────────────────┘
```

---

## Technical Architecture

### Client-Side (Browser)
```
┌─────────────────────────────────┐
│  Reminder Manager               │
│  ├─ Create reminders            │
│  ├─ Schedule notifications      │
│  ├─ Track adherence             │
│  └─ Sync with server            │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Service Worker                 │
│  ├─ Background notifications    │
│  ├─ Offline support             │
│  └─ Push message handling       │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  localStorage                   │
│  ├─ Reminder data               │
│  ├─ Adherence history           │
│  └─ User preferences            │
└─────────────────────────────────┘
```

### Server-Side (Flask)
```
┌─────────────────────────────────┐
│  Push Notification Service      │
│  ├─ Web Push API                │
│  ├─ SMS via Twilio              │
│  └─ Scheduled jobs              │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Reminder Scheduler             │
│  ├─ Cron jobs                   │
│  ├─ Queue management            │
│  └─ Retry logic                 │
└─────────────────────────────────┘
```

---

## Implementation Steps

### Week 1: Basic Auto-Reminders
1. Parse dosage and create reminder schedule
2. Store reminders in localStorage
3. Show reminder dashboard
4. Basic browser notifications

### Week 2: Enhanced Notifications
1. Service worker for persistent notifications
2. Notification actions (Taken, Snooze, Skip)
3. Missed dose detection
4. Adherence tracking

### Week 3: Push Notifications
1. Web Push API integration
2. VAPID keys setup
3. Backend push service
4. Subscription management

### Week 4: SMS Integration
1. Twilio account setup
2. SMS sending service
3. Two-way SMS handling
4. Phone number management

### Week 5: Polish & Testing
1. UI improvements
2. Settings panel
3. User testing
4. Bug fixes

### Week 6: Deployment
1. Production setup
2. Monitoring
3. Documentation
4. User onboarding

---

## Success Metrics

### Before (Current State):
- Adherence: 40%
- Users setting alarms: 10%
- Missed doses: 60%

### After (Target):
- Adherence: 85%
- Users with active reminders: 90%
- Missed doses: 15%

---

## Cost Estimate

### SMS Costs (Twilio):
- ₹0.50 per SMS
- Average: 3 SMS/day per user
- Monthly: ₹45 per user
- 1000 users: ₹45,000/month

### Push Notifications:
- Free (Web Push API)
- No ongoing costs

### Recommendation:
- Start with free push notifications
- Add SMS for premium users
- Or SMS for feature phone users only

---

## Next Steps

1. **Review this spec** - Approve approach
2. **Choose implementation** - Push vs SMS vs Both
3. **Start Week 1** - Basic auto-reminders
4. **Test with users** - Get feedback
5. **Iterate** - Improve based on usage

---

**Status:** Ready to implement  
**Timeline:** 6 weeks  
**Impact:** 85% adherence (from 40%)
