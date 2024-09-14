def chunk_parsed_code(codebase_dict, max_chunk_size=1000):
    chunks = []

    def process_item(item, path):
        if isinstance(item, str):
            content = item
            lines = content.split("\n")
            current_chunk = []
            current_size = 0
            for i, line in enumerate(lines, start=1):  # Start enumeration from 1
                if current_size + len(line) > max_chunk_size and current_chunk:
                    chunks.append(
                        {
                            "content": current_chunk,
                            "metadata": {
                                "file": path,
                                "start_line": current_chunk[0][0],
                                "end_line": current_chunk[-1][0],
                            },
                        }
                    )
                    current_chunk = []
                    current_size = 0
                current_chunk.append(
                    (i, line)
                )  # Store tuple of (line_number, line_content)
                current_size += len(line)
            if current_chunk:
                chunks.append(
                    {
                        "content": current_chunk,
                        "metadata": {
                            "file": path,
                            "start_line": current_chunk[0][0],
                            "end_line": current_chunk[-1][0],
                        },
                    }
                )
        elif isinstance(item, dict):
            for name, content in item.items():
                process_item(content, f"{path}/{name}" if path else name)

    process_item(codebase_dict, "")
    return chunks
