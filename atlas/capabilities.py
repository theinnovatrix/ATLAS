"""
Module: atlas.capabilities
Purpose: Registry of Atlas desktop assistant capabilities and risk levels.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: atlas.models
Last Updated: 2026-04-26
"""

from __future__ import annotations

from dataclasses import dataclass

from atlas.models import RiskLevel


@dataclass(frozen=True)
class Capability:
    """Describe a command Atlas can understand or roadmap."""

    name: str
    category: str
    summary: str
    risk: RiskLevel = RiskLevel.SAFE
    implemented: bool = False


CAPABILITIES: tuple[Capability, ...] = (
    Capability("capabilities", "help", "List Atlas capabilities.", implemented=True),
    Capability("system_info", "system", "Check PC details.", implemented=True),
    Capability("power_manager", "system", "Turn off or restart PC.", RiskLevel.CONFIRM),
    Capability("volume_control", "system", "Change sound levels.", RiskLevel.CONFIRM, True),
    Capability("brightness_control", "system", "Change screen brightness.", RiskLevel.CONFIRM, True),
    Capability("virus_scan", "system", "Check for viruses.", RiskLevel.CONFIRM),
    Capability("app_launcher", "system", "Open apps.", RiskLevel.CONFIRM, True),
    Capability("file_opener", "system", "Open files.", RiskLevel.CONFIRM, True),
    Capability("battery_saver", "system", "Save laptop battery.", RiskLevel.CONFIRM),
    Capability("pc_temp_check", "system", "Check PC temperature.", implemented=True),
    Capability("disk_cleaner", "system", "Clean junk files.", RiskLevel.CONFIRM),
    Capability("empty_trash", "system", "Empty trash.", RiskLevel.DANGEROUS),
    Capability("wifi_manager", "system", "Connect to WiFi.", RiskLevel.CONFIRM),
    Capability("network_speed", "system", "Check internet speed."),
    Capability("lock_screen", "system", "Lock screen.", RiskLevel.CONFIRM),
    Capability("screenshot", "system", "Take a screenshot.", RiskLevel.CONFIRM, True),
    Capability("screen_record", "system", "Record screen.", RiskLevel.CONFIRM),
    Capability("mic_control", "system", "Mute or unmute mic.", RiskLevel.CONFIRM),
    Capability("webcam_control", "system", "Turn webcam on or off.", RiskLevel.CONFIRM),
    Capability("mouse_speed", "system", "Change mouse speed.", RiskLevel.CONFIRM),
    Capability("keyboard_lights", "system", "Change keyboard colors.", RiskLevel.CONFIRM),
    Capability("time_sync", "system", "Sync PC time.", RiskLevel.CONFIRM),
    Capability("calendar_view", "productivity", "Show calendar.", implemented=True),
    Capability("notifications", "system", "Manage alerts.", RiskLevel.CONFIRM),
    Capability("night_mode", "system", "Turn on dark mode.", RiskLevel.CONFIRM),
    Capability("eye_care", "system", "Reduce blue light.", RiskLevel.CONFIRM),
    Capability("bluetooth_connect", "system", "Connect Bluetooth devices.", RiskLevel.CONFIRM),
    Capability("printer_setup", "system", "Connect to printer.", RiskLevel.CONFIRM),
    Capability("phone_link", "system", "Connect phone.", RiskLevel.CONFIRM),
    Capability("game_mode", "system", "Boost game speed.", RiskLevel.CONFIRM),
    Capability("task_manager", "system", "Close stuck apps.", RiskLevel.CONFIRM),
    Capability("auto_update", "system", "Update PC software.", RiskLevel.CONFIRM),
    Capability("window_move", "desktop", "Move windows.", RiskLevel.CONFIRM),
    Capability("auto_scroll", "desktop", "Scroll pages.", RiskLevel.CONFIRM),
    Capability("remote_control", "desktop", "Remote control PC.", RiskLevel.DANGEROUS),
    Capability("clipboard_history", "desktop", "Save copied text.", RiskLevel.CONFIRM),
    Capability("pin_to_top", "desktop", "Keep window on top.", RiskLevel.CONFIRM),
    Capability("quick_search", "desktop", "Find files fast.", implemented=True),
    Capability("folder_maker", "desktop", "Make folders.", RiskLevel.CONFIRM, True),
    Capability("quick_note", "desktop", "Take notes.", implemented=True),
    Capability("change_wallpaper", "desktop", "Set wallpaper.", RiskLevel.CONFIRM),
    Capability("clean_desktop", "desktop", "Hide desktop icons.", RiskLevel.CONFIRM),
    Capability("screen_ruler", "desktop", "Measure on screen."),
    Capability("color_picker", "desktop", "Pick colors from screen."),
    Capability("snipping_tool", "desktop", "Cut parts of screen.", RiskLevel.CONFIRM),
    Capability("snap_windows", "desktop", "Snap windows.", RiskLevel.CONFIRM),
    Capability("multi_monitor", "desktop", "Manage displays.", RiskLevel.CONFIRM),
    Capability("refresh_desktop", "desktop", "Refresh desktop.", RiskLevel.CONFIRM),
    Capability("delete_file", "desktop", "Delete files.", RiskLevel.DANGEROUS),
    Capability("copy_path", "desktop", "Copy file path.", RiskLevel.CONFIRM),
    Capability("zip_files", "desktop", "Compress files.", RiskLevel.CONFIRM),
    Capability("unzip_files", "desktop", "Extract zip files.", RiskLevel.CONFIRM),
    Capability("hide_files", "desktop", "Hide files.", RiskLevel.CONFIRM),
    Capability("show_hidden", "desktop", "Show hidden files.", RiskLevel.CONFIRM),
    Capability("rename_files", "desktop", "Rename files.", RiskLevel.CONFIRM),
    Capability("make_shortcut", "desktop", "Create shortcuts.", RiskLevel.CONFIRM),
    Capability("shred_file", "desktop", "Delete forever.", RiskLevel.DANGEROUS),
    Capability("folder_size", "desktop", "Check folder size.", implemented=True),
    Capability("sync_folders", "desktop", "Sync folders.", RiskLevel.CONFIRM),
    Capability("cloud_backup", "desktop", "Save to cloud.", RiskLevel.CONFIRM),
    Capability("downloads_folder", "desktop", "Open downloads.", RiskLevel.CONFIRM, True),
    Capability("go_home", "desktop", "Go to home folder.", RiskLevel.CONFIRM, True),
    Capability("log_out", "desktop", "Log out user.", RiskLevel.CONFIRM),
    Capability("any_language", "voice", "English, Hindi, and Urdu first; extensible.", implemented=True),
    Capability("whatsapp_bot", "productivity", "Send WhatsApp messages.", RiskLevel.CONFIRM),
    Capability("email_sender", "productivity", "Send emails.", RiskLevel.CONFIRM),
    Capability("auto_typing", "productivity", "Type text.", RiskLevel.CONFIRM),
    Capability("set_alarm", "productivity", "Set alarm.", implemented=True),
    Capability("stopwatch", "productivity", "Start stopwatch.", implemented=True),
    Capability("timer", "productivity", "Set timer.", implemented=True),
    Capability("add_event", "productivity", "Add calendar event.", RiskLevel.CONFIRM),
    Capability("todo_list", "productivity", "Manage tasks.", implemented=True),
    Capability("calculator", "productivity", "Do math.", implemented=True),
    Capability("currency_converter", "productivity", "Convert money."),
    Capability("unit_converter", "productivity", "Convert units.", implemented=True),
    Capability("translate_text", "productivity", "Translate text.", implemented=True),
    Capability("dictionary", "productivity", "Find meanings.", implemented=True),
    Capability("thesaurus", "productivity", "Find synonyms."),
    Capability("voice_status", "voice", "Check voice pipeline availability.", implemented=True),
    Capability("text_to_speech", "voice", "Read text aloud.", implemented=True),
    Capability("speech_to_text", "voice", "Type by talking.", implemented=True),
    Capability("pdf_reader", "productivity", "Read PDFs."),
    Capability("pdf_editor", "productivity", "Edit PDFs.", RiskLevel.CONFIRM),
    Capability("excel_helper", "productivity", "Help with Excel."),
    Capability("word_helper", "productivity", "Help with Word."),
    Capability("ppt_helper", "productivity", "Help with PowerPoint."),
    Capability("mind_map", "productivity", "Make mind maps."),
    Capability("pomodoro_timer", "productivity", "Focus timer.", implemented=True),
    Capability("relax_mode", "productivity", "Play calm sounds."),
    Capability("focus_music", "productivity", "Play focus music."),
    Capability("block_distractions", "productivity", "Block sites.", RiskLevel.CONFIRM),
    Capability("track_time", "productivity", "Track work time."),
    Capability("make_invoice", "productivity", "Create invoices."),
    Capability("sign_doc", "productivity", "Sign documents.", RiskLevel.CONFIRM),
    Capability("contacts", "productivity", "Manage contacts."),
    Capability("find_text", "productivity", "OCR text in images."),
    Capability("ai_coder", "developer", "Write code.", implemented=True),
    Capability("vscode_link", "developer", "Connect VS Code.", RiskLevel.CONFIRM),
    Capability("run_code", "developer", "Run code.", RiskLevel.CONFIRM, True),
    Capability("fix_bugs", "developer", "Find and fix bugs."),
    Capability("format_code", "developer", "Format code.", RiskLevel.CONFIRM),
    Capability("explain_code", "developer", "Explain code.", implemented=True),
    Capability("git_commit", "developer", "Git commit.", RiskLevel.CONFIRM),
    Capability("git_push", "developer", "Git push.", RiskLevel.CONFIRM),
    Capability("git_pull", "developer", "Git pull.", RiskLevel.CONFIRM),
    Capability("git_branch", "developer", "Git branch.", RiskLevel.CONFIRM),
    Capability("docker_helper", "developer", "Manage Docker.", RiskLevel.CONFIRM),
    Capability("db_helper", "developer", "Manage databases.", RiskLevel.CONFIRM),
    Capability("api_tester", "developer", "Test APIs.", implemented=True),
    Capability("mobile_view", "developer", "Test mobile view."),
    Capability("css_helper", "developer", "Help with CSS."),
    Capability("react_helper", "developer", "Help with React."),
    Capability("python_helper", "developer", "Help with Python.", implemented=True),
    Capability("java_helper", "developer", "Help with Java."),
    Capability("js_helper", "developer", "Help with JavaScript."),
    Capability("php_helper", "developer", "Help with PHP."),
    Capability("ruby_helper", "developer", "Help with Ruby."),
    Capability("rust_helper", "developer", "Help with Rust."),
    Capability("go_helper", "developer", "Help with Go."),
    Capability("write_tests", "developer", "Write tests.", implemented=True),
    Capability("check_speed", "developer", "Check code speed."),
    Capability("check_security", "developer", "Check code security."),
    Capability("read_docs", "developer", "Read docs.", implemented=True),
    Capability("write_docs", "developer", "Write docs.", implemented=True),
    Capability("deploy_app", "developer", "Deploy app.", RiskLevel.CONFIRM),
    Capability("aws_helper", "developer", "Help with AWS.", RiskLevel.CONFIRM),
    Capability("linux_commands", "developer", "Run Linux commands.", RiskLevel.CONFIRM, True),
    Capability("web_search", "web", "Search web.", implemented=True),
    Capability("weather_info", "web", "Check weather.", implemented=True),
    Capability("daily_news", "web", "Read news."),
    Capability("play_music", "media", "Play music.", RiskLevel.CONFIRM),
    Capability("play_video", "media", "Play YouTube videos.", RiskLevel.CONFIRM),
    Capability("find_images", "web", "Search images."),
    Capability("movie_info", "web", "Find movie details."),
    Capability("book_info", "web", "Find book details."),
    Capability("flight_info", "web", "Check flight status."),
    Capability("hotel_search", "web", "Find hotels."),
    Capability("maps_routes", "web", "Find directions."),
    Capability("food_delivery", "web", "Order food.", RiskLevel.CONFIRM),
    Capability("shop_online", "web", "Search products."),
    Capability("track_package", "web", "Track packages."),
    Capability("stock_prices", "web", "Check stocks."),
    Capability("crypto_prices", "web", "Check crypto."),
    Capability("sports_scores", "web", "Check scores."),
    Capability("game_info", "web", "Find game details."),
    Capability("tell_joke", "media", "Tell a joke.", implemented=True),
    Capability("daily_quote", "media", "Daily quote.", implemented=True),
    Capability("meditation", "media", "Guided meditation.", implemented=True),
    Capability("workout_plan", "media", "Workout plan.", implemented=True),
    Capability("diet_plan", "media", "Diet plan.", implemented=True),
    Capability("recipes", "media", "Find recipes.", implemented=True),
    Capability("wine_pairing", "media", "Find wine pairing.", implemented=True),
    Capability("pet_care", "media", "Pet care tips.", implemented=True),
    Capability("plant_care", "media", "Plant care tips.", implemented=True),
    Capability("car_info", "web", "Find car details.", implemented=True),
    Capability("home_decor", "media", "Home decor ideas.", implemented=True),
    Capability("fashion_tips", "media", "Fashion advice.", implemented=True),
    Capability("makeup_tips", "media", "Makeup advice.", implemented=True),
)


def capability_by_name(name: str) -> Capability | None:
    """Return a capability by internal name."""
    return next((capability for capability in CAPABILITIES if capability.name == name), None)


def implemented_capabilities() -> list[Capability]:
    """Return capabilities with a working first implementation."""
    return [capability for capability in CAPABILITIES if capability.implemented]


def capability_summary() -> dict[str, int]:
    """Return registry counts for status reporting."""
    return {
        "total": len(CAPABILITIES),
        "implemented": len(implemented_capabilities()),
        "confirm": sum(1 for capability in CAPABILITIES if capability.risk is RiskLevel.CONFIRM),
        "dangerous": sum(1 for capability in CAPABILITIES if capability.risk is RiskLevel.DANGEROUS),
    }
