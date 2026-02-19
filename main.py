"""
SDR Agent - Main Entry Point

This is a simple Sales Development Representative AI agent that:
1. Researches companies
2. Qualifies leads
3. Identifies decision makers
4. Generates personalized outreach emails

SUPPORTS MULTIPLE AI PROVIDERS:
- Google Gemini (FREE - 2M tokens/day)
- Groq (FREE - fast inference)
- Anthropic Claude (PAID - best quality)
"""
import sys
from agent.core.graph import run_sdr_agent
import agent.infra.config as config


def print_results(state):
    """Print the final results in a nice format"""
    print("\n" + "="*60)
    print("📋 FINAL RESULTS")
    print("="*60)
    
    print(f"\n🏢 Company: {state['company_name']}")
    print(f"📊 Qualification Score: {state['qualification_score']}/10")
    print(f"✅ Status: {state['status']}")
    
    if state['status'] == 'disqualified':
        print("\n❌ This lead was disqualified.")
        print("\nReasoning:")
        print(state['qualification_reasoning'])
        return
    
    print("\n" + "-"*60)
    print("🔍 COMPANY RESEARCH")
    print("-"*60)
    print(state['company_research'])
    
    print("\n" + "-"*60)
    print("👔 DECISION MAKERS")
    print("-"*60)
    for i, title in enumerate(state['decision_maker_titles'], 1):
        print(f"{i}. {title}")
    
    # Phase 2 Results
    if state.get('contacts'):
        print("\n" + "-"*60)
        print("📇 CONTACTS FOUND")
        print("-"*60)
        for i, contact in enumerate(state['contacts'], 1):
            print(f"\n{i}. {contact.get('name', 'Unknown')}")
            print(f"   Title: {contact.get('title', 'N/A')}")
            print(f"   Email: {contact.get('email', 'N/A')}")
            if contact.get('linkedin'):
                print(f"   LinkedIn: {contact.get('linkedin')}")
    
    if state.get('emails_sent'):
        print("\n" + "-"*60)
        print("📧 EMAILS SENT")
        print("-"*60)
        for result in state['emails_sent']:
            if result.get('success'):
                print(f"✅ {result['to_email']}: {result['subject']}")
            else:
                print(f"❌ {result.get('to_email', 'Unknown')}: {result.get('error')}")
    
    if state.get('linkedin_requests'):
        print("\n" + "-"*60)
        print("💼 LINKEDIN OUTREACH")
        print("-"*60)
        for result in state['linkedin_requests']:
            if result.get('success'):
                print(f"✅ Sent {result.get('requests_sent', 0)} connection requests")
                print(f"   Found {result.get('profiles_found', 0)} profiles")
            else:
                print(f"⚠️ {result.get('error', 'Unknown error')}")
    
    if state.get('sheets_logged'):
        print("\n" + "-"*60)
        print("📊 TRACKING")
        print("-"*60)
        print("✅ Logged to Google Sheets")
    
    print("\n" + "-"*60)
    print("✉️ OUTREACH EMAIL TEMPLATE")
    print("-"*60)
    print(state['outreach_email'])
    print("\n" + "="*60)


def check_api_keys():
    """Check if required API keys are configured"""
    provider = config.AI_PROVIDER
    
    # Check AI provider key
    if provider == "anthropic" and not config.ANTHROPIC_API_KEY:
        return False, "ANTHROPIC_API_KEY not found. Get it at: https://console.anthropic.com/"
    elif provider == "google" and not config.GOOGLE_API_KEY:
        return False, "GOOGLE_API_KEY not found. Get it FREE at: https://makersuite.google.com/app/apikey"
    elif provider == "groq" and not config.GROQ_API_KEY:
        return False, "GROQ_API_KEY not found. Get it FREE at: https://console.groq.com/"
    
    # Check search key
    if not config.TAVILY_API_KEY:
        print("⚠️ Warning: TAVILY_API_KEY not found")
        print("Web search will not work without it.")
        print("Get a FREE API key at: https://tavily.com/\n")
    
    return True, None


def main():
    """Main function"""
    
    print("\n🤖 SDR Agent - Sales Development Representative AI")
    print(f"Using: {config.AI_PROVIDER.upper()} ({config.MODELS[config.AI_PROVIDER]})")
    print("="*60)
    
    # Check API keys
    keys_ok, error = check_api_keys()
    if not keys_ok:
        print(f"\n❌ Error: {error}")
        print("\nCreate a .env file with:")
        if config.AI_PROVIDER == "google":
            print("GOOGLE_API_KEY=your_key_here")
        elif config.AI_PROVIDER == "groq":
            print("GROQ_API_KEY=your_key_here")
        else:
            print("ANTHROPIC_API_KEY=your_key_here")
        print("TAVILY_API_KEY=your_key_here")
        sys.exit(1)
    
    # Get company name from user
    if len(sys.argv) > 1:
        company_name = " ".join(sys.argv[1:])
    else:
        company_name = input("\nEnter company name to research: ").strip()
    
    if not company_name:
        print("❌ No company name provided. Exiting.")
        sys.exit(1)
    
    # Run the agent
    try:
        final_state = run_sdr_agent(company_name)
        print_results(final_state)
        
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()