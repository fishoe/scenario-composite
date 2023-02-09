from core import field as field_types
from core.chapter import SampleChapter
from core.scenario import Scenario

chapter = SampleChapter(
    prefix="/chapter",
    scenarios=[
        Scenario(
            fields=[
                field_types.BaseField(
                    name="num",
                    cls_type=int,
                    model_field="num",
                    use_in={"summary": field_types.UseInScenario.REQUIRED},
                ),
                field_types.BaseField(
                    name="value",
                    cls_type=str,
                    model_field="value",
                    use_in={"detail": field_types.UseInScenario.REQUIRED},
                ),
            ]
        )
    ]
)
