import anthropic
import json
import os
import re
from datetime import datetime
from flask import Flask, request, jsonify
import requests

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
app = Flask(__name__)

class Agent:
    def __init__(self, name, system_prompt):
        self.name = name
        self.system_prompt = system_prompt
    
    def run(self, task, context=""):
        prompt = f"Context:\n{context}\n\nTask:\n{task}" if context else task
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def run_json(self, task, context=""):
        result = self.run(task + "\n\nRespond with valid JSON only.", context)
        try:
            return json.loads(result)
        except:
            match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', result)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            return {"raw": result}

# Research Agents
researcher = Agent("Researcher", """You are an expert market researcher. Find specific opportunities with real demand. Include exact platforms, price points, and buyer behaviors. Always return actionable, specific insights.""")

competitor_analyst = Agent("CompetitorAnalyst", """You analyze competitors to find gaps. Identify what sells, at what price, and what's missing. Be specific about opportunities to differentiate.""")

audience_profiler = Agent("AudienceProfiler", """You create detailed buyer personas. Include demographics, pain points, desires, and buying triggers. Use exact language your target audience uses.""")

# Product Agents
product_creator = Agent("ProductCreator", """You design digital products that sell. Create practical, immediately usable templates and guides. Focus on solving one specific problem completely.""")

copywriter = Agent("Copywriter", """You write sales copy that converts. Hook attention, agitate problems, present solutions, stack value. Write conversationally. Every sentence earns the next.""")

# Marketing Agents
content_creator = Agent("ContentCreator", """You create engaging social media content. Hook in first line, provide value, lead to product naturally. Optimize for each platform.""")

email_writer = Agent("EmailWriter", """You write email sequences that convert. Compelling subjects, hooks that grab, stories that sell. Clear single CTAs. Build trust before pitching.""")

lead_generator = Agent("LeadGenerator", """You create lead magnets and funnels. Design quick wins that create desire for main product. Map the journey from stranger to buyer.""")

# Sales Agents
lead_qualifier = Agent("LeadQualifier", """You qualify leads and personalize outreach. Score intent, recommend actions, write personalized responses. Be helpful, not pushy.""")

sales_closer = Agent("SalesCloser", """You handle sales conversations. Identify needs, match benefits, handle objections, ask for sale. Solve problems, don't pressure.""")

support_agent = Agent("SupportAgent", """You handle customer support. Resolve issues quickly, turn complaints into opportunities. Be empathetic and solution-focused.""")

outreach_agent = Agent("OutreachAgent", """You find and engage potential customers. Research where they hang out, craft personalized messages. Build relationships before selling.""")

# Data Storage
data = {
    "config": {},
    "research": {},
    "product": {},
    "marketing": {},
    "leads": [],
    "customers": [],
    "revenue": 0,
    "outreach": []
}

# Core Functions
def research_market(niche):
    market = researcher.run_json(f"""Research market for: {niche}

Return JSON:
{{
    "market_size": "demand level",
    "platforms": [{{"name": "where buyers are", "activity": "high/medium/low"}}],
    "communities": [{{"name": "subreddit/group", "pain_points": ["problems"]}}],
    "pricing": {{"low": "$X", "mid": "$X", "high": "$X", "sweet_spot": "$X"}},
    "demand_signals": ["evidence"],
    "buyer_urgency": "why buy now"
}}""")
    
    competitors = competitor_analyst.run_json(f"""Analyze competitors in: {niche}

Return JSON:
{{
    "top_products": [{{"name": "product", "price": "$X", "strengths": [], "weaknesses": [], "sales_level": "high/medium/low"}}],
    "gaps": [{{"gap": "unmet need", "opportunity": "how to fill"}}],
    "differentiation": ["ways to stand out"]
}}""")
    
    audience = audience_profiler.run_json(f"""Create buyer persona for: {niche}

Return JSON:
{{
    "persona": {{
        "name": "fictional name",
        "occupation": "job",
        "biggest_problem": "main frustration",
        "desired_outcome": "what they want",
        "fears": ["concerns"],
        "buying_triggers": ["what makes them buy"],
        "objections": ["hesitations"],
        "hangouts": ["where online"],
        "language": ["phrases they use"]
    }}
}}""")
    
    return {"market": market, "competitors": competitors, "audience": audience}

