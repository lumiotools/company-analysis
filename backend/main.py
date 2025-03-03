import asyncio
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from services.fileUpload import create_folder_and_upload_files
from services.combineDocAnalysis import combine_doc_analyses
from services.comgineExcelAnalysis import combine_excel_analyses
from services.analyzer import process_hierarchical_data
from services.saveJosn import write_extracted_content_json
from services.files import download_files, find_alpine_vc_files, get_directory_list, listFiles, get_all_files
from services.extractContent import extractContent
from services.analyzeDocuments import analyzeDocuments
import os
import tempfile
import requests
from prompts import system_prompt, system_prompt_doc, system_prompt_excel
from services.saveExcel import save_to_excel
from services.saveDoc import save_multiple_analyses_to_docx
import shutil
import time
from file_server.route import router as fileServerRouter
from analysis.gemini import gemini_upload_files, gemini_analyze_files_excel, gemini_analyze_files_doc

UPLOAD_DIR = "temp_uploads"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fileServerRouter, prefix="/api/file-server")

@app.post("/api/analyze")
async def analyze_company(directory_name: str):
    folder_name = uuid.uuid4()
    str_folder_name = str(folder_name)  # Convert UUID to string right after creation
    
    try:
        start_time = time.time()
        # Get the list of files from the server
        files = listFiles()
        # print("files",files)
        # directory_name = "8-Bit Capital"
        print("directory",str(directory_name))
        target_dir = get_directory_list(files, str(directory_name))
        

        all_file_urls = get_all_files(target_dir)
        print("all file url",all_file_urls)
        
        # Download the files
        downloaded_files = download_files(all_file_urls, str_folder_name)  # Use string version
        print("Downloaded files:", downloaded_files)
        
        
        final_files = [path.replace("\\","/") for path in downloaded_files if not ".docx" in path]
        uploaded_files = gemini_upload_files( final_files)
        
        print("uploaded files",uploaded_files)
        
        # Analyze the files
        
        excel_response = gemini_analyze_files_excel( uploaded_files)
        print("excel response",excel_response)
        
        doc_response = gemini_analyze_files_doc( uploaded_files)    
        print("doc response",doc_response)
        
        end_time = time.time()  # End the timer
        total_time = end_time - start_time  # Calculate execution time in seconds
        
        return JSONResponse(
            content={"success": True, "excel": excel_response, "doc": doc_response, "time_taken_seconds": round(total_time, 2)}
        )
        
        
        
        # # Rest of your code using str_folder_name
        # result_location = write_extracted_content_json(str_folder_name)
        # final_result_location = process_hierarchical_data(result_location, system_prompt_excel, system_prompt_doc)
        # combinedExcelAnalysis = combine_excel_analyses(final_result_location)
        # combinedDocAnalysis = combine_doc_analyses(final_result_location)
        # saved_files = save_multiple_analyses_to_docx(combinedDocAnalysis, str_folder_name)
        # create_folder_and_upload_files(saved_files, 'docOutput')
        # return JSONResponse(content={"success": True,files:files})
        
        return JSONResponse(content={"success": True, "title":directory_name ,"excel": "combinedExcelAnalysis", "doc": "combinedDocAnalysis","time_taken_seconds": round(total_time, 2)})
    
    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)
    
    finally:
        folder_path = os.path.join(UPLOAD_DIR, str_folder_name)  # Use string version here
        try:
            if os.path.exists(folder_path):
                print(f"Cleaning up temporary folder: {folder_path}")
                shutil.rmtree(folder_path)
                print(f"Successfully removed {folder_path}")
            else:
                print(f"Folder {folder_path} does not exist, no cleanup needed")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {str(cleanup_error)}")



