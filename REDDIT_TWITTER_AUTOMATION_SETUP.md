# Reddit/Twitter Automation Setup Guide

## Overview
GrowthPilot now supports automated outreach on Reddit and Twitter (X.com). This guide explains how to set up API credentials and use the automation system.

## Reddit API Setup

### Step 1: Create Reddit App
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to the bottom and click "create another app..."
3. Fill in the form:
   - **name**: GrowthPilot
   - **App type**: Select "script"
   - **description**: AI-powered outreach automation
   - **about url**: (leave blank)
   - **redirect uri**: http://localhost:9000
4. Click "create app"

### Step 2: Get Reddit Credentials
After creating the app, you'll see:
- **Client ID**: The string under "personal use script" (14 characters)
- **Client Secret**: The "secret" field (27 characters)

### Step 3: Set Environment Variables
Add these to your Railway environment variables (or `.env` file for local development):

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=GrowthPilot/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

**Important**: Use your actual Reddit account username and password.

## Twitter API Setup (Already Configured)

According to your note, you've already set up Twitter API credentials. Verify these environment variables are set in Railway:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

## Using the Automation System

### 1. Create a Campaign
First, create a campaign through the frontend:
- Navigate to the Campaigns page
- Click "Create New Campaign"
- Fill in product details, target audience, etc.
- Save the campaign

### 2. Start Automation Job
On the Automation page:
1. **Select Platform**: Choose Reddit or Twitter
2. **Select Campaign**: Pick the campaign you want to promote
3. **Enter Keywords**: 
   - For Reddit: "stock investing individual investors"
   - For Twitter: "#investing stock market"
4. **Message Template**: Write your outreach message with placeholders:
   - `{username}` - Recipient's username
   - `{name}` - Recipient's display name
   - `{karma}` - Reddit karma (Reddit only)
   - `{subreddit}` - Subreddit name (Reddit only)
   - `{post_title}` - Post title (Reddit only)

### 3. Message Template Example

For Reddit:
```
Hi {username},

I noticed your expertise in stock investing at r/{subreddit}. Our AI-powered stock analysis platform helps individual investors make smarter decisions through real-time news analysis and personalized recommendations.

Would you be interested in a quick demo?
```

For Twitter:
```
Hi {name},

Saw your tweet about stock investing. Our AI platform helps individual investors analyze market trends and make data-driven decisions. 

Interested in trying it out?
```

### 4. Monitor Automation

The system will:
- Run every 1 minute checking for active jobs
- Search for users matching your keywords
- Send personalized messages (up to daily limit)
- Track success/error counts
- Reset daily counter at midnight UTC

**Daily Limits**:
- Free tier: 20 messages/day
- Premium tier: 40 messages/day (planned)

## Architecture

### Database Model: AutomationJob
```python
- platform: 'reddit' or 'twitter'
- search_keywords: Search query
- message_template: Message with placeholders
- status: 'active', 'paused', 'stopped', 'error'
- daily_limit: Messages per day
- total_sent_count: Total messages sent
- daily_sent_count: Messages sent today
- success_count: Successful sends
- error_count: Failed sends
```

### Background Scheduler
- Runs via APScheduler (AsyncIO)
- Checks for active jobs every 1 minute
- Processes Reddit and Twitter jobs separately
- Handles rate limiting and errors gracefully
- Resets daily counters at midnight UTC

### API Endpoints

#### POST /api/automation/jobs/start
Start a new automation job
```json
{
  "campaign_id": 1,
  "platform": "reddit",
  "search_keywords": "stock investing",
  "message_template": "Hi {username}...",
  "daily_limit": 20
}
```

#### GET /api/automation/jobs
Get all automation jobs for current user

#### GET /api/automation/jobs/{job_id}
Get specific job details

#### GET /api/automation/jobs/{job_id}/stats
Get job statistics (sent count, success rate, etc.)

#### PUT /api/automation/jobs/{job_id}/pause
Pause an active job

#### PUT /api/automation/jobs/{job_id}/resume
Resume a paused job

#### PUT /api/automation/jobs/{job_id}
Update job settings (keywords, template, daily limit)

#### DELETE /api/automation/jobs/{job_id}
Delete a job

## Testing

### Test Reddit Connection
```python
from app.services.reddit_automation import reddit_automation
await reddit_automation.test_connection()
```

### Test Twitter Connection
```python
from app.services.twitter_automation import twitter_automation
await twitter_automation.test_connection()
```

## Deployment Checklist

- [x] AutomationJob model created
- [x] API endpoints implemented
- [x] Reddit automation service updated
- [x] Twitter automation service updated
- [x] Background scheduler configured
- [x] Frontend platform selection added
- [x] Config.py updated with credentials
- [ ] **Set Reddit environment variables in Railway**
- [ ] Verify Twitter environment variables in Railway
- [ ] Deploy to Railway
- [ ] Test end-to-end automation

## Next Steps

1. **Set Reddit API credentials** in Railway environment variables
2. **Deploy to Railway** - Push changes to trigger deployment
3. **Test automation**:
   - Create a test campaign
   - Start automation job
   - Monitor logs for successful sends
   - Check database for interaction records

## Rate Limits & Best Practices

### Reddit
- Max 30 messages/day (platform limit)
- 10-second delay between messages
- Respect user preferences and subreddit rules

### Twitter
- Max 500 DMs/day (platform limit)
- 15-second delay between messages
- Only send to users who follow you or accept DMs from anyone

### Safety Features
- Automatic daily limit enforcement
- Rate limiting between messages
- Error tracking and retry logic
- User filtering (minimum karma/followers)
- Duplicate prevention

## Troubleshooting

### "Reddit API credentials not configured"
- Verify REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are set
- Check that values don't contain 'placeholder'

### "Cannot send DM to user"
- User may have DMs disabled
- User may have blocked your account
- You may have hit rate limits

### "Automation job in error state"
- Check job.error_message field
- Verify API credentials are correct
- Check platform API status pages

## Support

For issues or questions:
1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Test API connections using provided test functions
4. Review error messages in job.error_message field
