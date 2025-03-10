import json
def generate_codebase_summary(parsed_data: dict) -> str:
    summary = []
    summary.append("📚 Codebase Overview\n")

    for file_path, file_info in parsed_data["parsed_code"].items():
        summary.append(f"\n File: {file_path}")
        fc_list = file_info.get("functions_classes", [])

        if not fc_list:
            summary.append("  -  No functions/classes/scripts found.")
            continue

        for fc in fc_list:
            fc_type = fc.get("type", "unknown")
            name = fc.get("name", "unknown")

            if fc_type == "Script" and name == file_path:
                name = "Script Block (top-level code)"

            start = fc.get("start_line", "-")
            end = fc.get("end_line", "-")
            summary.append(f"  - [{fc_type}] {name} ({start}-{end})")

    summary_text = "\n".join(summary)
    return summary_text

with open("parsed_code.json", "r") as file:
    parsed_data = json.load(file)
summary = generate_codebase_summary(parsed_data)
print(summary)