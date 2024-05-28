import json
import os

import pymongo
from dotenv import load_dotenv
load_dotenv()

output = [
    """
        {
            "ticker": "TCS", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "TCS reported a revenue growth of 3.4% in constant currency terms for FY24, an annual EPS growth of 10.9%, and improved Q4 operating margins at 26%, achieving strong deal momentum with a Q4 TCV of $13.2 billion."
                },
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management highlighted the absence of specific revenue or earnings guidance, but expressed optimism for future growth driven by strategic initiatives, deepening client relationships, and a strong deal pipeline."
                },
                {
                    "title": "Market and Competitive Landscape",
                    "text": "TCS sees strong competition and market pressures but remains resilient with strategic engagements in cloud transformation, AI enablement, and customer and employee experience enhancement across different industry verticals."
                }
            ],
            "caution": "The near-term demand outlook remains unclear and volatile, and TCS flagged challenges like economic slowdown, high interest rates, and geopolitical tensions that add to the uncertainty of financial projections.",
            "score": {
                "value": "7",
                "reason": "TCS displays strong financial health and robust deal momentum, but ongoing global uncertainties and market volatility prompt a cautious stance towards immediate growth prospects."
            }
        }
    """,
    """
        {
            "ticker": "INFY", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "Infosys reported a modest revenue growth of 1.4% in constant currency terms for FY24, an operating margin of 20.7%, and recorded the highest ever large deal value of $17.7 billion."
                }, 
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management anticipates FY25 to have revenue growth of 1% to 3% in constant currency terms and operating margin guidance of 20% to 22%, expecting similar levels of discretionary spending and digital transformation work as FY24."
                }, 
                {
                    "title": "Market and Competitive Landscape",
                    "text": "Infosys is focused on cost efficiency and consolidation in the competitive landscape while intensifying efforts in Generative AI, having achieved record large deal wins in FY24."
                }
            ], 
            "caution": "The company's recent rescoping and renegotiation of a major contract which affected revenue highlights potential volatility and execution risks in large deals.",
            "score": {
                "value": "7",
                "reason": "Infosys's robust large deal pipeline and strategic focus on AI and digital transformations are strong points, but concerns about the execution of these large deals and their impact on revenue temper the investment outlook."
            }
        }

    """,
    """
        {
            "ticker": "HCLTECH", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "HCL Technologies reported a 5% revenue growth in constant currency and 5.4% in US dollars year-on-year, with a notable increase in free cash flow by 27.7% and operating margins maintained at 18.2%."
                },
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management provided FY'25 revenue growth guidance of 3% to 5% in constant currency, expecting moderate enterprise IT spending and a focus on AI and emerging technologies, with operating margins projected to remain between 18% to 19%."
                },
                {
                    "title": "Market and Competitive Landscape",
                    "text": "The company highlighted significant growth in the services sector, particularly in cloud transformation and cybersecurity, and secured key client wins across diverse sectors including financial services, manufacturing, and technology."
                }
            ],
            "caution": "The uncertain macroeconomic environment and potential challenges in scaling new technology adoptions like generative AI may impact the projected revenue growth and operational margins.",
            "score": {
                "value": "7",
                "reason": "Despite a cautious market outlook and some organizational restructuring, the company is maintaining a stable growth trajectory and expanding client base, which indicates a potential for continued success."
            }
        }
    """,
    """
        {
            "ticker": "WIPRO", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "In Q4 FY '24, Wipro reported a marginal sequential IT services revenue growth of 0.1%, with large deal bookings TCV increasing by 17.4% year-on-year to $4.6 billion, and operating margins improved to 16.4%."
                },
                {
                    "title": "Management Commentary and Guidance",
                    "text": "The management focused on five areas to drive growth, including large deal momentum and industry-specific AI-infused solutions, with a cautious Q1 FY'25 growth guidance of (-1.5%) to (+0.5%) in constant currency."
                },
                {
                    "title": "Market and Competitive Landscape",
                    "text": "Wipro is strengthening its consulting capabilities, particularly through acquisitions like Capco, amidst a challenging and uncertain economic environment with specific growth seen in healthcare and BFSI sectors."
                }
            ],
            "caution": "The uncertain economic environment, coupled with challenges in the discretionary spending and the need for large-scale integration and execution, may pose risks to consistent growth and performance.",
            "score": {
                "value": "6",
                "reason": "Despite improved margins and large deal bookings, the cautious revenue guidance and ongoing economic uncertainties present a moderate risk, making a balanced investment outlook."
            }
        }
    """,
    """
        {
            "ticker": "TECHM", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics", 
                    "text": "Tech Mahindra reported a revenue of $1,548 million for Q4 FY24, a 6.4% YoY decline, and a full-year revenue of $6,277 million with a YoY decline of 4.7%; Q4 operating margin was 7.4%, and the company forecasts improvements with targeted EBIT margins exceeding 15% by FY27."
                }, 
                {
                    "title": "Management Commentary and Guidance", 
                    "text": "The company plans a turnaround with extensive investment in capabilities, focus on value-driven deals, and operational optimization to achieve above-peer-average growth and improved margins by FY27 under a revised strategic vision called 'Scale at Speed'."
                }, 
                {
                    "title": "Market and Competitive Landscape", 
                    "text": "Tech Mahindra identifies significant growth opportunities in the Americas, prioritizing sectors such as Telecom, Manufacturing, Banking, and Financial Services, aiming to leverage core banking transformation trends, digitalization, and its deep engineering capabilities."
                }
            ], 
            "caution": "The company's reliance on the communication vertical, historical instances of unpredictable quarterly performance, and ongoing organizational and structural changes present execution risks in achieving the planned turnaround.", 
            "score": {
                "value": "6", 
                "reason": "The company has laid out a solid strategy for transformation and growth backed by high-level commitments, but execution risks and current performance trends warrant cautious optimism."
            }
        }
    """,
    """
        {
            "ticker": "LTIM", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "LTIMindtree Limited reported a revenue of $4.3 billion in FY24, a growth of 4.4% in USD terms year-over-year, with an EBIT margin of 15.7% and PAT margin of 12.9%."
                }, 
                {
                    "title": "Management Commentary and Guidance",
                    "text": "The management acknowledged challenges in discretionary spending impacting revenue, noted improvements in process efficiencies and client count, and emphasized continued focus on synergistic growth and margin improvement."
                }, 
                {
                    "title": "Market and Competitive Landscape ",
                    "text": "Despite existing market volatilities and increased competition, LTIMindtree has achieved significant deal inflows and client expansion, positioning itself favorably within key industry verticals and geographies."
                }
            ], 
            "caution": "The caution involves potential risks in revenue fluctuation due to client-specific project cancellations and reliance on discretionary spending recovery.", 
            "score": {
                "value": "7", 
                "reason": "While the company shows stable financial performance and strong order inflow, the uncertain discretionary spending environment and recent challenges in top client engagements present some investment risks."
            }
        }

    """,
    """
        {
            "ticker": "POLICYBZR", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "PB Fintech's insurance premiums grew significantly with total premiums at ₹5,123Cr for the quarter and a YoY revenue growth of 34% to ₹3,438Cr; the company also reported a PAT of ₹64Cr, a swing of ₹552Cr from a loss of ₹488Cr last year."
                },
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management expressed satisfaction with achieving ahead-of-schedule break-even in Q3 and a strong growth in health and life insurance, projecting continued leadership and innovation while cautiously guiding short-term growth expectations due to ongoing adjustments."
                },
                {
                    "title": "Market and Competitive Landscape",
                    "text": "Despite a slowdown in the credit-linked business and overall challenging market conditions, PB Fintech maintained strong growth rates and market leadership, particularly in health insurance, benefiting from high persistency rates and digital efficiencies."
                }
            ],
            "caution": "The financial health of this company is largely dependent on the volatile insurance sector and regulatory changes could significantly impact operations.",
            "score": {
                "value": "8",
                "reason": "The company's transition from a loss to profitability and strong growth in core areas of health and insurance are promising though tempered by regulatory risks and market volatility."
            }
        }
    """,
    """
        {
            "ticker": "LTTS", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "L&T Technology Services delivered a solid financial performance with a 17.9% revenue growth in constant currency for FY24, EBIT margins maintained at 17%, and a significant increase in large deal wins including one USD 100 million deal."
                },
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management is optimistic about FY25 with a guidance of 8-10% USD constant currency revenue growth and continues to target a $1.5 billion run rate; however, they anticipate some softness in Q1 due to decision-making delays and geopolitical risks."
                },
                {
                    "title": "Market and Competitive Landscape",
                    "text": "The company highlighted strength across various sectors like Telecom, Hitech, and Transportation, and is actively seeking growth through new acquisitions in areas like ISV, MedTech, and European Automotive."
                }
            ],
            "caution": "The company warns of potential softness in Q1 FY25 and margin pressures due to geopolitical risks and the necessity for investment in technology and reorganization.",
            "score": {
                "value": "7",
                "reason": "Despite potential short-term challenges, the strong annual performance and strategic investments for future growth present a promising outlook."
            }
        }
    """,
    """
        {
            "ticker": "PERSISTENT", 
            "criteria": [
                {
                    "title": "Financial Performance Metrics",
                    "text": "Persistent Systems reported a Q4 FY24 revenue of USD 310.9 million, marking a 13.2% year-on-year growth and a quarterly revenue run rate crossing INR 2,500 crores; EBIT margin for Q4 was 14.45%, with strategic investments in sales, marketing, and technology including AI impacting margins."
                }, 
                {
                    "title": "Management Commentary and Guidance",
                    "text": "Management aims to maintain top quartile growth while keeping margins stable in the challenging macro environment by enhancing operational efficiencies, with medium-term targets to improve margins by 200 to 300 basis points over the next 3 years."
                }, 
                {
                    "title": "Market and Competitive Landscape",
                    "text": "Persistent Systems is expanding its presence and capabilities in generative AI through the SASVA platform and GenAI Hub, aiming to differentiate and capture a bigger market share in competition with larger IT service providers."
                }
            ], 
            "caution": "Strategic transitions towards high investment in AI technologies and associated platforms could impact short-term profitability and return on investments if growth does not meet expectations or if there is slower adoption of these technologies in the market.",
            "score": {
                "value": 8,
                "reason": "Given Persistent Systems' robust growth rates, strategic investments in emerging technologies, and expanding margin goals, there is potential upside, though strategic shifts and competitive pressures must be navigated carefully."
            }
        }
    """
]

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_concall_analysis = db['top_10_it_concall_analysis']

for val in output:
    json_response = json.loads(val)
    print(json_response['ticker'])
    if collection_concall_analysis.insert_one(json_response).acknowledged:
        print('Document for', json_response['ticker'], 'inserted successfully')
    # criteria = json_response['criteria']
    # for index, criterion in enumerate(criteria):
    #     print(index)
    #     print('Title:', criterion['title'])
    #     print('Text:', criterion['text'])
    # print('CAUTION:', json_response['caution'])
    # print('SCORE:', json_response['score']['value'])
    # print('REASON:', json_response['score']['reason'])
    # print()
    # print()
