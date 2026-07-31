from typing import Optional
from dotenv import dotenv_values
from pydantic import BaseModel, Field, model_validator, ValidationError, field_validator


class MazeConfig(BaseModel):
    width: int = Field(..., ge=3, alias='WIDTH')
    height: int = Field(..., ge=3, alias='HEIGHT')
    entry: tuple[int, int] = Field(..., alias='ENTRY')
    exit: tuple[int, int] = Field(..., alias='EXIT')
    output_file: str = Field(default="maze.txt", alias='OUTPUT_FILE')
    perfect: bool = Field(default=True, alias='PERFECT')
    seed: Optional[int] = Field(default=None, alias='SEED')

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def validate_coordinates(cls, value: str) -> tuple[int, int]:
        return tuple(map(int, value.split(',')))

    @field_validator('perfect', mode='before')
    @classmethod
    def validate_perfect(cls, value: str) -> bool:
        if value == "1":
            return True
        elif value == "0":
            return False
        if value != "True" and value != "False":
            raise ValueError("PERFECT must be 'True' or 'False'.")
        return value
    
    @model_validator(mode="after")
    def validate_entry_and_exit(self) -> "MazeConfig":
        entry = self.entry
        exit = self.exit
        width = self.width
        height = self.height

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry point is out of bounds.")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Exit point is out of bounds.")
        if entry == exit:
            raise ValueError("Entry and exit points cannot be the same.")

        return self

def load_config(config_path: str) -> MazeConfig:
    try:
        data = dict(dotenv_values(config_path))
        return MazeConfig(**data)
    except ValidationError as e:
        for error in e.errors():
            if error['type'] == 'value_error':
                print(f"Invalid value in '{config_path}': {error['msg']}")
            print(f"Invalid configuration in '{config_path}': {error['loc'][0]} {error['msg']}")
        raise SystemExit("Program terminated due to invalid configuration.")
    except FileNotFoundError:
        raise SystemExit(f"Configuration file '{config_path}' not found.")
    except PermissionError:
        raise SystemExit(f"Permission denied when trying to read '{config_path}'.")