def create_product(niche, research):
    product = product_creator.run_json(f"""Create product for: {niche}
Research: {json.dumps(research, indent=2)}

Return JSON:
{{
    "name": "product name",
    "tagline": "one-line hook",
    "format": "PDF/Notion/etc",
    "promise": "main transformation",
    "sections": [{{"title": "section", "contents": ["items"], "result": "outcome"}}],
    "bonuses": [{{"name": "bonus", "value": "$X", "description": "what"}}],
    "time_to_result": "how fast"
}}""")
    
    copy = copywriter.run_json(f"""Write sales copy for: {json.dumps(product, indent=2)}
Audience: {json.dumps(research.get('audience', {}), indent=2)}

Return JSON:
{{
    "headline": "main headline",
    "subheadline": "supporting line",
    "hook": "opening paragraph",
    "problem": "pain paragraphs",
    "solution": "product intro",
    "included": [{{"item": "feature", "benefit": "why matters"}}],
    "bonuses": [{{"name": "bonus", "value": "$X"}}],
    "faq": [{{"q": "question", "a": "answer"}}],
    "guarantee": "risk reversal",
    "cta": "call to action"
}}""")
    
    pricing = researcher.run_json(f"""Set pricing for: {json.dumps(product, indent=2)}
Competitors: {json.dumps(research.get('competitors', {}), indent=2)}

Return JSON:
{{
    "price": 37,
    "launch_price": 27,
    "value_stack": [{{"item": "included", "value": "$X"}}],
    "total_value": "$XXX"
}}""")
    
    return {"product": product, "copy": copy, "pricing": pricing}

def create_marketing(product, research):
    lead_magnet = lead_generator.run_json(f"""Create lead magnet for: {json.dumps(product.get('product', {}), indent=2)}

Return JSON:
{{
    "name": "lead magnet name",
    "format": "checklist/template/guide",
    "promise": "what they get",
    "contents": ["whats inside"],
    "landing_page": {{
        "headline": "main headline",
        "bullets": ["benefits"],
        "cta": "button text"
    }}
}}""")
    
    emails = email_writer.run_json(f"""Write 5-email welcome sequence.
Lead magnet: {json.dumps(lead_magnet, indent=2)}
Product: {json.dumps(product.get('product', {}), indent=2)}
Price: ${product.get('pricing', {}).get('launch_price', 27)}

Return JSON:
{{
    "emails": [
        {{
            "number": 1,
            "send": "immediately",
            "purpose": "deliver lead magnet",
            "subject": "subject line",
            "body": "full email body",
            "cta": "call to action"
        }}
    ]
}}""")
    
    social = content_creator.run_json(f"""Create 14 days of social content.
Product: {json.dumps(product.get('product', {}), indent=2)}
Audience: {json.dumps(research.get('audience', {}), indent=2)}

Mix: 60% value, 20% story/engagement, 20% promo

Return JSON:
{{
    "posts": [
        {{
            "day": 1,
            "platform": "twitter",
            "type": "value",
            "hook": "first line",
            "body": "full post",
            "cta": "call to action",
            "hashtags": ["tags"]
        }}
    ]
}}""")
    
    return {"lead_magnet": lead_magnet, "emails": emails, "social": social}

