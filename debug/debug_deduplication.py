"""Debug test for lead deduplication using real API calls.

Tests the complete deduplication pipeline with real OpenAI, Pinecone, and MongoDB calls.
Processes provided sample leads and saves all outputs to debug/output directory.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from clients import MongoDBClient, OpenAIClient, PineconeClient
from models import Lead
from services import deduplicate_leads
from utils import logger


def create_sample_leads() -> list[Lead]:
    """Create Lead objects from the provided sample text."""
    sample_texts = [
        "President Trump announced frameworks for new trade agreements with Japan and the Philippines, reducing U.S. tariffs on Japanese imports to 15% and Philippine goods to 19%. The deals include enhanced military cooperation, particularly significant amid China's aggression in the South China Sea, with Philippine President Marcos stating the U.S. remains their 'strongest partner.' This strengthens U.S. economic and strategic positioning in the Indo-Pacific.",
        
        "Trump called for criminal charges against former President Barack Obama and other officials, alleging treason over altered intelligence reports related to Trump-Russia investigations. This follows a criminal referral by Director of National Intelligence Tulsi Gabbard, who cited a '180-degree shift' in intelligence assessments during the 2016–2017 transition period, escalating political tensions in Washington.",
        
        "Humanitarian catastrophe deepens in Gaza as UN Secretary-General António Guterres warns of 'starvation knocking on every door.' Cease-fire negotiations are deadlocked over food aid distribution, with EU foreign policy chief Kaja Kallas threatening 'all options remain on the table' if Israel fails to improve access. U.S. envoy Steve Witkoff is mediating talks in Rome and Qatar to finalize a hostage deal.",
        
        "Turkey vowed direct intervention to prevent Syria's fragmentation after clashes in the south, with Foreign Minister Hakan Fidan pledging to block militant autonomy. This aligns with Turkey's increasing regional assertiveness, as President Erdoğan praised the nation's defense industry growth at the IDEF expo, where localization surpassed 80%.",
        
        "Ukraine saw its largest wartime protests targeting President Zelensky after he signed legislation weakening anti-corruption agencies. Protesters condemned what they called concessions to 'Russian influence,' while Zelensky defended the move as necessary for sovereignty. Meanwhile, Ukraine's military commander urgently requested more U.S. and European air defenses against intensified Russian strikes.",
        
        "The U.S. imposed sanctions on a Houthi-linked petroleum smuggling network spanning Yemen and the UAE, targeting Iran-backed militant activities. This coincides with fresh sanctions against the Houthis as part of broader efforts to disrupt Iran's regional influence and curtail its destabilizing proxy warfare in the Middle East.",
        
        "China rebuked the U.S. for withdrawing from UNESCO—its third exit—calling it 'not what a major country should do.' This occurred amid U.S.-China trade talks scheduled in Stockholm, where Treasury Secretary Scott Bessent will discuss extending tariff truces and China's oil purchases from Russia/Iran. Trump also teased a 'not too distant' visit to China.",
        
        "Portugal endorsed Morocco's Western Sahara autonomy plan, with Foreign Minister Paulo Rangel calling it a 'serious and credible basis.' This aligns with growing Western support for Morocco's proposal, contrasting Spain's previous stance and shifting diplomatic dynamics in North Africa amid regional instability.",
        
        "The International Court of Justice will issue a landmark advisory opinion on state obligations to combat climate change and legal consequences for emissions-causing harm. While non-binding, the ruling is expected to influence global climate litigation and pressure nations to strengthen environmental policies under international law.",
        
        "A Syrian American was executed during sectarian violence in Sweida, Syria, highlighting escalating tensions. The killing follows anti-government protests in the Druze-majority region, underscoring Syria's persistent instability and the risks facing diaspora returnees amid the country's protracted conflict.",
        
        "Students protested in Bangladesh demanding transparency after an air force jet crashed into a school, killing 19. Demonstrators called for accountability and investigations into military safety protocols, reflecting public anger over governance failures as the death toll continues to rise."
    ]
    
    return [Lead(discovered_lead=text) for text in sample_texts]


def debug_mongodb_queries(mongodb_client: MongoDBClient) -> Dict[str, Any]:
    """Debug MongoDB database queries to understand why get_recent_stories returns 0."""
    from bson import ObjectId
    from datetime import datetime, timedelta
    
    logger.info("🔍 DEBUGGING MONGODB QUERIES...")
    
    debug_info: Dict[str, Any] = {
        "total_documents": 0,
        "recent_documents_24h": 0,
        "documents_with_summary": 0,
        "sample_documents": [],
        "query_analysis": {},
    }
    
    try:
        # Get total document count
        total_count = mongodb_client._collection.count_documents({})
        debug_info["total_documents"] = total_count
        logger.info("  📊 Total documents in collection: %d", total_count)
        
        if total_count == 0:
            logger.warning("  ⚠️ Database collection is empty!")
            return debug_info
        
        # Get sample documents (latest 5) for basic structure analysis
        sample_docs = list(mongodb_client._collection.find({}).sort("_id", -1).limit(5))
        debug_info["sample_documents"] = []
        
        if sample_docs:
            latest_doc = sample_docs[0]
            obj_id = latest_doc["_id"]
            timestamp = obj_id.generation_time
            has_summary = "summary" in latest_doc and bool(latest_doc["summary"])
            
            logger.info("  📋 Sample document structure (latest):")
            logger.info("    Latest timestamp: %s", timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"))
            logger.info("    Has summary field: %s", has_summary)
            logger.info("    Document fields: %s", ", ".join(latest_doc.keys()))
            
            # Store minimal info for debugging
            for i, doc in enumerate(sample_docs, 1):
                obj_id = doc["_id"]
                timestamp = obj_id.generation_time
                has_summary = "summary" in doc and bool(doc["summary"])
                
                sample_info = {
                    "index": i,
                    "id": str(obj_id),
                    "timestamp": timestamp.isoformat(),
                    "has_summary": has_summary,
                    "summary_length": len(doc.get("summary", "")) if has_summary else 0,
                    "fields": list(doc.keys()),
                }
                if isinstance(debug_info["sample_documents"], list):
                    debug_info["sample_documents"].append(sample_info)
        
        # Test the 24-hour query
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_object_id = ObjectId.from_datetime(cutoff_time)
        
        logger.info("  🕐 Testing 24-hour query...")
        logger.info("    Cutoff time: %s", cutoff_time.strftime("%Y-%m-%d %H:%M:%S UTC"))
        logger.info("    Cutoff ObjectId: %s", str(cutoff_object_id))
        
        # Query for recent documents
        query = {"_id": {"$gte": cutoff_object_id}}
        recent_docs = list(mongodb_client._collection.find(query))
        debug_info["recent_documents_24h"] = len(recent_docs)
        logger.info("    Documents from last 24h: %d", len(recent_docs))
        
        # Test with summary field projection
        recent_with_summary = list(mongodb_client._collection.find(query, {"summary": 1}))
        debug_info["documents_with_summary"] = len([d for d in recent_with_summary if d.get("summary")])
        logger.info("    Documents with summary field: %d", debug_info["documents_with_summary"])
        
        # Try alternative time ranges
        for hours in [48, 72, 168]:  # 2 days, 3 days, 1 week
            alt_cutoff = datetime.now() - timedelta(hours=hours)
            alt_cutoff_id = ObjectId.from_datetime(alt_cutoff)
            alt_query = {"_id": {"$gte": alt_cutoff_id}}
            alt_count = mongodb_client._collection.count_documents(alt_query)
            if isinstance(debug_info["query_analysis"], dict):
                debug_info["query_analysis"][f"{hours}h"] = alt_count
            logger.info("    Documents from last %dh: %d", hours, alt_count)
        
        # Test direct date field if available
        if sample_docs and "date" in sample_docs[0]:
            logger.info("  📅 Testing date field queries...")
            from utils.date_formatting import get_today_formatted
            today = get_today_formatted()
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            today_count = mongodb_client._collection.count_documents({"date": today})
            yesterday_count = mongodb_client._collection.count_documents({"date": yesterday})
            
            logger.info("    Documents with today's date (%s): %d", today, today_count)
            logger.info("    Documents with yesterday's date (%s): %d", yesterday, yesterday_count)
        
    except Exception as e:
        logger.error("  ❌ MongoDB debug query failed: %s", str(e))
        debug_info["error"] = str(e)
    
    return debug_info


def save_test_outputs(leads: list[Lead], unique_leads: list[Lead], test_start_time: datetime, debug_info: dict[str, object] | None = None) -> None:
    """Save test results to debug/output/deduplication_output directory."""
    output_dir = Path("debug/output/deduplication_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = test_start_time.strftime("%Y%m%d_%H%M%S")
    
    # Save original leads
    original_leads_file = output_dir / f"deduplication_original_leads_{timestamp}.json"
    with open(original_leads_file, "w", encoding="utf-8") as f:
        original_data = {
            "timestamp": test_start_time.isoformat(),
            "total_leads": len(leads),
            "leads": [
                {
                    "index": i,
                    "discovered_lead": lead.discovered_lead,
                    "date": lead.date,
                    "sources": lead.sources,
                    "report": lead.report,
                }
                for i, lead in enumerate(leads)
            ]
        }
        json.dump(original_data, f, indent=2, ensure_ascii=False)
    
    # Save unique leads after deduplication
    unique_leads_file = output_dir / f"deduplication_unique_leads_{timestamp}.json"
    with open(unique_leads_file, "w", encoding="utf-8") as f:
        unique_data = {
            "timestamp": test_start_time.isoformat(),
            "original_count": len(leads),
            "unique_count": len(unique_leads),
            "duplicates_removed": len(leads) - len(unique_leads),
            "unique_leads": [
                {
                    "index": i,
                    "discovered_lead": lead.discovered_lead,
                    "date": lead.date,
                    "sources": lead.sources,
                    "report": lead.report,
                }
                for i, lead in enumerate(unique_leads)
            ]
        }
        json.dump(unique_data, f, indent=2, ensure_ascii=False)
    
    # Save summary report
    summary_file = output_dir / f"deduplication_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        summary_data = {
            "test_metadata": {
                "timestamp": test_start_time.isoformat(),
                "test_type": "deduplication_debug",
                "description": "Real API test of lead deduplication pipeline",
            },
            "results": {
                "total_input_leads": len(leads),
                "unique_output_leads": len(unique_leads),
                "duplicates_detected": len(leads) - len(unique_leads),
                "deduplication_rate": round((len(leads) - len(unique_leads)) / len(leads) * 100, 2) if leads else 0,
            },
            "mongodb_debug": debug_info,
            "file_outputs": {
                "original_leads": str(original_leads_file.name),
                "unique_leads": str(unique_leads_file.name),
                "summary": str(summary_file.name),
            }
        }
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    logger.info("💾 Saved test outputs:")
    logger.info("  📄 Original leads: %s", original_leads_file.name)
    logger.info("  📄 Unique leads: %s", unique_leads_file.name)
    logger.info("  📄 Summary: %s", summary_file.name)


def main() -> None:
    """Run the deduplication debug test with real API calls."""
    test_start_time = datetime.now()
    logger.info("🧪 DEDUPLICATION DEBUG TEST STARTED")
    logger.info("⏰ Test started at: %s", test_start_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # Initialize real clients
        logger.info("📡 Initializing real API clients...")
        openai_client = OpenAIClient()
        pinecone_client = PineconeClient()
        mongodb_client = MongoDBClient()
        logger.info("✅ All clients initialized successfully")
        
        # Debug MongoDB queries first
        debug_info = debug_mongodb_queries(mongodb_client)
        
        # Create sample leads
        logger.info("📝 Creating sample leads from provided texts...")
        leads = create_sample_leads()
        logger.info("✅ Created %d sample leads", len(leads))
        
        # Run deduplication with real API calls
        logger.info("🔄 Starting deduplication pipeline...")
        unique_leads = deduplicate_leads(
            leads,
            openai_client=openai_client,
            pinecone_client=pinecone_client,
            mongodb_client=mongodb_client,
        )
        
        # Log results
        duplicates_found = len(leads) - len(unique_leads)
        logger.info("✅ DEDUPLICATION COMPLETE:")
        logger.info("  📊 Original leads: %d", len(leads))
        logger.info("  📊 Unique leads: %d", len(unique_leads))
        logger.info("  📊 Duplicates removed: %d", duplicates_found)
        
        if duplicates_found > 0:
            dedup_rate = round(duplicates_found / len(leads) * 100, 2)
            logger.info("  📊 Deduplication rate: %s%%", dedup_rate)
        
        # Save outputs
        logger.info("💾 Saving test outputs to debug/output...")
        save_test_outputs(leads, unique_leads, test_start_time, debug_info)
        
        # Final summary
        test_duration = datetime.now() - test_start_time
        logger.info("🎉 TEST COMPLETED SUCCESSFULLY")
        logger.info("⏱️ Test duration: %s", str(test_duration).split('.')[0])
        
    except Exception as e:
        logger.error("❌ TEST FAILED: %s", str(e))
        logger.error("📍 Error occurred during deduplication test execution")
        raise


if __name__ == "__main__":
    main()
