from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from .schemas import ScanRequest, ThreatMineRequest
from feedback.loop_controller import FeedbackLoop
from identify.threat_miner import ThreatMiner
import os

router = APIRouter()

loop_controller = FeedbackLoop()
threat_miner = ThreatMiner()

@router.post("/scan")
def scan_text(request: ScanRequest):
    try:
        result = loop_controller.run(
            text=request.text,
            category=request.category,
            evolve=request.evolve,
            transaction=request.transaction
        )
        return loop_controller.serialize(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identify")
def identify_threat(request: ThreatMineRequest):
    try:
        attack = threat_miner.mine_threat(
            fraud_pattern=request.fraud_pattern,
            genai_capability=request.genai_capability,
            payment_vulnerability=request.payment_vulnerability
        )
        return attack.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history():
    return loop_controller.history.all()

@router.get("/stats")
def get_stats():
    return loop_controller.stats()

@router.get("/health")
def health_check():
    return {"status": "healthy"}
