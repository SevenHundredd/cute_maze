from typing import Optional
try:
    from dotenv import dotenv_values
    from pydantic import BaseModel, Field, model_validator, ValidationError, field_validator, ConfigDict
except ImportError as e:
    raise SystemExit(f"Required module not found: {e.name}. Please install the required modules using 'make install'.")

class MazeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
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
        if isinstance(value, tuple) and len(value) == 2:
            return value
        elif isinstance(value, str):
            return tuple(map(int, value.split(',')))
        else: 
            raise ValueError("Coordinates must be a tuple of two integers or a string in the format 'x,y'.")

    
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
                print(f"Invalid value in '{config_path}': {error['msg'].split(', ')[1]}")
            else:
                print(f"Invalid configuration in '{config_path}': {error['loc'][0]} {error['msg']}")
        raise SystemExit("Program terminated due to invalid configuration.")
    except FileNotFoundError:
        raise SystemExit(f"Configuration file '{config_path}' not found.",)
    except PermissionError:
        raise SystemExit(f"Permission denied when trying to read '{config_path}'.")
