from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.juror_generator import JurorGenerator
import logging

router = APIRouter(tags=["jurors"])
logger = logging.getLogger(__name__)

# Initialize generator
juror_generator = JurorGenerator()


@router.post("/generate")
async def generate_jury_pool(
    county: str = Query(..., description="County name"),
    state: str = Query(..., description="State abbreviation (e.g., CA, TX)"),
    pool_size: int = Query(12, ge=6, le=24, description="Number of jurors to generate"),
    case_type: Optional[str] = Query(None, description="Type of case (capital, drug, police, corporate)")
):
    """
    Generate a jury pool for a specific county
    """
    try:
        logger.info(f"Generating {pool_size} jurors for {county}, {state}")
        
        jurors = juror_generator.generate_jury_pool(
            county=county,
            state=state,
            pool_size=pool_size,
            case_type=case_type
        )
        
        return {
            "status": "success",
            "location": {
                "county": county,
                "state": state
            },
            "pool_size": pool_size,
            "case_type": case_type,
            "jurors": jurors
        }
        
    except Exception as e:
        logger.error(f"Error generating jury pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample/{state}")
async def get_sample_juror(
    state: str,
    age: Optional[int] = Query(None, ge=18, le=80, description="Juror age"),
    gender: Optional[str] = Query(None, description="Juror gender (Male/Female)"),
    education: Optional[int] = Query(None, ge=8, le=20, description="Years of education")
):
    """
    Generate a single sample juror with specific demographics
    """
    try:
        # Use a default county for the state
        default_counties = {
            'CA': 'Los Angeles',
            'TX': 'Harris',
            'FL': 'Miami-Dade',
            'NY': 'New York',
            'IL': 'Cook',
            'PA': 'Philadelphia',
            'OH': 'Cuyahoga',
            'GA': 'Fulton',
            'NC': 'Mecklenburg',
            'MI': 'Wayne'
        }
        
        county = default_counties.get(state, 'County')
        
        # Generate a single juror
        jurors = juror_generator.generate_jury_pool(county, state, pool_size=1)
        
        if jurors:
            juror = jurors[0]
            
            # Override demographics if specified
            if age:
                juror['demographics']['age'] = age
            if gender:
                juror['demographics']['gender'] = gender
            if education:
                juror['demographics']['education_years'] = education
                juror['demographics']['education_level'] = juror_generator._education_label(education)
            
            return {
                "status": "success",
                "juror": juror
            }
        
    except Exception as e:
        logger.error(f"Error generating sample juror: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demographics/stats")
async def get_demographic_stats(
    county: str = Query(..., description="County name"),
    state: str = Query(..., description="State abbreviation")
):
    """
    Get demographic statistics for a county
    """
    try:
        # Generate a larger pool to get statistics
        jurors = juror_generator.generate_jury_pool(county, state, pool_size=100)
        
        # Calculate statistics
        ages = [j['demographics']['age'] for j in jurors]
        genders = [j['demographics']['gender'] for j in jurors]
        races = [j['demographics']['race'] for j in jurors]
        education = [j['demographics']['education_years'] for j in jurors]
        political = [j['attitudes']['political_view'] for j in jurors]
        
        stats = {
            "county": county,
            "state": state,
            "sample_size": len(jurors),
            "demographics": {
                "age": {
                    "mean": round(sum(ages) / len(ages), 1),
                    "min": min(ages),
                    "max": max(ages)
                },
                "gender": {
                    "male": sum(1 for g in genders if g == 'Male'),
                    "female": sum(1 for g in genders if g == 'Female')
                },
                "race": {
                    race: sum(1 for r in races if r == race)
                    for race in set(races)
                },
                "education": {
                    "mean_years": round(sum(education) / len(education), 1),
                    "college_degree_pct": sum(1 for e in education if e >= 16) / len(education) * 100
                }
            },
            "attitudes": {
                "political_lean": {
                    "mean": round(sum(political) / len(political), 2),
                    "liberal": sum(1 for p in political if p <= 3),
                    "moderate": sum(1 for p in political if 3 < p < 5),
                    "conservative": sum(1 for p in political if p >= 5)
                },
                "death_penalty_support": round(
                    sum(j['attitudes']['death_penalty'] for j in jurors) / len(jurors) * 100, 1
                ),
                "marijuana_legalization": round(
                    sum(j['attitudes']['marijuana_legal'] for j in jurors) / len(jurors) * 100, 1
                )
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting demographic stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))