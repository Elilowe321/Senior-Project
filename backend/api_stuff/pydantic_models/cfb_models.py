from pydantic import BaseModel, Field
from typing import List, Optional


# Define a Pydantic model for the request body
class ReturnModel(BaseModel):
    model_id: int = Field(..., description="Model ID", alias="id")
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="Name of user model")
    description: Optional[str] = Field(None, description="Description of user model")
    type: str = Field(..., description="Type of model used")
    target: str = Field(..., description="Target of the model")
    file_location_class: Optional[str] = Field(
        None, description="Location of the classification model"
    )
    file_location_reg: Optional[str] = Field(
        None, description="Location of the regression model"
    )
    classification_accuracy: Optional[float] = Field(
        None, description="Accuracy of the classification model"
    )
    mean_squared_error_home: Optional[float] = Field(
        None,
        description="Accuracy of the regression model for home team",
        alias="mse_home",
    )
    mean_squared_error_away: Optional[float] = Field(
        None,
        description="Accuracy of the regression model for away team",
        alias="mse_away",
    )
    columns: List[str] = Field(..., description="List of columns used in model")


# Define a Pydantic model for the request body
class CreateModel(BaseModel):
    user_id: int
    model_columns: List[str]
    name: str
    type: str
    target: str
    description: Optional[str] = None

    class Config:
        protected_namespaces = ()


# Delete model
class DeleteModel(BaseModel):
    user_id: int
    model_id: int

    class Config:
        protected_namespaces = ()


# Changes the columns that a user chooses into correct format
def chosen_columns(selected_columns, target):

    home_away_columns: List[str] = []
    away_columns: List[str] = []

    # Make sure the home stats are first
    for column in selected_columns:
        if column != "target":
            home_away_columns.append(f"home_{column}")
            away_columns.append(f"away_{column}")

    # If the target wasn't selected as an identifier, put it in
    if target not in selected_columns and target != "target":
        home_away_columns.append(f"home_{target}")
        away_columns.append(f"away_{target}")

    home_away_columns.extend(away_columns)

    # Only put target as a column if its in
    if target == "target":
        home_away_columns.append(target)

    # Sort for machine learning
    return home_away_columns