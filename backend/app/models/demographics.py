from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class Sex(str, Enum):
    MALE = "1"
    FEMALE = "2"


class Race(str, Enum):
    WHITE = "1"
    BLACK = "2"
    AMERICAN_INDIAN = "3"
    ALASKA_NATIVE = "4"
    AMERICAN_INDIAN_ALASKA_NATIVE = "5"
    ASIAN = "6"
    NATIVE_HAWAIIAN_PACIFIC_ISLANDER = "7"
    OTHER = "8"
    TWO_OR_MORE = "9"


class Education(str, Enum):
    NO_SCHOOLING = "01"
    NURSERY_SCHOOL = "02"
    KINDERGARTEN = "03"
    GRADE_1 = "04"
    GRADE_2 = "05"
    GRADE_3 = "06"
    GRADE_4 = "07"
    GRADE_5 = "08"
    GRADE_6 = "09"
    GRADE_7 = "10"
    GRADE_8 = "11"
    GRADE_9 = "12"
    GRADE_10 = "13"
    GRADE_11 = "14"
    GRADE_12_NO_DIPLOMA = "15"
    HIGH_SCHOOL_DIPLOMA = "16"
    GED = "17"
    SOME_COLLEGE_NO_DEGREE = "18"
    ASSOCIATE_DEGREE = "20"
    BACHELORS_DEGREE = "21"
    MASTERS_DEGREE = "22"
    PROFESSIONAL_DEGREE = "23"
    DOCTORATE_DEGREE = "24"


class ACSPUMSRecord(BaseModel):
    AGEP: int = Field(..., description="Age")
    SEX: Sex = Field(..., description="Sex")
    RAC1P: Race = Field(..., description="Race (single category)")
    SCHL: Education = Field(..., description="Educational attainment")
    HINCP: Optional[int] = Field(None, description="Household income (past 12 months)")
    PUMA: str = Field(..., description="Public Use Microdata Area code")
    STATEFIP: str = Field(..., description="State FIPS code")
    
    class Config:
        use_enum_values = True


class PersonalityTraits(BaseModel):
    extraversion: float = Field(..., ge=1, le=5, description="Extraversion score (1-5)")
    neuroticism: float = Field(..., ge=1, le=5, description="Neuroticism score (1-5)")
    agreeableness: float = Field(..., ge=1, le=5, description="Agreeableness score (1-5)")
    conscientiousness: float = Field(..., ge=1, le=5, description="Conscientiousness score (1-5)")
    openness: float = Field(..., ge=1, le=5, description="Openness score (1-5)")


class DemographicCluster(BaseModel):
    age_range: tuple[int, int]
    sex: Optional[Sex]
    race: Optional[Race]
    education_level: Optional[Education]
    income_range: Optional[tuple[int, int]]
    personality_averages: PersonalityTraits
    
    
class CountyData(BaseModel):
    state_fips: str
    county_name: str
    puma_codes: list[str]
    population: int
    demographics: list[ACSPUMSRecord]
    voting_data: Optional[Dict[str, float]] = Field(None, description="Party vote percentages")
    

class DataSource(BaseModel):
    name: str
    url: str
    last_updated: Optional[str]
    fields_used: list[str]
    description: str