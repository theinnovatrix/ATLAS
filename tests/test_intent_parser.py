from atlas.core.intent_parser import IntentParser


def test_parse_english_system_info() -> None:
    intent = IntentParser().parse("Atlas, show system info")

    assert intent.name == "system_info"
    assert intent.language == "en"
    assert intent.confidence > 0.5


def test_parse_hindi_urdu_weather() -> None:
    intent = IntentParser().parse("Delhi ka mausam batao")

    assert intent.name == "weather_info"
    assert intent.language == "hi"
    assert intent.args["target"] == "delhi"


def test_extract_volume_level() -> None:
    intent = IntentParser().parse("volume 72")

    assert intent.name == "volume_control"
    assert intent.args["level"] == 72


def test_extract_calculator_expression() -> None:
    intent = IntentParser().parse("calculate 2 + 3 * 4")

    assert intent.name == "calculator"
    assert intent.args["expression"] == "2 + 3 * 4"


def test_unknown_intent() -> None:
    intent = IntentParser().parse("make the moon blue")

    assert intent.name == "unknown"
    assert intent.confidence == 0.0
