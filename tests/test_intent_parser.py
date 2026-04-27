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


def test_parse_voice_status() -> None:
    intent = IntentParser().parse("voice status")

    assert intent.name == "voice_status"


def test_parse_tts_speak_target() -> None:
    intent = IntentParser().parse("say hello atlas")

    assert intent.name == "text_to_speech"
    assert intent.args["target"] == "hello atlas"


def test_parse_transcribe_target() -> None:
    intent = IntentParser().parse("transcribe /tmp/audio.wav")

    assert intent.name == "speech_to_text"
    assert intent.args["target"] == "/tmp/audio.wav"


def test_unknown_intent() -> None:
    intent = IntentParser().parse("make the moon blue")

    assert intent.name == "unknown"
    assert intent.confidence == 0.0


def test_parse_todo_timer_and_dictionary_aliases() -> None:
    parser = IntentParser()

    assert parser.parse("todo buy milk").name == "todo_list"
    assert parser.parse("timer 12").args["minutes"] == 12
    assert parser.parse("define atlas").args["target"] == "atlas"


def test_parse_system_control_aliases() -> None:
    parser = IntentParser()

    assert parser.parse("notify hello").name == "notifications"
    assert parser.parse("take screenshot").name == "screenshot"
    assert parser.parse("lock screen").name == "lock_screen"
    assert parser.parse("service ssh status").args["target"] == "ssh"


def test_parse_web_integration_aliases() -> None:
    parser = IntentParser()

    assert parser.parse("news technology").name == "daily_news"
    assert parser.parse("youtube atlas assistant").name == "youtube_metadata"
    assert parser.parse("summarize https://example.com").args["target"] == "https://example.com"


def test_parse_productivity_coding_aliases() -> None:
    parser = IntentParser()

    assert parser.parse("zip /tmp/demo").name == "zip_files"
    assert parser.parse("git status").name == "git_status"
    assert parser.parse("validate json {}").name == "json_validator"