def create_outreach(niche, research):
    return outreach_agent.run_json(f"""Create outreach plan for: {niche}
Target: {json.dumps(research.get('audience', {}), indent=2)}

Return JSON:
{{
    "daily_actions": [
        {{
            "platform": "twitter/linkedin/reddit",
            "action": "what to do",
            "time": "minutes needed",
            "script": "what to say"
        }}
    ],
    "communities": [
        {{
            "name": "specific place",
            "rules": "how to engage",
            "value_post": "example post",
            "soft_pitch": "how to mention product"
        }}
    ],
    "dm_templates": [
        {{
            "context": "when to use",
            "message": "template",
            "follow_up": "if no response"
        }}
    ],
    "cold_outreach": [
        {{
            "target": "who to reach",
            "where": "how to find them",
            "approach": "first message",
            "value_offer": "free thing to give"
        }}
    ]
}}""")

def find_leads(niche, count=10):
    return outreach_agent.run_json(f"""Find {count} specific leads for: {niche}

Look for people who:
- Are discussing this problem
- Asked for help recently
- Showed frustration with current solutions

Return JSON:
{{
    "leads": [
        {{
            "type": "twitter/reddit/linkedin",
            "identifier": "username or post description",
            "signal": "why theyre a lead",
            "pain_point": "their specific problem",
            "approach": "personalized message",
            "urgency": "hot/warm/cold"
        }}
    ],
    "search_queries": [
        {{
            "platform": "where to search",
            "query": "exact search terms",
            "why": "what this finds"
        }}
    ]
}}""")

def process_lead(lead_data, product):
    return lead_qualifier.run_json(f"""Qualify this lead: {json.dumps(lead_data, indent=2)}
Product: {json.dumps(product, indent=2)}

Return JSON:
{{
    "score": 8,
    "intent": "hot/warm/cold",
    "response": "personalized message to send",
    "follow_up": [{{"when": "timing", "action": "what to do"}}],
    "notes": "observations"
}}""")

def handle_inquiry(message, product):
    return sales_closer.run_json(f"""Handle this sales inquiry: "{message}"
Product: {json.dumps(product, indent=2)}

Return JSON:
{{
    "intent": "buy/question/objection",
    "response": "your reply",
    "objections": ["detected concerns"],
    "next_action": "what to do next",
    "close_ready": false
}}""")

def handle_support(message, customer=None):
    return support_agent.run_json(f"""Handle support request: "{message}"
Customer: {json.dumps(customer or {}, indent=2)}

Return JSON:
{{
    "category": "question/issue/refund",
    "response": "helpful reply",
    "resolution": "how this resolves it",
    "follow_up": false
}}""")

# API Endpoints
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "POST /build": "Build complete business",
            "GET /payhip-copy": "Get product description",
            "GET /email-sequence": "Get email sequence",
            "GET /social-posts": "Get all social posts",
            "GET /daily-post": "Get today's post",
            "POST /find-leads": "Find leads to contact",
            "GET /outreach-plan": "Get outreach strategy",
            "POST /process-lead": "Qualify a lead",
            "POST /inquiry": "Handle sales question",
            "POST /support": "Handle support request",
            "POST /webhook/payhip": "Payhip sales webhook",
            "POST /webhook/stripe": "Stripe webhook",
            "GET /stats": "View statistics",
            "GET /assets": "View all data"
        }
    })

@app.route("/build", methods=["POST"])
def build():
    global data
    req = request.json or {}
    niche = req.get("niche", "AI prompts for solopreneurs")
    
    print(f"Building: {niche}")
    
    print("1/5 Research...")
    data["research"] = research_market(niche)
    
    print("2/5 Product...")
    data["product"] = create_product(niche, data["research"])
    
    print("3/5 Marketing...")
    data["marketing"] = create_marketing(data["product"], data["research"])
    
    print("4/5 Outreach...")
    data["outreach_plan"] = create_outreach(niche, data["research"])
    
    print("5/5 Leads...")
    data["initial_leads"] = find_leads(niche, 10)
    
    data["config"] = {"niche": niche, "created": datetime.now().isoformat()}
    
    with open("business.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Done!")
    
    return jsonify({
        "status": "complete",
        "product": data["product"].get("product", {}).get("name"),
        "price": data["product"].get("pricing", {}).get("launch_price"),
        "leads_found": len(data.get("initial_leads", {}).get("leads", [])),
        "next_steps": [
            "GET /payhip-copy - Copy to your store",
            "GET /find-leads - Contact these people",
            "GET /daily-post - Post this today",
            "GET /outreach-plan - Follow this daily"
        ]
    })

