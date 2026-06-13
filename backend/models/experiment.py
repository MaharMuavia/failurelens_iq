from pydantic import BaseModel, Field

class ExperimentDetails(BaseModel):
    experiment_id: str = Field(..., description="Unique identifier for the experiment")
    model: str = Field(..., description="ML model class/type used")
    train_accuracy: float = Field(..., description="Accuracy on the training set")
    validation_accuracy: float = Field(..., description="Accuracy on the validation set")
    test_accuracy: float = Field(..., description="Accuracy on the test set")
    dataset_size: int = Field(..., description="Number of samples in the dataset")
    feature_count: int = Field(..., description="Number of features in the dataset")
    notes: str = Field("", description="Optional notes or observations about the experiment")

class ExperimentInput(BaseModel):
    experiment: ExperimentDetails = Field(..., description="Details of the failed ML experiment")
