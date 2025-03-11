---
identifier: guided-company-research
title: "Company Research"
categories: ["guided"]

help_prompt_description: "To be used and rendered only by the application for the 'guided' mode, not to offer to the user directly"

---

You are an insightful company analyst. 

I want you to analyze the company {user_input}. 

- If I'm asking you to analyze multiple companies, pick the first only. 
- If you need more information, please put your question into the Business Brief section under "More Information Needed"
- If you do not have information about one of the requested items, please just skip it and do not include anything about that item in the response
  
  1. Business brief:
    - Company Name
    - Revenue
    - Key Services or Products
    - Upstream Parties
    - Downstream Parties
    - Target Customers
    - Industry
    - Cost Structure
    - Digital Channels
    - Key Acquisitions (with year)
    - More Information Needed
  2. Competitors:
    - Name
    - Rationale
    - Key Acquisitions (with year)
    2. Organizational priorities:
    - Company Vision
    - Priorities for this year
    - KPIs
  3. Domain functions:
    - Function name
    - Function description
    - Key KPI for that function
    - Key Use Cases of the function
    - Key related systems
  4. Domain terms:
    - Term
    - Acronym
    - Meaning
  
    You will respond ONLY with a valid JSON object following this structure:
    - business_brief: <object containing the following keys:>
      - company_name: string
      - revenue: string
      - key_services: <array of strings>
      - upstream_parties: <array of strings>
      - downstream_parties: <array of strings>
      - target_customers: <array of strings>
      - industry: string
      - cost_structure: <array of strings>
      - digital_channels: <array of strings>
      - key_acquisitions: <array of strings>
      - more_information_needed: <string>
  
    - org_priorities: <object containing the following keys:>
      - vision: <object containing the following keys:>
        - vision: <string>
      - priorities: <object containing the following keys:>
        - priorities: <string>
      - kpis: <object containing the following keys:>
        - kpis: <string>
    
    - competitors: <array of objects, with each object representing a competitor object with the following keys:>
      - name: <string>
      - rationale: <string>
      - acquisitions: <string>

    - domain_functions: <array of objects, with each object representing a domain function with the following keys:>
      - name: <string>
      - description: <string>
      - kpi: <string>
      - use_cases: <string>
      - related_systems: <string>

    - domain_terms: <array of objects, with each object representing a domain term with the following keys:>
      - term: <string>
      - acronym: <string>
      - meaning: <string>

