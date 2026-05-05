from datetime import date

from pydantic import BaseModel, Field, model_validator


class TradingBase(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    date: date
    oil_id: str
    delivery_type_id: str
    delivery_basis_id: str
    volume: int
    total: int
    count: int


class TradingResultResponse(TradingBase):
    pass


class TradingDatesResponse(BaseModel):
    dates: list[date]


class DynamicsResponse(TradingBase):
    pass


class TradingFilterBase(BaseModel):
    oil_id: str | None = None
    delivery_type_id: str | None = None
    delivery_basis_id: str | None = None


class TradingDatesQuery(BaseModel):
    last_days: int = Field(default=30, ge=0, le=365)


class TradingResultsQuery(TradingFilterBase):
    limit: int = Field(default=100, gt=0, le=1000)


class DynamicsResultsQuery(TradingFilterBase):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date")
        return self
