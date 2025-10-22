# GrowthPilot API Reference

Complete API documentation for all endpoints.

## Base URL

Development: `http://localhost:6000`
Production: `https://your-app.railway.app`

## Authentication

Currently, the API does not require authentication. In production, implement API key or JWT authentication.

## Health Check

### GET /health

Check API health status.

**Response**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

---

## Agent Endpoints

### POST /api/agents/icp

Generate Ideal Customer Profile from product information.

**Request Body**
```json
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool for retail investors",
  "target_audience_hint": "retail investors using TradingView",
  "locales": ["US", "SG", "IN"],
  "language_pref": "en"
}
```

**Response**
```json
{
  "icp": {
    "roles": ["Retail Investor", "Finance Blogger", "Day Trader"],
    "industries": ["Finance", "Fintech", "Investment Management"],
    "regions": ["US", "Singapore", "India"],
    "company_sizes": ["Individual", "SMB"],
    "pain_points": ["Finding reliable stock insights", "Time-consuming research"]
  },
  "keywords": {
    "root": ["stock investing", "AI investing", "stock analysis"],
    "long_tail": ["find trending stocks", "ai stock screener", "best stocks to buy"]
  }
}
```

---

### POST /api/agents/queries

Build platform-specific search queries.

**Request Body**
```json
{
  "icp": { /* ICP object from previous endpoint */ },
  "channels": ["linkedin", "reddit", "facebook"]
}
```

**Response**
```json
{
  "queries": {
    "linkedin": [
      "Retail Investor AND (stock analysis OR trading)",
      "\"Day Trader\" AND TradingView",
      "Finance Blogger AND stock market"
    ],
    "reddit": [
      "r/stocks + AI analysis",
      "r/investing + stock screener",
      "r/TradingView + automated trading"
    ],
    "facebook": [
      "Stock Trading Groups + investment tools",
      "Day Trading Communities + AI recommendations"
    ]
  }
}
```

---

### POST /api/agents/linkedin

Generate LinkedIn DM copy variants.

**Request Body**
```json
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool",
  "icp": { /* ICP object */ },
  "tone": "friendly",
  "cta": "free beta?",
  "channel": "linkedin"
}
```

**Response**
```json
{
  "variants": [
    {
      "variant": "A",
      "copy": "Hey [Name], noticed you're into stock analysis tools. Built an AI that spots trending stocks early using sentiment signals. Want to try the beta?",
      "tone": "value_first"
    },
    {
      "variant": "B",
      "copy": "Hi [Name], similar to other TradingView users, you might find this useful. My AI analyzes 1000+ stocks daily for early trends. Free beta?",
      "tone": "social_proof"
    }
  ]
}
```

---

### POST /api/agents/reddit

Generate Reddit comment copy variants.

**Request Body**
```json
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool",
  "icp": { /* ICP object */ },
  "tone": "friendly",
  "cta": "happy to share more",
  "channel": "reddit"
}
```

**Response**
```json
{
  "variants": [
    {
      "variant": "A",
      "copy": "I've been in a similar situation. Started using an AI tool called AIStockAnalyst that analyzes sentiment across 1000+ stocks. Helped me spot NVDA early last month. Happy to share more if helpful.",
      "tone": "conversational"
    }
  ]
}
```

---

### POST /api/agents/facebook

Generate Facebook post copy variants.

**Request Body**
```json
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool",
  "icp": { /* ICP object */ },
  "tone": "friendly",
  "cta": "Would love your thoughts!",
  "channel": "facebook"
}
```

**Response**
```json
{
  "variants": [
    {
      "variant": "A",
      "copy": "Hey everyone! I wanted to share something that's helped my stock picks. Been testing an AI tool that analyzes market sentiment across 1000+ stocks. Caught some great early movers! Would love your thoughts on AI in investing.",
      "tone": "friendly"
    }
  ]
}
```

---

### POST /api/agents/review

Review copy for platform policy compliance.

**Request Body**
```json
{
  "channel": "linkedin",
  "copy_variants": [
    {
      "variant": "A",
      "copy": "Your copy here..."
    }
  ]
}
```

**Response**
```json
{
  "status": "pass",
  "reasons": [],
  "revised": null
}
```

**Status Values**:
- `pass`: All variants compliant
- `fail`: Serious violations found
- `needs_revision`: Minor issues to fix

---

### POST /api/agents/analyze

Analyze prospect response and suggest follow-up.

**Request Body**
```json
{
  "prospect_reply": "Interesting! Tell me more about how it works.",
  "original_message": "Your original outreach message...",
  "channel": "linkedin"
}
```

**Response**
```json
{
  "classification": "question",
  "sentiment_score": 0.7,
  "suggested_followup": "Great question! Our AI analyzes real-time sentiment from social media, news, and market data to identify stocks gaining momentum. I can set up a quick demo if you're interested?",
  "reasoning": "Prospect is asking clarifying questions, showing genuine interest. Positive sentiment with specific information request."
}
```

**Classification Types**:
- `positive`: Interested, wants more information
- `neutral`: Acknowledges but non-committal
- `negative`: Not interested, dismissive
- `question`: Asking questions, seeking clarification
- `objection`: Expressing concerns or objections

---

### POST /api/agents/report

Generate campaign performance report.

**Request Body**
```json
{
  "campaign_id": 1,
  "metrics": {
    "linkedin": {
      "sends": 150,
      "replies": 12,
      "conversions": 3
    },
    "reddit": {
      "sends": 25,
      "replies": 8,
      "conversions": 2
    }
  }
}
```

**Response**
```json
{
  "summary": {
    "overall_performance": "Strong engagement across channels",
    "key_metrics": {
      "sends": 175,
      "reply_rate": 11.4,
      "conversion_rate": 2.9
    },
    "top_channel": "reddit",
    "concerns": []
  },
  "recommendations": [
    "Scale Reddit efforts - highest conversion rate at 8%",
    "Test variant B on LinkedIn - better engagement than A",
    "Increase sends during 9-11am PST window"
  ],
  "insights": [
    "Reddit performing 3x better than LinkedIn for conversions",
    "Question-based variants getting 40% more replies"
  ]
}
```

---

## Campaign Endpoints

### POST /api/campaigns/generate

Run full agent chain to generate complete campaign.

**Request Body**
```json
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool for retail investors",
  "target_audience_hint": "retail investors using TradingView",
  "locales": ["US", "SG", "IN"],
  "language_pref": "en",
  "channels": ["linkedin", "reddit", "facebook"],
  "tone": "friendly",
  "cta": "free beta?"
}
```

**Response**: Complete campaign object with all generated content.

---

### GET /api/campaigns

List all campaigns.

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response**
```json
[
  {
    "id": 1,
    "product_name": "AIStockAnalyst",
    "status": "draft",
    "created_at": "2025-10-20T10:00:00Z",
    // ... full campaign object
  }
]
```

---

### GET /api/campaigns/{campaign_id}

Get campaign by ID.

**Response**: Full campaign object.

---

### PUT /api/campaigns/{campaign_id}

Update campaign.

**Request Body**: Partial campaign object with fields to update.

**Response**: Updated campaign object.

---

### DELETE /api/campaigns/{campaign_id}

Delete campaign.

**Response**
```json
{
  "message": "Campaign deleted successfully"
}
```

---

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `404`: Resource not found
- `422`: Validation error
- `500`: Server error

---

## Rate Limits

No rate limits in development. Production should implement:
- 100 requests per minute per IP
- 1000 requests per hour per API key
