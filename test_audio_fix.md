# Audio Fix Testing Guide

## Quick Test Steps

### 1. Start the Application
```bash
python app.py
```

### 2. Upload a Prescription
1. Visit http://localhost:5000
2. Select a language (e.g., English)
3. Upload a prescription image (use `sample.jpg` if available)
4. Wait for processing

### 3. Test Audio Playback

#### Test A: Single Audio Playback
1. Click the speaker button (🔊) on the first medicine
2. **Expected**: 
   - Button immediately shows spinner
   - Button is disabled
   - After ~2 seconds, spinner changes to pause icon (⏸️)
   - Audio plays
   - When done, button returns to 🔊

#### Test B: Multiple Audio (Sequential)
1. Click speaker on Medicine 1
2. Wait for it to finish playing
3. Click speaker on Medicine 2
4. **Expected**: 
   - Medicine 2 plays normally
   - No overlap with Medicine 1

#### Test C: Multiple Audio (Interruption)
1. Click speaker on Medicine 1
2. While Medicine 1 is still loading or playing, click speaker on Medicine 2
3. **Expected**:
   - Medicine 1 audio STOPS immediately
   - Medicine 1 button resets to 🔊
   - Medicine 2 shows spinner
   - Medicine 2 loads and plays
   - Only Medicine 2 audio is heard

#### Test D: Rapid Clicking
1. Click speaker on Medicine 1
2. Immediately click speaker on Medicine 2
3. Immediately click speaker on Medicine 3
4. **Expected**:
   - Only Medicine 3 plays
   - All previous buttons reset to 🔊
   - No audio overlap

### 4. Test Error Handling

#### Test E: Network Error
1. Disconnect internet (if using external TTS)
2. Click speaker button
3. **Expected**:
   - Falls back to browser TTS
   - Button shows pause icon
   - Audio plays via browser

### 5. Visual State Verification

Check that buttons show correct states:

| State | Icon | Disabled | When |
|-------|------|----------|------|
| Ready | 🔊 | No | Initial state |
| Loading | Spinner | Yes | 0-2 seconds after click |
| Playing | ⏸️ | No | While audio plays |
| Error | 🔊 | No | After error |

## Success Criteria

✅ All tests pass  
✅ Only one audio plays at a time  
✅ Loading spinner shows immediately  
✅ Button states are correct  
✅ No console errors  
✅ Audio stops when new one starts  

## Common Issues

### Issue: Audio doesn't play
- Check browser console for errors
- Verify `/speak` endpoint is working
- Check `static/audio/` folder exists
- Verify API key is configured

### Issue: Multiple audios play
- This should be FIXED now
- If still happening, check browser console for JavaScript errors
- Verify only ONE `stopSpeech()` function exists

### Issue: Spinner doesn't show
- Check CSS for `.spinner-small` class
- Verify button element is being passed correctly
- Check browser console for errors

### Issue: Button doesn't reset
- Verify `currentSpeakingButton` is being set
- Check `stopSpeech()` is being called
- Look for JavaScript errors in console

## Browser Testing

Test in multiple browsers:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Production Testing

After deploying to Render:
1. Visit your production URL
2. Repeat all tests above
3. Verify audio files are being created in `/static/audio/`
4. Check Render logs for any errors

## Debugging Commands

### Check audio files
```bash
ls -la static/audio/
```

### Check app logs
```bash
# Local
python app.py

# Render
# Check logs in Render dashboard
```

### Test TTS endpoint directly
```bash
curl -X POST http://localhost:5000/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Test medicine","language":"English"}'
```

## Expected Response
```json
{
  "audio_url": "/static/audio/chat_xxxxx.mp3"
}
```

---

**Status**: Ready for testing after fix deployment
