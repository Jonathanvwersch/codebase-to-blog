def chunk_parsed_code(codebase_dict, max_chunk_size=1000):
    chunks = []

    def process_item(item, path):
        if isinstance(item, str):
            content = item
            lines = content.split("\n")
            current_chunk = []
            current_size = 0
            for i, line in enumerate(lines):
                if current_size + len(line) > max_chunk_size and current_chunk:
                    chunks.append(
                        {
                            "content": "\n".join(current_chunk),
                            "metadata": {
                                "file": path,
                                "start_line": i - len(current_chunk) + 1,
                                "end_line": i,
                            },
                        }
                    )
                    current_chunk = []
                    current_size = 0
                current_chunk.append(line)
                current_size += len(line)
            if current_chunk:
                chunks.append(
                    {
                        "content": "\n".join(current_chunk),
                        "metadata": {
                            "file": path,
                            "start_line": len(lines) - len(current_chunk) + 1,
                            "end_line": len(lines),
                        },
                    }
                )
        elif isinstance(item, dict):
            for name, content in item.items():
                process_item(content, f"{path}/{name}" if path else name)

    process_item(codebase_dict, "")
    return chunks