@app.route("/research", methods=["GET", "POST"])
def research_endpoint():
    global data
    if request.method == "POST":
        niche = (request.json or {}).get("niche", "")
        data["research"] = research_market(niche)
    return jsonify(data.get("research", {}))

@app.route("/find-leads", methods=["POST"])
def find_leads_endpoint():
    global data
    req = request.json or {}
    niche = req.get("niche", data.get("config", {}).get("niche", ""))
    count = req.get("count", 10)
    leads = find_leads(niche, count)
    data["outreach"].append({"time": datetime.now().isoformat(), "leads": leads})
    return jsonify(leads)

@app.route("/outreach-plan")
def outreach_endpoint():
    return jsonify(data.get("outreach_plan", {}))

@app.route("/process-lead", methods=["POST"])
def process_lead_endpoint():
    global data
    lead_data = request.json or {}
    result = process_lead(lead_data, data.get("product", {}))
    data["leads"].append({
        **lead_data,
        "score": result.get("score", 0),
        "processed": datetime.now().isoformat()
    })
    return jsonify(result)

@app.route("/inquiry", methods=["POST"])
def inquiry_endpoint():
    message = (request.json or {}).get("message", "")
    return jsonify(handle_inquiry(message, data.get("product", {})))

@app.route("/support", methods=["POST"])
def support_endpoint():
    req = request.json or {}
    return jsonify(handle_support(req.get("message", ""), req.get("customer")))

@app.route("/payhip-copy")
@app.route("/gumroad-copy")
def product_copy():
    copy = data.get("product", {}).get("copy", {})
    pricing = data.get("product", {}).get("pricing", {})
    
    if not copy:
        return "Build first: POST /build with {\"niche\": \"your niche\"}", 400
    
    text = f"""# {copy.get('headline', 'Product')}

## {copy.get('subheadline', '')}

{copy.get('hook', '')}

---

## The Problem

{copy.get('problem', '')}

---

## The Solution

{copy.get('solution', '')}

---

## What You Get:

"""
    for item in copy.get('included', []):
        text += f"✅ **{item.get('item', '')}** - {item.get('benefit', '')}\n\n"
    
    text += "\n## BONUSES:\n\n"
    for bonus in copy.get('bonuses', []):
        text += f"🎁 **{bonus.get('name', '')}** ({bonus.get('value', '')})\n\n"
    
    text += f"""
---

## 100% Money-Back Guarantee

{copy.get('guarantee', '30-day no questions asked refund')}

---

## FAQ

"""
    for faq in copy.get('faq', []):
        text += f"**Q: {faq.get('q', '')}**\nA: {faq.get('a', '')}\n\n"
    
    text += f"""
---

**Launch Price: ${pricing.get('launch_price', 27)}** (Regular ${pricing.get('price', 37)})

{copy.get('cta', 'Get Instant Access')}
"""
    return text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/email-sequence")
def email_sequence():
    emails = data.get("marketing", {}).get("emails", {}).get("emails", [])
    
    if not emails:
        return "Build first", 400
    
    text = "# Email Sequence\n\n"
    for e in emails:
        text += f"""## Email {e.get('number', '')}
**Send:** {e.get('send', '')}
**Purpose:** {e.get('purpose', '')}
**Subject:** {e.get('subject', '')}

{e.get('body', '')}

**CTA:** {e.get('cta', '')}

---

"""
    return text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/social-posts")
