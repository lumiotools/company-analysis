import os
from typing import List
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Overview(BaseModel):
    vision_statement: str
    key_value_proposition: str
    strategic_initiatives: List[str]


class EfficiencyMetrics(BaseModel):
    gross_margin: float
    net_profit_margin: float


class OperationalMetrics(BaseModel):
    key_products: List[str]
    deployment_scale: str
    efficiency_metrics: EfficiencyMetrics
    market_position: str


class FinancialHighlights(BaseModel):
    total_revenues: float
    gross_profit: float
    net_income: float
    total_assets: float
    total_liabilities: float
    stockholders_equity: float


class CapitalAllocation(BaseModel):
    name: str
    value: float

class InvestmentRequirements(BaseModel):
    amount_required: float
    funding_sources: List[str]
    capital_allocation: List[CapitalAllocation]


class AdditionalInsights(BaseModel):
    strategic_risks: List[str]
    strategic_opportunities: List[str]
    comments: str


class CompanyReport(BaseModel):
    company_name: str
    industry: str
    headquarters: str
    source_documents: List[str]
    overview: Overview
    financial_highlights: FinancialHighlights
    operational_metrics: OperationalMetrics
    investment_requirements: InvestmentRequirements
    additional_insights: AdditionalInsights



def analyzeDocuments(documents, prompt):
    print("Analyzing documents")
    
    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]
    
    for document in documents:
        messages.append({
            "role": "user",
            "content": f"Input Document : {document}"
        })
    
    # Using the client object with the beta method as before
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        # response_format=CompanyReport  # Ensure CompanyReport is defined appropriately
        response_format={"type": "json_object"}
    )
    
    analysis = response.choices[0].message.content
    print("analysis",analysis)
    print("Analysis complete")
    return json.loads(analysis)