HARDCODED_RESPONSE = {
    "success": True,
  "excel": [
        {
            "Fund Manager": "8-Bit Capital",
            "TVPI": "1.24",
            "Location": "San Francisco, CA",
            "URL": "https://8bitcapital.com/",
            "Summary": "Founded in 2019, 8-Bit Capital is a venture capital investment firm based in San Francisco, California. The firm prefers to invest in early-stage software startups with a focus on artificial intelligence, cloud, cybersecurity, enterprise, fintech, and social.",
            "Fund Stage": "Fund II",
            "Fund Size": "$60,000,000",
            "Invested to Date": "$20,416,093",
            "Minimum Check Size": "$500,000",
            "# of Portfolio Companies": 56,
            "Stage Focus": "Pre-Seed, Seed",
            "Sectors": "AI / ML, Cloudtech, Cybersecurity, B2B, Fintech, SaaS",
            "Market Validated Outlier": False,
            "Female Partner in Fund": False,
            "Minority (BIPOC) Partner in Fund": False
        },
        {
            "Fund Manager": "Draper Cygnus",
            "TVPI": "3.69",
            "Location": "Buenos Aires, Argentina",
            "URL": "https://www.drapercygnus.vc/",
            "Summary": "Founded in 2017, Draper Cygnus is a venture capital firm based in Buenos Aires, Argentina. The firm is focused on backing early-stage, high-impact companies with global potential. The firm specializes in deep tech, including artificial intelligence, biotechnology, materials, space, and cybersecurity, while also targeting opportunities in fintech and decentralization. The firm partners with visionary founders, particularly those from Latin America or US Latinos, to drive transformative innovation and scale on the international stage.",
            "Fund Stage": "Fund IV",
            "Fund Size": "$50,000,000",
            "Invested to Date": "$30,000,000",
            "Minimum Check Size": "$200,000",
            "# of Portfolio Companies": 33,
            "Stage Focus": "Pre-Seed, Seed",
            "Sectors": "AI / ML, Web 3.0, Deep Tech, Defense Tech, Energy, Robotics & Drones, Space Tech",
            "Market Validated Outlier": True,
            "Female Partner in Fund": True,
            "Minority (BIPOC) Partner in Fund": True
        },
        {
            "Fund Manager": "Alpine VC",
            "TVPI": "0.94",
            "Location": "Alameda, CA",
            "URL": "http://www.alpine.vc/",
            "Summary": "Founded in 2022, Alpine VC is a venture capital firm based in Alameda, California. The firm seeks to invest in seed-stage startups operating in the consumer application, B2B software, and marketplace sectors across the United States and Southeast Asia.",
            "Fund Stage": "Fund I",
            "Fund Size": "$20,000,000",
            "Invested to Date": "$5,327,538",
            "Minimum Check Size": "$500,000",
            "# of Portfolio Companies": 50,
            "Stage Focus": "Seed",
            "Sectors": "B2B, B2C",
            "Market Validated Outlier": False,
            "Female Partner in Fund": True,
            "Minority (BIPOC) Partner in Fund": False
        },
        {
            "Fund Manager": "Feld Ventures",
            "TVPI": "1.76",
            "Location": "Toronto, Canada",
            "URL": "http://www.feldventures.com/",
            "Summary": "Feld Ventures aims to be the early-stage capital provider of choice for startups who leverage financial technology to power, grow, and strengthen their businesses.",
            "Fund Stage": "Fund I",
            "Fund Size": "$15,000,000",
            "Invested to Date": "$17,231,000",
            "Minimum Check Size": "$150,000",
            "# of Portfolio Companies": 24,
            "Stage Focus": "Pre-Seed, Seed",
            "Sectors": "Fintech, AI / ML",
            "Market Validated Outlier": False,
            "Female Partner in Fund": False,
            "Minority (BIPOC) Partner in Fund": False
        }
  ],
    
    "doc": {
        "analysis": [
            {
                "GENERAL FUND INFORMATION": {
                    "Fund Name": "8-Bit Capital",
                    "Fund Location": "USA",
                    "Fund Website URL": "https://www.8bitcapital.com"
                },
                "PRIMARY CONTACT INFORMATION": {
                    "Primary Contact Name": "James Sowers",
                    "Primary Contact Position": "Managing Partner",
                    "Primary Contact Phone Number": "555-123-4567",
                    "Primary Contact Email": "james@8bitcapital.com",
                    "Primary Contact LinkedIn URL": "https://www.linkedin.com/in/jamessowers"
                },
                "FUND-SPECIFIC DETAILS (CURRENT FUND)": {
                    "Fundraising Status & Timing": {
                        "Currently Fundraising": True,
                        "Current Fund Number": "III",
                        "Fund Size (Target & Cap)": "$200M",
                        "Already Closed / Committed Amount": "$150M",
                        "First Close Date": "2022-01-15",
                        "Expected Final Close Date": "2023-12-31",
                        "Minimum LP Commitment": "$500K",
                        "Capital Call Mechanics": "Quarterly"
                    },
                    "Fees, Terms, and Economics": {
                        "Management Fee Percentage": 2,
                        "Carried Interest Percentage": 20,
                        "Total AUM (for the GP)": "$1B"
                    },
                    "Sector & Stage Focus": {
                        "Sector Preference / Focus": "Technology",
                        "Stage Focus": "Early Stage",
                        "Impact Investing": False
                    },
                    "Investment Strategy": {
                        "Preferred Investment Stage": "Seed to Series A",
                        "Check Size Range": "$1M - $5M",
                        "Yearly Investment Cadence": 10,
                        "Target Ownership Percentage": 15,
                        "Follow-On Reserves": True,
                        "Active Investment Period": "5 years",
                        "Portfolio Company Investment Forecast": "$50M",
                        "Target Valuations": "$20M - $100M"
                    },
                    "Governance & Participation": {
                        "Board Seat Requests": True,
                        "Lead Investor Frequency": True,
                        "LP List": []
                    }
                },
                "TRACK RECORD (PORTFOLIO COMPANIES)": [
                    {
                        "Portfolio Company Name": "GameTech",
                        "Company URL": "https://www.gametech.com",
                        "Investment Fund/Source": "8-Bit Capital",
                        "Amount Invested": "$2M",
                        "Post-Money Valuation": "$25M",
                        "Stage/Round": "Series A",
                        "Form of Financing": "Equity",
                        "Unrealized Value": "$5M",
                        "Distributed Value": "$0",
                        "Total Value": "$5M",
                        "DPI": 0,
                        "MOIC": 2.5,
                        "IRR": 10,
                        "Highlighted Co-Investors": []
                    }
                ],
                "DIVERSITY INFORMATION": {
                    "Minority (BIPOC) Partners in GP": False,
                    "Female Partners in GP": True
                },
                "PAST FUNDS / INVESTMENT VEHICLES": [],
                "ADDITIONAL / MISCELLANEOUS DATA POINTS": {
                    "Validation/Proof Cases of Sourcing Methodology": None,
                    "Due Diligence Scorecard": None,
                    "Entity Structure": "LLC",
                    "Creator of Fund Manager's LPA": "Jane Doe",
                    "Creator of Subscription Agreement": "John Smith",
                    "Existing Side Letters": False,
                    "Fund Manager Bio/Career Summary": None
                }
            },
            {
                "GENERAL FUND INFORMATION": {
                    "Fund Name": "Alpine VC",
                    "Fund Location": "USA",
                    "Fund Website URL": "https://www.alpinevc.com"
                },
                "PRIMARY CONTACT INFORMATION": {
                    "Primary Contact Name": "Sarah Johnson",
                    "Primary Contact Position": "Managing Partner",
                    "Primary Contact Phone Number": "555-987-6543",
                    "Primary Contact Email": "sarah@alpinevc.com",
                    "Primary Contact LinkedIn URL": "https://www.linkedin.com/in/sarahjohnson"
                },
                "FUND-SPECIFIC DETAILS (CURRENT FUND)": {
                    "Fundraising Status & Timing": {
                        "Currently Fundraising": False,
                        "Current Fund Number": "II",
                        "Fund Size (Target & Cap)": "$300M",
                        "Already Closed / Committed Amount": "$300M",
                        "First Close Date": "2021-06-01",
                        "Expected Final Close Date": "2022-05-30",
                        "Minimum LP Commitment": "$1M",
                        "Capital Call Mechanics": "Semi-Annual"
                    },
                    "Fees, Terms, and Economics": {
                        "Management Fee Percentage": 2,
                        "Carried Interest Percentage": 20,
                        "Total AUM (for the GP)": "$750M"
                    },
                    "Sector & Stage Focus": {
                        "Sector Preference / Focus": "Healthcare, Technology",
                        "Stage Focus": "Growth Stage",
                        "Impact Investing": True
                    },
                    "Investment Strategy": {
                        "Preferred Investment Stage": "Series B and later",
                        "Check Size Range": "$5M - $15M",
                        "Yearly Investment Cadence": 10,
                        "Target Ownership Percentage": 20,
                        "Follow-On Reserves": True,
                        "Active Investment Period": "5 years",
                        "Portfolio Company Investment Forecast": "$60M",
                        "Target Valuations": "$40M - $150M"
                    },
                    "Governance & Participation": {
                        "Board Seat Requests": False,
                        "Lead Investor Frequency": False,
                        "LP List": []
                    }
                },
                "TRACK RECORD (PORTFOLIO COMPANIES)": [],
                "DIVERSITY INFORMATION": {
                    "Minority (BIPOC) Partners in GP": True,
                    "Female Partners in GP": True
                },
                "PAST FUNDS / INVESTMENT VEHICLES": [],
                "ADDITIONAL / MISCELLANEOUS DATA POINTS": {
                    "Validation/Proof Cases of Sourcing Methodology": None,
                    "Due Diligence Scorecard": None,
                    "Entity Structure": "LP Partnership",
                    "Creator of Fund Manager's LPA": "Emily White",
                    "Creator of Subscription Agreement": None,
                    "Existing Side Letters": False,
                    "Fund Manager Bio/Career Summary": None
                }
            },
            {
                "GENERAL FUND INFORMATION": {
                    "Fund Name": "Feld Ventures",
                    "Fund Location": "USA",
                    "Fund Website URL": "https://www.feldventures.com"
                },
                "PRIMARY CONTACT INFORMATION": {
                    "Primary Contact Name": "Brad Feld",
                    "Primary Contact Position": "Managing Partner",
                    "Primary Contact Phone Number": None,
                    "Primary Contact Email": "brad@feldventures.com",
                    "Primary Contact LinkedIn URL": "https://www.linkedin.com/in/bradfeld"
                },
                "FUND-SPECIFIC DETAILS (CURRENT FUND)": {
                    "Fundraising Status & Timing": {
                        "Currently Fundraising": False,
                        "Current Fund Number": "IV",
                        "Fund Size (Target & Cap)": "$500M",
                        "Already Closed / Committed Amount": "$500M",
                        "First Close Date": "2020-01-01",
                        "Expected Final Close Date": "2021-12-31",
                        "Minimum LP Commitment": "$1M",
                        "Capital Call Mechanics": "Annual"
                    },
                    "Fees, Terms, and Economics": {
                        "Management Fee Percentage": 2,
                        "Carried Interest Percentage": 20,
                        "Total AUM (for the GP)": "$1.5B"
                    },
                    "Sector & Stage Focus": {
                        "Sector Preference / Focus": "Technology, Consumer",
                        "Stage Focus": "Seed and Early Stage",
                        "Impact Investing": False
                    },
                    "Investment Strategy": {
                        "Preferred Investment Stage": "Seed to Series B",
                        "Check Size Range": "$500K - $5M",
                        "Yearly Investment Cadence": 20,
                        "Target Ownership Percentage": 25,
                        "Follow-On Reserves": True,
                        "Active Investment Period": "7 years",
                        "Portfolio Company Investment Forecast": "$100M",
                        "Target Valuations": "$10M - $50M"
                    },
                    "Governance & Participation": {
                        "Board Seat Requests": True,
                        "Lead Investor Frequency": True,
                        "LP List": []
                    }
                },
                "TRACK RECORD (PORTFOLIO COMPANIES)": [],
                "DIVERSITY INFORMATION": {
                    "Minority (BIPOC) Partners in GP": True,
                    "Female Partners in GP": False
                },
                "PAST FUNDS / INVESTMENT VEHICLES": [],
                "ADDITIONAL / MISCELLANEOUS DATA POINTS": {
                    "Validation/Proof Cases of Sourcing Methodology": None,
                    "Due Diligence Scorecard": None,
                    "Entity Structure": "LLC",
                    "Creator of Fund Manager's LPA": "Brad Feld",
                    "Creator of Subscription Agreement": None,
                    "Existing Side Letters": True,
                    "Fund Manager Bio/Career Summary": None
                }
            },
            {
                "GENERAL FUND INFORMATION": {
                    "Fund Name": "Draper Cygnus",
                    "Fund Location": "USA",
                    "Fund Website URL": "https://www.drapercygnus.com"
                },
                "PRIMARY CONTACT INFORMATION": {
                    "Primary Contact Name": "Tim Draper",
                    "Primary Contact Position": "Founder",
                    "Primary Contact Phone Number": "555-111-2222",
                    "Primary Contact Email": "tim@drapercygnus.com",
                    "Primary Contact LinkedIn URL": "https://www.linkedin.com/in/timdraper"
                },
                "FUND-SPECIFIC DETAILS (CURRENT FUND)": {
                    "Fundraising Status & Timing": {
                        "Currently Fundraising": True,
                        "Current Fund Number": "I",
                        "Fund Size (Target & Cap)": "$100M",
                        "Already Closed / Committed Amount": "$50M",
                        "First Close Date": "2022-03-01",
                        "Expected Final Close Date": "2023-09-30",
                        "Minimum LP Commitment": "$250K",
                        "Capital Call Mechanics": "Quarterly"
                    },
                    "Fees, Terms, and Economics": {
                        "Management Fee Percentage": 2.5,
                        "Carried Interest Percentage": 25,
                        "Total AUM (for the GP)": "$2B"
                    },
                    "Sector & Stage Focus": {
                        "Sector Preference / Focus": "Blockchain, Fintech",
                        "Stage Focus": "Early Stage",
                        "Impact Investing": False
                    },
                    "Investment Strategy": {
                        "Preferred Investment Stage": "Seed and Series A",
                        "Check Size Range": "$1M - $3M",
                        "Yearly Investment Cadence": 12,
                        "Target Ownership Percentage": 10,
                        "Follow-On Reserves": True,
                        "Active Investment Period": "5 years",
                        "Portfolio Company Investment Forecast": "$30M",
                        "Target Valuations": "$5M - $15M"
                    },
                    "Governance & Participation": {
                        "Board Seat Requests": True,
                        "Lead Investor Frequency": True,
                        "LP List": []
                    }
                },
                "TRACK RECORD (PORTFOLIO COMPANIES)": [],
                "DIVERSITY INFORMATION": {
                    "Minority (BIPOC) Partners in GP": False,
                    "Female Partners in GP": True
                },
                "PAST FUNDS / INVESTMENT VEHICLES": [],
                "ADDITIONAL / MISCELLANEOUS DATA POINTS": {
                    "Validation/Proof Cases of Sourcing Methodology": None,
                    "Due Diligence Scorecard": None,
                    "Entity Structure": "LLC",
                    "Creator of Fund Manager's LPA": "Tim Draper",
                    "Creator of Subscription Agreement": None,
                    "Existing Side Letters": False,
                    "Fund Manager Bio/Career Summary": None
                }
            }
        ]
    }
}


@app.post("/api/analyze2")
async def analyze_company():
    # Simulate a 30-second delay
    # await asyncio.sleep(30)
    
    # Return the hardcoded response
    return HARDCODED_RESPONSE