def social_posts():
    posts = data.get("marketing", {}).get("social", {}).get("posts", [])
    
    if not posts:
        return "Build first", 400
    
    text = "# Social Content Calendar\n\n"
    for p in posts:
        text += f"""## Day {p.get('day', '')} - {p.get('platform', '').upper()}
**Type:** {p.get('type', '')}

**Hook:** {p.get('hook', '')}

{p.get('body', '')}

"""
        if p.get('cta'):
            text += f"**CTA:** {p.get('cta', '')}\n"
        if p.get('hashtags'):
            text += f"**Tags:** {' '.join(p.get('hashtags', []))}\n"
        text += "\n---\n\n"
    
    return text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/daily-post")
def daily_post():
    posts = data.get("marketing", {}).get("social", {}).get("posts", [])
    
    if not posts:
        return jsonify({"error": "Build first"})
    
    created = data.get("config", {}).get("created", datetime.now().isoformat())
    try:
        start = datetime.fromisoformat(created.split('.')[0])
    except:
        start = datetime.now()
    
    days = (datetime.now() - start).days
    post_index = days % len(posts)
    
    return jsonify({
        "day": days + 1,
        "post": posts[post_index]
    })

@app.route("/webhook/payhip", methods=["POST"])
def payhip_webhook():
    global data
    sale = request.json or {}
    
    customer = {
        "email": sale.get("buyer_email") or sale.get("email"),
        "price": sale.get("total") or sale.get("price"),
        "source": "payhip",
        "time": datetime.now().isoformat()
    }
    
    data["customers"].append(customer)
    try:
        data["revenue"] += float(customer.get("price", 0) or 0)
    except:
        pass
    
    print(f"💰 SALE: {customer['email']} - ${customer.get('price')}")
    
    return jsonify({"status": "processed", "customer": customer})

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    global data
    event = request.json or {}
    
    if event.get("type") == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        customer = {
            "email": session.get("customer_email"),
            "price": session.get("amount_total", 0) / 100,
            "source": "stripe",
            "time": datetime.now().isoformat()
        }
        data["customers"].append(customer)
        data["revenue"] += customer.get("price", 0)
        print(f"💰 STRIPE: {customer['email']} - ${customer['price']}")
    
    return jsonify({"status": "processed"})

@app.route("/webhook/gumroad", methods=["POST"])
def gumroad_webhook():
    global data
    sale = request.form.to_dict() or request.json or {}
    
    customer = {
        "email": sale.get("email"),
        "price": sale.get("price"),
        "source": "gumroad",
        "time": datetime.now().isoformat()
    }
    
    data["customers"].append(customer)
    try:
        data["revenue"] += float(sale.get("price", 0) or 0)
    except:
        pass
    
    return jsonify({"status": "processed"})

@app.route("/stats")
def stats():
    return jsonify({
        "product": data.get("product", {}).get("product", {}).get("name", "Not built"),
        "price": data.get("product", {}).get("pricing", {}).get("launch_price", 0),
        "leads": len(data.get("leads", [])),
        "customers": len(data.get("customers", [])),
        "revenue": data.get("revenue", 0),
        "created": data.get("config", {}).get("created", "Not built yet")
    })

@app.route("/assets")
def assets():
    return jsonify(data)

@app.route("/leads")
def get_leads():
    return jsonify({
        "leads": data.get("leads", []),
        "initial_leads": data.get("initial_leads", {}),
        "outreach_history": data.get("outreach", [])
    })

@app.route("/customers")
def get_customers():
    return jsonify({
        "customers": data.get("customers", []),
        "count": len(data.get("customers", [])),
        "revenue": data.get("revenue", 0)
    })

# Load existing data on startup
if __name__ == "__main__":
    try:
        with open("business.json", "r") as f:
            data = json.load(f)
            print("Loaded existing data")
    except:
        print("Starting fresh")
    
    port = int(os.environ.get("PORT", 8080))
    print(f"Running on port {port}")
    app.run(host="0.0.0.0", port=port)